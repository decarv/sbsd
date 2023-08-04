import sys
import os
import logging
import numpy as np
import pandas as pd
import torch
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATA_DIR
from utils import log


class Searcher:
    """
    TODO: documentation
    Retrieve -> Rank
    """
    def __init__(self, collection_name: str, model_name: str, vector_database_client:
    QdrantClient, model: SentenceTransformer):
        self.collection_name = collection_name
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = model
        self.vector_database_client = vector_database_client

    @log(logging.DEBUG)
    def search(self, query: str, filter_: dict = None) -> List[dict]:
        """
        TODO: documentation
        Retrieve and Rank
        """
        vector = self.process_query(query)
        hits = self.vector_database_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            top=30
        )
        hits = self.rank(hits)
        return [hit.payload for hit in hits]

    @log(logging.DEBUG)
    def process_query(self, query):
        """
        For now, this returns the direct encoding of the model. This pre-processing step
        for queries may consider standardization, tokenization and spell check.
        :param query:
        :return:
        """
        vector: list = self.model.encode(query).tolist()
        return vector

    @log(logging.DEBUG)
    def rank(self, hits):
        """
        For now, this returns the same order as the hits.
        :param hits: List of computed nearest vectors.
        :return:
        """
        return hits