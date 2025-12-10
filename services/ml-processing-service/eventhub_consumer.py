import os, json, logging
import requests
from azure.eventhub import EventHubConsumerClient
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

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

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
form_client = DocumentAnalysisClient(FORM_ENDPOINT, AzureKeyCredential(FORM_KEY))

def translate_text(text: str, to_language="es"):
    """
    Translate text to the target language using Azure Translator.
    (Default: Spanish "es")
    """

    path = "/translate?api-version=3.0&to=" + to_language
    url = TRANSLATOR_ENDPOINT + path

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Region": "global"
    }

    body = [{"text": text}]

    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code != 200:
        logging.error("Translation failed: %s", response.text)
        return text

    result = response.json()
    return result[0]["translations"][0]["text"]

def on_event(partition_context, event):
    logger.info("Received event from partition %s", partition_context.partition_id)
    payload = json.loads(event.body_as_str())
    logger.info("Event payload: %s", payload)
    container = payload["container"]
    blob_path = payload["blob_path"]

    # Download PDF
    logger.info("Downloading blob '%s' from container '%s'", blob_path, container)
    blob = blob_service.get_blob_client(container, blob_path)
    pdf_bytes = blob.download_blob().readall()

    # Extract text
    logger.info("Extracting text from PDF blob")
    poller = form_client.begin_analyze_document("prebuilt-read", pdf_bytes)
    result = poller.result()

    text = "\n".join([line.content for page in result.pages for line in page.lines])

    # Determine target languages (list). If none provided, default to English ('en')
    languages = payload.get("languages") or ["en"]
    out_container = blob_service.get_container_client("processed")

    base, _ = os.path.splitext(blob_path)
    for lang in languages:
        try:
            logger.info("Translating extracted text to '%s'", lang)
            translated_text = translate_text(text, to_language=lang)

            # Store output per language, e.g., folder/filename.en.txt
            text_blob_path = f"{base}.{lang}.txt"
            out_blob = out_container.get_blob_client(text_blob_path)
            out_blob.upload_blob(translated_text, overwrite=True)
            logger.info("Uploaded extracted text to '%s/%s'", "processed", text_blob_path)
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
            client.receive(on_event=on_event)
    except KeyboardInterrupt:
        logger.info("Event consumer stopped by user")
    except Exception:
        logger.error("Event consumer stopped with exception")