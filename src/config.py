import os

# Global configuration
DATA_DIR = os.path.abspath("../data")
LOGS_DIR = os.path.abspath("../logs")
ERRORS_DIR = os.path.abspath("../data")
DATABASES_DIR = os.path.abspath("../data/databases")
VECTORS_DIR = os.path.abspath("../data/npy")

DATABASE = os.path.join(DATABASES_DIR, "database.db")
ERRORS_DATABASE = os.path.join(DATABASES_DIR, "errors.db")

# Crawler configuration
BASE_URL = "https://www.teses.usp.br"
SITEMAP = "https://www.teses.usp.br/sitemap.xml"

# Searcher configuration
THESES_QUERY_URL: str = (
        "https://teses.usp.br/index.php?option=com_jumi&fileid=19"
        "&Itemid=87&lang=pt&g=1&b3={}&c3=p&o3=AND"
)
RESULT_SIZE: int = 30

# Qdrant configuration
COLLECTIONS = [
        "abstracts",  # collection created with the abstracts texts
        "theses",  # collection created with theses paragraphs texts
]

MODELS = [
        "distilbert-base-nli-stsb-mean-tokens"
]

HOST = "0.0.0.0"
PORT = "6333"
