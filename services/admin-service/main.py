from fastapi import FastAPI
from metrics_store import metrics, record

app = FastAPI(title="Admin Service")

@app.get("/admin/usage")
def get_usage():
    return metrics

@app.get("/health")
def health():
    return {"status": "ok"}