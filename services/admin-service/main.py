from fastapi import FastAPI
from metrics_store import metrics, record
import logging
from azure.monitor.opentelemetry import configure_azure_monitor
import requests
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)

configure_azure_monitor()
app = FastAPI(title="Admin Service")

APP_ID = os.getenv("APPINSIGHTS_APP_ID")
API_KEY = os.getenv("APPINSIGHTS_API_KEY")

@app.get("/admin/stats")
def get_stats():
    url = f"https://api.applicationinsights.io/v1/apps/{APP_ID}/query"

    query = """
    requests
    | summarize count=count(), avg_response_ms=avg(duration)
      by name, method
    """

    headers = {
        "x-api-key": API_KEY
    }

    r = requests.get(url, params={"query": query}, headers=headers)
    r.raise_for_status()

    data = r.json()["tables"][0]["rows"]

    endpoints = []
    for name, method, count, avg_ms in data:
        endpoint = name.split(" ", 1)[1]
        endpoints.append({
            "endpoint": endpoint,
            "method": method,
            "count": int(count),
            "avg_response_ms": round(avg_ms, 2)
        })

    return {"endpoints": endpoints}

@app.get("/health")
def health():
    return {"status": "ok"}