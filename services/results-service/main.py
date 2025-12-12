import os
from fastapi import FastAPI, HTTPException, Depends
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from auth_middleware import get_current_user
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Results Service")

COSMOS_ENDPOINT = os.getenv("COSMOS_CONN")
COSMOS_KEY = os.getenv("COSMOS_KEY")
BLOB_CONN = os.getenv("BLOB_CONN_STRING")

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
cosmos = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

db = cosmos.get_database_client("appdb")
docs = db.get_container_client("documents")

processed_container = blob_service.get_container_client("processed")

@app.get("/results")
def get_results(user = Depends(get_current_user)):
    """
    Return all documents belonging to the authenticated user.
    Also fetch processed text output from Blob Storage.
    """

    user_id = user["id"]

    # Use a parameterized query (safer & recommended)
    query = """
        SELECT * FROM c WHERE c.userId = @uid
    """

    items = list(
        docs.query_items(
            query=query,
            parameters=[{"name": "@uid", "value": user_id}],
            enable_cross_partition_query=True
        )
    )

    results = []

    for doc in items:
        translated_blob_path = doc.get("translatedBlobPath")

        if not translated_blob_path:
            continue

        processed_text = None

        try:
            blob_client = processed_container.get_blob_client(translated_blob_path)
        except Exception as e:
            logging.warning(
                f"Processed blob missing for {translated_blob_path}: {str(e)}"
            )

        results.append({
            "documentId": doc["id"],
            "blobPath": translated_blob_path,
            "uploadedAt": doc.get("uploadedAt"),
            "language": doc.get("language", "unknown"),
            "public_url": blob_client.url
        })

    return {
        "userId": user_id,
        "count": len(results),
        "documents": results
    }