from fastapi import FastAPI
from eventhub_consumer import start_event_consumer
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("uamqp").setLevel(logging.WARNING)
logging.getLogger("azure.eventhub").setLevel(logging.WARNING)
app = FastAPI(title="ML Processing Service")

@app.on_event("startup")
async def startup_event():
    print("Starting EventHub consumer in background thread...")
    thread = threading.Thread(target=start_event_consumer, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}