from fastapi import FastAPI
from search import SearchClient

import config


class Server:
    """"""

    def __init__(self, search_client: SearchClient):
        self.search_client = search_client

        self.app = FastAPI()

        @self.app.get("/search")
        async def search_query(query: str):
            result = self.search_client.search(query)
            print("Result", result)
            return {
                "result": result
            }
        self.search = search_query