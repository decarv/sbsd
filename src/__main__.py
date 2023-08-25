"""

"""
import uvicorn
from server import Server
from search import Searcher

from config import COLLECTION_NAME, MODEL_NAME, QDRANT_DB_HOST, QDRANT_DB_PORT

search_client = Searcher(COLLECTION_NAME, MODEL_NAME, QDRANT_DB_HOST, QDRANT_DB_PORT, )
server = Server(search_client)
uvicorn.run(server.app, host=QDRANT_DB_HOST, port=8000)
