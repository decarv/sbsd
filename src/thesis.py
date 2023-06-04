import re
from bs4 import BeautifulSoup


class Thesis:
    def __init__(self, **kwargs):
        self.doi = kwargs.get("doi", None)
        self.type = kwargs.get("type", None)
        self.author = kwargs.get("author", None)
        self.institute = kwargs.get("institute", None)
        self.knowledge_area = kwargs.get("knowledge_area", None)
        self.committee = kwargs.get("committee", None)
        self.title_pt = kwargs.get("title_pt", None)
        self.title_en = kwargs.get("title_en", None)
        self.keywords_pt = kwargs.get("keywords_pt", None)
        self.keywords_en = kwargs.get("keywords_en", None)
        self.abstract_pt = kwargs.get("abstract_pt", None)
        self.abstract_en = kwargs.get("abstract_en", None)
        self.publish_date = kwargs.get("publish_date", None)

    def __repr__(self):
        return str(self.__dict__)

    def parse_webpage(self, webpage):
        soup = BeautifulSoup(webpage, 'html.parser')

        raw_metadata = soup.find_all(class_="DocumentoTexto")
        raw_metadata_keys = soup.find_all(class_="DocumentoTituloTexto")
        metadata = {
            k.text.strip().lower(): re.sub(r"\s+", " ", v.text.strip())
            for (k, v) in zip(raw_metadata_keys, raw_metadata)
        }
        self.doi = metadata.get("doi")
        self.type = metadata.get("documento")
        self.author = metadata.get("autor")
        self.institute = metadata.get("unidade da usp")
        self.knowledge_area = metadata.get("área do conhecimento")
        self.committee = metadata.get("banca examinadora")
        self.title_pt = metadata.get("título em português")
        self.keywords_pt = metadata.get("palavras-chave em português")
        self.title_en = metadata.get("título em inglês")
        self.keywords_en = metadata.get("palavras-chave em inglês")
        self.publish_date = metadata.get("data de publicação")

        raw_data = soup.find_all(class_="DocumentoTextoResumo")
        raw_data_keys = soup.find_all(class_="DocumentoTituloTexto2")
        data = {
            k.text.strip().lower(): re.sub(r"\s+", " ", v.text.strip())
            for (k, v) in zip(raw_data_keys, raw_data)
        }
        self.abstract_pt = data.get("resumo em português")
        self.abstract_en = data.get("resumo em inglês")
