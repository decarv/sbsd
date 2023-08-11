import random
import requests
from fastapi import FastAPI
from search import Searcher

from models.metadata import Metadata
from utils import get_request
from config import THESES_QUERY_URL, RESULT_SIZE


class Server:
    """
    TODO: documentation
    """

    def __init__(self, search_client: Searcher):
        self.search_client = search_client
        self.app = FastAPI()

        @self.app.get("/experiment")
        async def experiment(query: str):
            """

            :param query:
            :return:
            """
            website_results: list[Metadata] = self.website_query(query)
            engine_results: list[Metadata] = self.engine_query(query)

            results: list[list[int, Metadata]] = []
            results_set: set[Metadata] = set()
            i: int = 0
            j: int = 0
            while len(results) <= RESULT_SIZE:
                if website_results[i] not in results_set:
                    results.append([i, website_results[i]])
                i += 1
                if engine_results[j] not in results_set:
                    results.append([j, engine_results[j]])
                j += 1

            return {
                "result": results
            }

        self.experiment = experiment


    def website_query(self, query) -> list[dict]:
        """

        :param query:
        :return:
        """
        formatted_theses_query_url: str = THESES_QUERY_URL.format(query.replace(" ", "%20"))
        response: requests.Response = get_request(formatted_theses_query_url)
        if response is not None:
            results_titles: list[str] = parse_response_titles(response)
            results: list[dict] = database_search_metadata(results_titles)
            return results

    def engine_query(self, query) -> list[dict]:
        """

        :return:
        """
        results: list[dict] = self.search_client.retrieve(query)
        return results