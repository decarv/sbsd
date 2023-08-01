# from torch import cuda
import os
import logging
import numpy as np
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATA_DIR
from utils import log


class SearchClient:
    def __init__(self, collection_name: str, model: str, host: str, port: str):
        self.collection_name = collection_name
        device = 'cuda'  # TODO: if cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model, device=device)
        self.client = QdrantClient(host, port)
        self.vectors = np.load(os.path.join(DATA_DIR, "vectors.npy"))

    @log(logging.DEBUG)
    def search(self, query: str, filter_: dict = None) -> List[dict]:
        vector = self.model.encode(query).tolist()
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            top=30
        )
        return [hit.payload for hit in hits]

    def local_search(self, query):
        if self.vectors is not None:
            query_vector = self.model.encode(query)
            [scores] = cosine_similarity(query_vector.reshape(1, -1), self.vectors)
            top_scores_ids = np.argsort(scores)
            top_scores_ids = top_scores_ids[::-1][:30]
