from elasticsearch import Elasticsearch
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from app.elasticsearch import search_in_elasticsearch
from app.scraper_service import run_scraper_and_save, using_pinterest_apis, using_search_engine
from fastapi.middleware.cors import CORSMiddleware

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=("elastic", "cB7AAT0k")  
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/search")
def search(background_tasks: BackgroundTasks, q: str = Query(..., description="Keyword for search")):
    try:
        # Buscar en Elasticsearch primero
        message, results, count = search_in_elasticsearch(q)

        if message == "Results fetched from Elasticsearch":
            return {
                "message": message,
                "query": q,
                "results": results,
                "search_count": count
            }

        # Si no hay resultados, ejecutar el scrapper en segundo plano
        background_tasks.add_task(run_scraper_and_save, q)
        print("Scraping started in background.")
        return {
            "message": "No data found in Elasticsearch. Scraping started in background.",
            "query": q,
            "results": [],
            "search_count": 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))