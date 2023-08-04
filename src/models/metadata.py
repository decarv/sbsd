
import re
from models.webpage import Webpage


class Metadata:
    """
    TODO: documentation
    """
    def __init__(self, webpage: Webpage):
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

        self.parse_metadata(webpage)

    def __repr__(self):
        return str(self.__dict__)

    def parse_metadata(self, webpage):
        """
        TODO: documentation
        :param webpage:
        :return:
        """
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

    def to_dict(self):
        return {
            "title": self.title_pt,
            "author": self.author,
            "knowledge_area": self.knowledge_area,
        }