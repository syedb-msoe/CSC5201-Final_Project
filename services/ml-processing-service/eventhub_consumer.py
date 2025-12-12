import os, json, logging, requests, uuid
from azure.eventhub import EventHubConsumerClient
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
EVENTHUB_CONN = os.getenv("EVENTHUB_CONN")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
EVENTHUB_CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "$Default")
BLOB_CONN = os.getenv("BLOB_CONN_STRING")
FORM_KEY = os.getenv("FORM_RECOGNIZER_KEY")
FORM_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
TRANSLATOR_KEY = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT")
COSMOS_ENDPOINT = os.getenv("COSMOS_CONN")
COSMOS_KEY = os.getenv("COSMOS_KEY")

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
form_client = DocumentAnalysisClient(FORM_ENDPOINT, AzureKeyCredential(FORM_KEY))
cosmos = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
db = cosmos.get_database_client("appdb")
docs = db.get_container_client("documents")

def translate_text(text: str, to_language="es"):
    """
    Translate text to the target language using Azure Translator.
    (Default: Spanish "es")
    """

    path = "/translate?api-version=3.0&to=" + to_language
    url = TRANSLATOR_ENDPOINT + path

    logging.info("Calling translation API at %s", url)

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Region": "centralus"
    }

    body = [{"text": text}]

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        logging.error("Translation failed: %s", response.text)
        return text

    result = response.json()
    return result[0]["translations"][0]["text"]

def translate_large_text(text, to_language="es"):
    chunks = chunk_text(text)
    translated_chunks = []

    for i, chunk in enumerate(chunks):
        logger.info(f"Translating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")

        translated = translate_text(chunk, to_language)
        translated_chunks.append(translated)
    
    return "\n".join(translated_chunks)


def on_event(partition_context, event):
    logger.info("Received event from partition %s", partition_context.partition_id)
    payload = json.loads(event.body_as_str())
    logger.info("Event payload: %s", payload)
    container = payload["container"]
    blob_path = payload["blob_path"]

    # Download PDF
    try:
    logger.info("Downloading blob '%s' from container '%s'", blob_path, container)
    blob = blob_service.get_blob_client(container, blob_path)

    if not blob.exists():
        logger.error(f"Blob '{blob_path}' does not exist in '{container}'. Skipping event.")
        partition_context.update_checkpoint(event)
        return
    pdf_bytes = blob.download_blob().readall()

    # Extract text
    logger.info("Extracting text from PDF blob")
    poller = form_client.begin_analyze_document("prebuilt-read", pdf_bytes)
    result = poller.result()

    text = "\n".join([line.content for page in result.pages for line in page.lines])

    # Determine target languages (list). If none provided, default to English ('en')
    lang = payload.get("language") or ["en"]
    out_container = blob_service.get_container_client("processed")

    base, _ = os.path.splitext(blob_path)
    try:
        logger.info("Translating extracted text to '%s'", lang)
        translated_text = translate_large_text(text, to_language=lang)

        # Store output per language, e.g., folder/filename.en.txt
        text_blob_path = f"{base}.{lang}.txt"
        out_blob = out_container.get_blob_client(text_blob_path)
        out_blob.upload_blob(translated_text, overwrite=True)
        logger.info("Uploaded extracted text to '%s/%s'", "processed", text_blob_path)

        # Record in Cosmos DB
        docs.create_item({
            "id": str(uuid.uuid4()),
            "userId": payload["userId"],
            "uploadedAt": str(datetime.now()),
            "language": lang,
            "originalBlobPath": blob_path,
            "translatedBlobPath": text_blob_path,
            "status": "processed"
        })
    except Exception:
        logger.exception("Failed to translate or upload for language %s", lang)
    partition_context.update_checkpoint(event)


def start_event_consumer():
    """Start a blocking Event Hub consumer that processes incoming upload events.

    Environment variables required: `EVENTHUB_CONN`, `EVENTHUB_NAME`.
    Optional: `CONSUMER_GROUP` (defaults to `$Default`).
    """

    logger.info("Initializing Event Hub consumer client")

    client = EventHubConsumerClient.from_connection_string(
        EVENTHUB_CONN, consumer_group=EVENTHUB_CONSUMER_GROUP, eventhub_name=EVENTHUB_NAME
    )

    logger.info("Starting Event Hub consumer for hub '%s', group '%s'", EVENTHUB_NAME, EVENTHUB_CONSUMER_GROUP)

    try:
        with client:
            client.receive(on_event=on_event,starting_position="-1")
    except KeyboardInterrupt:
        logger.info("Event consumer stopped by user")
    except Exception:
        logger.error("Event consumer stopped with exception")

def chunk_text(text, max_size=4500):
    chunks = []
    while len(text) > max_size:
        # break at nearest sentence end for better quality
        split_pos = text.rfind('.', 0, max_size)
        if split_pos == -1:
            split_pos = max_size
        chunks.append(text[:split_pos+1])
        text = text[split_pos+1:]
    if text:
        chunks.append(text)
    return chunks
