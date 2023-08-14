import os

# Global configuration
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")
ERRORS_DIR = os.path.join(PROJECT_DIR, "data")
VECTORS_DIR = os.path.join(PROJECT_DIR, "data", "npy")
EMBEDDINGS_DIR = os.path.join(PROJECT_DIR, "data", "embeddings")
INDICES_DIR = os.path.join(PROJECT_DIR, "data", "indices")
MODELS_DIR = os.path.join(PROJECT_DIR, "data", "models")
DATABASES_DIR = os.path.join(PROJECT_DIR, "data", "databases")
DATABASE = os.path.join(DATABASES_DIR, "database.db")
ERRORS_DATABASE = os.path.join(DATABASES_DIR, "errors.db")

# Crawler configuration
BASE_URL = "https://www.teses.usp.br"
SITEMAP = "https://www.teses.usp.br/sitemap.xml"

# Searcher configuration
THESES_QUERY_URL: str = (
        "https://teses.usp.br/index.php?option=com_jumi&fileid=19"
        "&Itemid=87&lang=pt&g=1&b3={}&c3=p&o3=AND&pagina="
)
RESULT_SIZE: int = 30

# Qdrant configuration
COLLECTIONS = [
        "abstracts",  # collection created with the abstracts texts
        "theses",  # collection created with theses paragraphs texts
]

MODELS = [
        "distilbert-base-nli-stsb-mean-tokens",
        "neuralmind/bert-base-portuguese-cased"
]

HOST = "0.0.0.0"
PORT = "6333"
