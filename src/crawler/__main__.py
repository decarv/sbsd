"""
BASE_URLS: as url base foram obtidas da área do site "Área do Conhecimento".
"""
import sys
import config
from crawler import Crawler

BASE_URL = "https://www.teses.usp.br"

crawler = Crawler(
    base_url=BASE_URL,
    data_path=config.DATA_PATH,
    logs_path=config.LOGS_PATH,
    errors_path=config.ERRORS_PATH,
    database=config.WEBPAGES_DATABASE,
)
crawler.execute()
