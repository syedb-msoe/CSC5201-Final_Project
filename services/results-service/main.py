from fastapi import FastAPI, HTTPException
from cosmos_client import get_result

app = FastAPI(title="Results Service")

@app.get("/results/{documentId}")
def get_results(documentId: str):
    result = get_result(documentId)
    if not result:
        raise HTTPException(404, "Not found")
    return result

@app.get("/health")
def health():
    return {"status": "ok"}