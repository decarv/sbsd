"""
encoder

Copyright (c) 2023 Henrique Araújo de Carvalho

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
import os
import re
import logging
import numpy as np
import pandas as pd
from typing import Union

import config
from utils import log, save_embeddings, save_indices
from sentence_transformers import SentenceTransformer

from utils import batch_generator


class Encoder:
    """TODO: Documentation"""
    def __init__(self, data, model_name: str,
                 embeddings_dir=None, indices_dir=None,
                 batch_size=64, language: str = "pt"):
        self.data = data
        self.language = language
        self.model_name = model_name.split("/")[-1]
        self.model = SentenceTransformer(model_name, device='cuda')
        self.indices_dir = indices_dir
        self.embeddings_dir = embeddings_dir
        if not os.path.exists(self.embeddings_dir) or not os.path.exists(self.indices_dir):
            logging.error("Either embeddings or indices save path does not exist.")
            sys.exit(1)
        self.batch_size = batch_size
        self.encoded_data = None

    @staticmethod
    def clean_embedding_units(embedding_units: list[str]) -> list[str]:
        """
        Cleans embedding units.
        Removes leading and trailing whitespace from each string in the given list of strings.
        Removes empty strings from the given list of strings.
        """
        embedding_units = [s.strip() for s in embedding_units]
        embedding_units = [s for s in embedding_units if s != '']
        return embedding_units

    def generate_embedding_units(self, title: str, abstract: str, keywords: str) -> dict[str, list[str]]:
        """
        Generate various textual groupings to serve as inputs for embeddings.

        Parameters:
            - title (str): Document title.
            - abstract (str): Document abstract.
            - keywords (str): Document keywords.

        Returns:
            - dict: Dictionary containing:
                "sentences" -> List of sentences as units to be vectorized.
                "text" -> List containing the whole concatenated text.
                "sentences_and_text" -> Combined list of sentences and the entire text.
        """

        text_embedding_unit: list[str] = [(title + ". " + abstract + " " + keywords).strip()]

        title_units: list[str] = title.split(".")
        abstract_units: list[str] = abstract.split(".")

        # Split keywords by uppercase letters
        keywords_units: list[str] = []
        keyword = ""
        for word in keywords.split():
            if word[0].isupper():
                if keyword != "":
                    keywords_units.append(keyword.strip())
                keyword = word
            else:
                keyword += " " + word
        keywords_units.append(keyword)

        sentences_embedding_units = self.clean_embedding_units(
            title_units + abstract_units + keywords_units
        )

        return {
            # "words": (title + abstract + keywords).replace(".", "").split(" "),
            "text": text_embedding_unit,
            "sentences": sentences_embedding_units,
            # "sentences_and_text": text_embedding_unit + sentences_embedding_units
        }

    def structure_data_for_embedding(self):
        """
        TODO: Documentation
        - dict: Dictionary structured as:
            {
                "text/sentences/sentences_and_text": {
                    "indices": List mapping single encode input to the index in data.
                    "embedding_units": List of text units for encoding.
                }
            }
        """
        data_to_encode = {k: [] for k in ["text", "sentences"]}
        indices = {k: [] for k in ["text", "sentences"]}
        for index, row in self.data.iterrows():
            embedding_units = self.generate_embedding_units(
                row[f"title_{self.language}"],
                row[f"abstract_{self.language}"],
                row[f"keywords_{self.language}"]
            )
            for k in embedding_units.keys():
                data_to_encode[k] += embedding_units[k]
                indices[k] += [index for _ in range(len(embedding_units[k]))]

        return data_to_encode, indices

    @log
    def encode_embedding_units(self, embedding_units):
        """TODO: Documentation"""
        embeddings = []
        for batch in batch_generator(embedding_units):
            embedding = self.model.encode(batch, batch_size=len(batch), show_progress_bar=False)
            embeddings.append(embedding)
        embeddings = np.concatenate(embeddings)
        return embeddings

    def encode(self, save=True):
        """TODO: Documentation"""
        data_for_embedding, indices = self.structure_data_for_embedding()
        if save and self.embeddings_dir:
            save_indices(indices)
        self.encoded_data = {}
        for units_type, units in data_for_embedding.items():
            embeddings = self.encode_embedding_units(units)
            self.encoded_data[units_type] = embeddings
            if save and self.embeddings_dir:
                save_embeddings(embeddings, self.embeddings_dir, self.model_name, units_type,
                                self.language)
        return self.encoded_data, indices


if __name__ == "__main__":
    metadata = pd.read_csv(os.path.join(config.DATA_DIR, "metadata.csv"), keep_default_na=False)
    encoder = Encoder(
        metadata,
        model_name=config.MODELS[0],
        embeddings_dir=config.EMBEDDINGS_DIR,
        indices_dir=config.INDICES_DIR,
        language="en"
    )
    encoder.encode()
