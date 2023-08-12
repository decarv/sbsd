from src.server import Server
from src.utils import get_request, post_request
from fastapi import FastAPI

app = FastAPI()



@app.get("/search")
async def search(query: str):

    return {"query": query}
