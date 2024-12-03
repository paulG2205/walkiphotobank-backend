from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError

app = FastAPI()

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=("elastic", "cB7AAT0k")
)

@app.get("/search")
def search(q: str):
    try:
        main_index = "your_index"
        
        if not es.indices.exists(index=main_index):
            es.indices.create(index=main_index)
        
        query_doc_id = q 
        try:
            doc = es.get(index=main_index, id=query_doc_id)
            # Increment a search count or append new results
            current_count = doc["_source"].get("count", 0)
            new_count = current_count + 1
            es.update(
                index=main_index,
                id=query_doc_id,
                body={"doc": {"count": new_count}}
            )
            message = "Query found and count updated"
            updated_count = new_count
        except NotFoundError:
            # If the query does not exist, create a new document
            es.index(index=main_index, id=query_doc_id, body={"query": q, "count": 1})
            message = "Query executed and saved"
            updated_count = 1
        
        res = es.search(index=main_index, body={"query": {"match": {"field": q}}})
        results = res["hits"]["hits"]

        return {
            "message": message,
            "query": q,
            "results": results,
            "search_count": updated_count
        }

    except ConnectionError:
        raise HTTPException(status_code=503, detail="Elasticsearch service is unavailable")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")