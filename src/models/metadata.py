"""
models.metadata

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

import re
from models.webpage import Webpage


class Metadata:
    """
    TODO:
        - Refactor this class as a class
    """
    def __init__(self, webpage: Webpage = None):
        self.url: str
        self.doi: str
        self.type: str
        self.author: str
        self.institute: str
        self.knowledge_area: str
        self.committee: str
        self.title_pt: str
        self.title_en: str
        self.keywords_pt: str
        self.keywords_en: str
        self.abstract_pt: str
        self.abstract_en: str
        self.publish_date: str

        if webpage is not None:
            self.parse_metadata(webpage)

    def __repr__(self):
        return str(self.__dict__)

    def parse_metadata(self, webpage):
        """
        TODO: documentation
        :param webpage:
        :return:
        """
        if not webpage.is_processed:
            raise Exception

        self.url = webpage.url
        raw_metadata = webpage.soup.find_all(class_="DocumentoTexto")
        raw_metadata_keys = webpage.soup.find_all(class_="DocumentoTituloTexto")
        metadata = {
            k.text.strip().lower(): re.sub(r"\s+", " ", v.text.strip())
            for (k, v) in zip(raw_metadata_keys, raw_metadata)
        }
        self.doi = metadata.get("doi", None)
        self.type = metadata.get("documento", None)
        self.author = metadata.get("autor", None)
        self.institute = metadata.get("unidade da usp", None)
        self.knowledge_area = metadata.get("área do conhecimento", None)
        self.committee = metadata.get("banca examinadora", None)
        self.title_pt = metadata.get("título em português", None)
        self.keywords_pt = metadata.get("palavras-chave em português", None)
        self.title_en = metadata.get("título em inglês", None)
        self.keywords_en = metadata.get("palavras-chave em inglês", None)
        self.publish_date = metadata.get("data de publicação", None)

        raw_data = webpage.soup.find_all(class_="DocumentoTextoResumo")
        raw_data_keys = webpage.soup.find_all(class_="DocumentoTituloTexto2")
        data = {
            k.text.strip().lower(): re.sub(r"\s+", " ", v.text.strip())
            for (k, v) in zip(raw_data_keys, raw_data)
        }
        self.abstract_pt = data.get("resumo em português", None)
        self.abstract_en = data.get("resumo em inglês", None)
        return self

    def parse_db_instance(self, instance):
        """TODO: documentation"""
        attributes = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for inst, attr in zip(instance, attributes):
            setattr(self, attr, inst)
        return self

    def to_dict(self):
        """TODO: documentation"""
        return {
            "title": self.title_pt,
            "author": self.author,
            "knowledge_area": self.knowledge_area,
        }

    def __hash__(self):
        return hash(self.doi)