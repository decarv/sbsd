import uvicorn
from server import Server
from search import SearchClient

from config import COLLECTION_NAME, MODEL_NAME, HOST, PORT


search_client = SearchClient(COLLECTION_NAME, MODEL_NAME, HOST, PORT)
server = Server(search_client)
uvicorn.run(server.app, host=HOST, port=8000)
