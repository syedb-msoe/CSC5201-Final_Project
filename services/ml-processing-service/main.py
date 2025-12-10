from fastapi import FastAPI
from eventhub_consumer import start_event_consumer
import threading

app = FastAPI(title="ML Processing Service")

@app.on_event("startup")
async def startup_event():
    print("Starting EventHub consumer in background thread...")
    thread = threading.Thread(target=start_event_consumer, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}