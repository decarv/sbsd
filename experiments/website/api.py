from utils import get_request, post_request
from fastapi import FastAPI

app = FastAPI()



@app.get("/search")
async def search(query: str):
    query_url = teses_keyword_search_endpoint.format(query.replace(" ", "%20"))

    return {"query": query}
