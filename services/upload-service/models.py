from pydantic import BaseModel

class UploadResponse(BaseModel):
    documentId: str
    blobUrl: str