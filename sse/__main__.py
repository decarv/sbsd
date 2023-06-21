import uvicorn
from server import Server
from search import SearchClient

import config


def run():
    search_client = SearchClient(config.COLLECTION_NAME, config.MODEL_NAME, config.HOST, config.PORT)
    server = Server(search_client)
    uvicorn.run(server.app, host=config.HOST, port=8000)

run()