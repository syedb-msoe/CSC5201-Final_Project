from fastapi import FastAPI, UploadFile, File
from azure_blob import upload_to_blob
from eventhub_producer import send_event
from models import UploadResponse
import uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("uamqp").setLevel(logging.WARNING)
logging.getLogger("azure.eventhub").setLevel(logging.WARNING)

app = FastAPI(title="Upload Service")

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())

    blob_url = upload_to_blob(doc_id, file)

    send_event({
    "container": "uploads",
    "blob_path": f"{doc_id}/{file}"
    })

    return UploadResponse(documentId=doc_id, blobUrl=blob_url)

@app.get("/health")
def health():
    return {"status": "ok"}