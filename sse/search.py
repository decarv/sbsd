# from torch import cuda
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from sentence_transformers import SentenceTransformer


class SearchClient:
    """"""
    def __init__(self, collection_name: str, model: str, host: str, port: str):
        self.collection_name = collection_name

        device = 'cuda' # if cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model, device=device)

        self.client = QdrantClient(host, port)

    def search(self, query: str, filter_: dict = None) -> List[dict]:
        print("Querying", query)
        vector = self.model.encode(query).tolist()
        print("Encoding", vector)
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            top=5
        )
        return [hit.payload for hit in hits]