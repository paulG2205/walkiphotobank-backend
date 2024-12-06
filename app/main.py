from fastapi import FastAPI, HTTPException, Query
from app.elasticsearch import search_in_elasticsearch
from app.scraper_service import using_pinterest_apis, using_search_engine
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/search")
def search(q: str = Query(..., description="Keyword for search")):
    try:
        search_engine_urls = using_search_engine(q)
        pinterest_urls = using_pinterest_apis(q)

        all_urls = search_engine_urls + pinterest_urls

        message, results, count = search_in_elasticsearch(q, urls=all_urls)

        return {
            "message": message,
            "query": q,
            "results": results,
            "search_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))