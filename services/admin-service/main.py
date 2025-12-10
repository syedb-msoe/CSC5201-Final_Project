from fastapi import FastAPI
from metrics_store import metrics, record
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)
app = FastAPI(title="Admin Service")

@app.get("/admin/usage")
def get_usage():
    return metrics

@app.get("/health")
def health():
    return {"status": "ok"}