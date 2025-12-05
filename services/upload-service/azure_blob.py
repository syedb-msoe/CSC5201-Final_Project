import os
from fastapi import UploadFile
from azure.storage.blob import BlobServiceClient

# Read connection settings from env vars
_BLOB_CONN_STRING = os.getenv("BLOB_CONN_STRING")
_BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "uploads")


def _get_blob_service_client():
    if not _BLOB_CONN_STRING:
        raise RuntimeError("BLOB_CONN_STRING environment variable is not set")
    return BlobServiceClient.from_connection_string(_BLOB_CONN_STRING)


def upload_to_blob(doc_id: str, file: UploadFile) -> str:
    """Upload a FastAPI `UploadFile` to Azure Blob Storage and return the blob URL.

    Expects `BLOB_CONN_STRING` in environment. Optional `BLOB_CONTAINER` (defaults to 'uploads').
    """
    service = _get_blob_service_client()
    container_client = service.get_container_client(_BLOB_CONTAINER)

    # Ensure container exists (ignore error if it already exists)
    try:
        container_client.create_container()
    except Exception:
        pass

    blob_name = f"{doc_id}/{file.filename}"
    blob_client = container_client.get_blob_client(blob_name)

    # Make sure we're at start of the file and stream upload
    file.file.seek(0)
    blob_client.upload_blob(file.file, overwrite=True)

    # Return the HTTP URL to the blob
    return blob_client.url