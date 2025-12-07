import os
import json
import logging
from azure.eventhub import EventHubProducerClient, EventData

_CONN_STR = os.getenv("EVENTHUB_CONN")
_HUB_NAME = os.getenv("EVENTHUB_NAME")


def send_event(event: dict):
    """Send `event` (a JSON-serializable dict) to Azure Event Hubs.

    If `EVENTHUB_CONN` or `EVENTHUB_NAME` are not set, this function logs and returns.
    """
    try:
        producer = EventHubProducerClient.from_connection_string(_CONN_STR, eventhub_name=_HUB_NAME)
        event_data = EventData(json.dumps(event))
        with producer:
            batch = producer.create_batch()
            batch.add(event_data)
            producer.send_batch(batch)
        logging.debug("Sent event to Event Hub '%s'", _HUB_NAME)
    except Exception:
        logging.exception("Failed to send event to Event Hub")