from fastapi import FastAPI
from eventhub_consumer import start_event_consumer

app = FastAPI(title="ML Processing Service")

@app.on_event("startup")
async def startup_event():
    print("Starting EventHub consumer...")
    start_event_consumer()

@app.get("/health")
def health():
    return {"status": "ok"}