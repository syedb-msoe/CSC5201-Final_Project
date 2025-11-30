from fastapi import FastAPI, UploadFile, File
from azure_blob import upload_to_blob
from eventhub_producer import send_event
from models import UploadResponse
import uuid

app = FastAPI(title="Upload Service")

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())

    # Upload to Blob (stubbed locally)
    blob_url = upload_to_blob(doc_id, file)

    # Send event to EventHub (stubbed locally)
    send_event({
        "documentId": doc_id,
        "blobUrl": blob_url
    })

    return UploadResponse(documentId=doc_id, blobUrl=blob_url)

@app.get("/health")
def health():
    return {"status": "ok"}