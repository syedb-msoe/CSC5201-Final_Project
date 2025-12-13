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
def get_stats():
    url = f"https://api.applicationinsights.io/v1/apps/{APP_ID}/query"

    query = """
    requests
    | summarize
        count = count(),
        avg_response_ms = avg(duration)
      by name
    | order by count desc
    """

    headers = {
        "x-api-key": API_KEY
    }

    r = requests.get(url, params={"query": query}, headers=headers)
    r.raise_for_status()

    table = r.json()["tables"][0]
    rows = table["rows"]

    endpoints = []
    for name, count, avg_ms in rows:
        # name looks like: "GET /health"
        parts = name.split(" ", 1)
        method = parts[0] if len(parts) > 1 else "UNKNOWN"
        endpoint = parts[1] if len(parts) > 1 else name

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