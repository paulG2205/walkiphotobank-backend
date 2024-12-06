from elasticsearch import Elasticsearch, NotFoundError

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=("elastic", "cB7AAT0k")
)

def search_in_elasticsearch(q: str, index_name: str = "your_index", urls: list = []):
    """
    Search or update a document in Elasticsearch and include scraping URLs in results.
    """
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    try:
        doc = es.get(index=index_name, id=q)
        current_count = doc["_source"].get("count", 0)
        new_count = current_count + 1
        es.update(index=index_name, id=q, body={"doc": {"count": new_count}})
        message = "Query found and count updated"
        updated_count = new_count
    except NotFoundError:
        es.index(index=index_name, id=q, body={"query": q, "count": 1})
        message = "Query executed and saved"
        updated_count = 1

    es_results = es.search(index=index_name, body={"query": {"match": {"query": q}}})
    results = [{"source": "elasticsearch", "data": hit["_source"]} for hit in es_results["hits"]["hits"]]
    results.extend([{"source": "scraper", "url": url} for url in urls])

    return message, results, updated_count