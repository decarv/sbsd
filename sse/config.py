import os

BASE_URL = "https://www.teses.usp.br"
SITEMAP = "https://www.teses.usp.br/sitemap.xml"

# Global configuration
DATA_DIR = os.path.abspath("../data")
LOGS_DIR = os.path.abspath("../logs")
ERRORS_DIR = os.path.abspath("../data")

WEBPAGES_DATABASE = "webpages.db"
ERRORS_DATABASE = "errors.db"

COLLECTION_NAME = "theses"
MODEL_NAME = "distilbert-base-nli-stsb-mean-tokens"

HOST = "0.0.0.0"
PORT = "6333"