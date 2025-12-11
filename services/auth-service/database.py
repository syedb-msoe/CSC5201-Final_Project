import os
from azure.cosmos import CosmosClient
from uuid import uuid4

COSMOS_URL = os.getenv("COSMOS_CONN")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = "appdb"
COSMOS_CONTAINER = "users"

client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db = client.get_database_client(COSMOS_DB)
users = db.get_container_client(COSMOS_CONTAINER)


def create_user(email: str, hashed_pass: str):
    user_doc = {
        "id": str(uuid4()),
        "email": email.lower(),
        "hashed_password": hashed_pass,
    }
    users.create_item(user_doc)
    return user_doc


def find_user_by_email(email: str):
    query = "SELECT * FROM c WHERE c.email=@e"
    results = list(users.query_items(
        query=query,
        parameters=[{"name": "@e", "value": email.lower()}],
        enable_cross_partition_query=True
    ))
    return results[0] if results else None