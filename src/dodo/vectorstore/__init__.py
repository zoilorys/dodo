import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

VECTORSTORE_CONNECTION_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
DOCUMENT_COLLECTION_NAME = "documents"
DOCUMENT_PAYLOAD_KEY = "document_id"
# VECTOR_LEN = 3584 # gemma2
# VECTOR_LEN = 3072 # phi3.5
VECTOR_LEN = 768

vectorstore = QdrantClient(url=VECTORSTORE_CONNECTION_URL)

if not vectorstore.collection_exists(DOCUMENT_COLLECTION_NAME):
    vectorstore.create_collection(
        collection_name=DOCUMENT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_LEN,
            distance=Distance.DOT
        )
    )

