import pandas as pd
import numpy as np
import os

import sqlite3
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

from models.metadata import Metadata

from config import DATA_DIR


class Indexer:
    """
    Indexed documents -> document encoder -> indexed documents (embedding) -> embedding
    quantization -> index publish
    """

    def __init__(
            self, collection_name: str, host: str, port: str, data_filename: str, vectors_filename:
        str,
            model_name: str,
            documents: list[Metadata], embedding_size: int, distance: Distance = Distance.COSINE
    ):

        self.collection_name = collection_name
        self.client = QdrantClient(host, port)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=device)
        self.client = QdrantClient(host, port)

        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=embedding_size,
                distance=distance
            )
        )

        data =
        vectors_path = os.path.join(DATA_DIR, vectors_filename)
        if not os.path.exists(vectors_path):
            vectors = self.encode_documents(data_path, vectors_path)
        else:
            vectors = np.load(vectors_path)

        payload = pd.read_csv(os.path.join(DATA_DIR, "metadata_pt.csv")).to_dict(orient="records")
        self.client.upload_collection(
            collection_name=collection_name,
            vectors=vectors,
            payload=payload,
            ids=None,
            batch_size=256
        )

    def text_for_encoding(self, row):
        return row.title_pt + ". " + row.abstract_pt + " " + row.keywords_pt

    def encode_documents(self, db_path, vectors_path):
        data = pd.read_csv(db_path)
        vectors = []
        batch_size = 64
        batch = []
        for row in data.itertuples():
            descriptions = []
            pre = self.text_for_encoding(row)
            batch.append(pre)
            if len(batch) >= batch_size:
                vectors.append(self.model.encode(batch, batch_size=len(batch)))
                batch = []
        if len(batch) > 0:
            vectors.append(self.model.encode(batch))
            batch = []

        vectors = np.concatenate(vectors)
        np.save(os.path.join(vectors_path), vectors, allow_pickle=False)
        return vectors
