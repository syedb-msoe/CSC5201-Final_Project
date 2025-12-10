import os, json
from azure.eventhub import EventHubConsumerClient
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

EVENTHUB_CONN = os.getenv("EVENTHUB_CONN")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
EVENTHUB_CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "$Default")
BLOB_CONN = os.getenv("BLOB_CONN_STRING")
FORM_KEY = os.getenv("FORM_RECOGNIZER_KEY")
FORM_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
form_client = DocumentAnalysisClient(FORM_ENDPOINT, AzureKeyCredential(FORM_KEY))


def on_event(partition_context, event):
    logging.info("Received event from partition %s", partition_context.partition_id)
    payload = json.loads(event.body_as_str())
    logging.info("Event payload: %s", payload)
    container = payload["container"]
    blob_path = payload["blob_path"]

    # Download PDF
    logging.info("Downloading blob '%s' from container '%s'", blob_path, container)
    blob = blob_service.get_blob_client(container, blob_path)
    pdf_bytes = blob.download_blob().readall()

    # Extract text
    logging.info("Extracting text from PDF blob")
    poller = form_client.begin_analyze_document("prebuilt-read", pdf_bytes)
    result = poller.result()

    text = "\n".join([line.content for page in result.pages for line in page.lines])

    # Store output
    logging.info("Uploading extracted text to 'processed' container")
    out_container = blob_service.get_container_client("processed")
    out_blob = out_container.get_blob_client(blob_path + ".txt")
    out_blob.upload_blob(text, overwrite=True)

    partition_context.update_checkpoint(event)


def start_event_consumer():
    """Start a blocking Event Hub consumer that processes incoming upload events.

    Environment variables required: `EVENTHUB_CONN`, `EVENTHUB_NAME`.
    Optional: `CONSUMER_GROUP` (defaults to `$Default`).
    """

    client = EventHubConsumerClient.from_connection_string(
        EVENTHUB_CONN, consumer_group=EVENTHUB_CONSUMER_GROUP, eventhub_name=EVENTHUB_NAME
    )

    logging.info("Starting Event Hub consumer for hub '%s', group '%s'", _HUB_NAME, EVENTHUB_CONSUMER_GROUP)

    try:
        with client:
            client.receive(on_event=on_event)
    except KeyboardInterrupt:
        logging.info("Event consumer stopped by user")
    except Exception:
        logging.exception("Event consumer stopped with exception")