"""

"""

from ingestor import Ingestor
from indexer import Indexer
from searcher import Searcher


class Engine:
    def __init__(self, ingestor: Ingestor, indexer: Indexer, processor, searcher:
    Searcher):
        self.ingestor = ingestor
        self.indexer = indexer
        self.searcher = searcher

    # receive_query
    # process_query
    def search_query(self, query: str):
        self.searcher.process_query()
