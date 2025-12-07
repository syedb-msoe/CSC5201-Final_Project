import os
import json
import logging
from azure.eventhub import EventHubConsumerClient
from azure.storage.blob import BlobServiceClient
from form_recognizer import extract_text
from cosmos_client import save_result

_CONN_STR = os.getenv("EVENTHUB_CONN")
_HUB_NAME = os.getenv("EVENTHUB_NAME")
_CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "$Default")


def _on_event(partition_context, event):
    try:
        body = event.body_as_str(encoding="UTF-8")
    except Exception:
        # fallback: try bytes -> decode
        try:
            body = b"".join(b for b in event.body).decode("utf-8")
        except Exception:
            logging.exception("Failed to decode event body")
            return

    try:
        payload = json.loads(body)
    except Exception:
        logging.exception("Event body is not valid JSON: %s", body)
        return

    logging.info("Processing event from partition %s: %s", partition_context.partition_id, payload)

    doc_id = payload.get("documentId")
    blob_url = payload.get("blobUrl")

    if not doc_id or not blob_url:
        logging.warning("Event missing required fields: %s", payload)
        return

    try:
        extracted = extract_text(blob_url)
        save_result(doc_id, extracted)
    except Exception:
        logging.exception("Failed processing document %s", doc_id)
        return

    # checkpoint after successful processing
    try:
        partition_context.update_checkpoint(event)
    except Exception:
        logging.exception("Failed to update checkpoint for partition %s", partition_context.partition_id)


def start_event_consumer():
    """Start a blocking Event Hub consumer that processes incoming upload events.

    Environment variables required: `EVENTHUB_CONN`, `EVENTHUB_NAME`.
    Optional: `CONSUMER_GROUP` (defaults to `$Default`).
    """

    client = EventHubConsumerClient.from_connection_string(
        _CONN_STR, consumer_group=_CONSUMER_GROUP, eventhub_name=_HUB_NAME
    )

    logging.info("Starting Event Hub consumer for hub '%s', group '%s'", _HUB_NAME, _CONSUMER_GROUP)

    try:
        with client:
            client.receive(on_event=_on_event)
    except KeyboardInterrupt:
        logging.info("Event consumer stopped by user")
    except Exception:
        logging.exception("Event consumer stopped with exception")