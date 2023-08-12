import sys
import os
import logging

import numpy
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
    def __init__(self, *args, **kwargs):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.collection_name = kwargs['collection_name']
        self.embedding_model = kwargs['encoder_model']
        self.ranking_model = kwargs['ranking_model']
        self.language = kwargs['language']
        self.vectors = kwargs['vectors']
        self.data = kwargs['data']
        self.indices = kwargs['indices']

    def retrieve(self, query: str, filter_: dict = None) -> list[dict]:
        """
        This function is responsible for processing the query, retrieving and ranking
        the results of the retrieval.
        :param query:
        :param filter_:
        :return:
        """
        raise NotImplementedError

    def rank(self, hits):
        """
        For now, this returns the same order as the hits.
        :param hits: List of computed nearest vectors.
        :return:
        """
        raise NotImplementedError

    def filter(self, hits):
        """
        Responsible for filtering invalid hits amongst all hits found with ANN or knowledge graph.
        :param hits:
        :return:
        """
        raise NotImplementedError

    def process_query(self, query):
        """
        For now, this returns the direct encoding of the model. This pre-processing step
        for queries may consider standardization, tokenization and spell check.
        :param query:
        :return:
        """
        raise NotImplementedError


class LocalSearcher(Searcher):
    """
    TODO: documentation
    Retrieve + Rank
    """
    def __init__(self, *args, **kwargs):
        super(LocalSearcher, self).__init__(*args, **kwargs)

    @log
    def retrieve(self, query: str, hits_cnt: int = 30, filter_: dict = None) -> list[dict]:
        """
        This function is responsible for processing the query, retrieving and ranking
        the results of the retrieval.
        :param query:
        :param filter_:
        :return:
        """
        vector: numpy.ndarray = self.process_query(query)
        [scores] = cosine_similarity(vector.reshape(1, -1), self.vectors)
        hits = np.argsort(scores)[::-1][:hits_cnt]
        return [self.data.iloc[self.indices[i]].to_dict() for i in hits]

    @log
    def process_query(self, query):
        """
        For now, this returns the direct encoding of the model. This pre-processing step
        for queries may consider standardization, tokenization and spell check.
        :param query:
        :return:
        """
        vector: numpy.ndarray = self.embedding_model.encode(query)
        return vector

    @log
    def rank(self, hits):
        """
        For now, this returns the same order as the hits.
        :param hits: List of computed nearest vectors.
        :return:
        """
        return hits

    @log
    def filter(self, hits):
        """
        Responsible for filtering invalid hits amongst all hits found with ANN or knowledge graph.
        :param hits:
        :return:
        """
        pass


class QdrantSearcher(Searcher):
    """
    TODO: documentation
    Retrieve + Rank
    """
    def __init__(self, *args, **kwargs):
        super(QdrantSearcher, self).__init__(args, kwargs)
        self.client = kwargs['qdrant_client']

    @log
    def retrieve(self, query: str, filter_: dict = None) -> List[dict]:
        """
        This function is responsible for processing the query, retrieving and ranking
        the results of the retrieval.
        :param query:
        :param filter_:
        :return:
        """
        vector = self.process_query(query)
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            top=30
        )
        hits = self.rank(hits)
        return [hit.payload for hit in hits]

    @log
    def process_query(self, query):
        """
        For now, this returns the direct encoding of the model. This pre-processing step
        for queries may consider standardization, tokenization and spell check.
        :param query:
        :return:
        """
        vector: list = self.embedding_model.encode(query).tolist()
        return vector

    @log
    def rank(self, hits):
        """
        For now, this returns the same order as the hits.
        :param hits: List of computed nearest vectors.
        :return:
        """
        return hits

    @log
    def filter(self, hits):
        """
        Responsible for filtering invalid hits amongst all hits found with ANN or knowledge graph.
        :param hits:
        :return:
        """
        pass

