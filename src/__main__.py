"""

"""
import uvicorn
from server import Server
from search import Searcher

from config import COLLECTION_NAME, MODEL_NAME, HOST, PORT

search_client = Searcher(COLLECTION_NAME, MODEL_NAME, HOST, PORT, )
server = Server(search_client)
uvicorn.run(server.app, host=HOST, port=8000)
