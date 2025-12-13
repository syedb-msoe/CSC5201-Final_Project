from fastapi import FastAPI
from metrics_store import metrics, record
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)

configure_azure_monitor()
app = FastAPI(title="Admin Service")

@app.get("/admin/usage")
def get_usage():
    return metrics

@app.get("/health")
def health():
    return {"status": "ok"}