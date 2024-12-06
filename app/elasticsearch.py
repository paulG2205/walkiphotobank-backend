from elasticsearch import Elasticsearch, NotFoundError

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=("elastic", "cB7AAT0k")  # Configuración de Elasticsearch
)

def search_in_elasticsearch(q: str, index_name: str = "photos"):
    """
    Busca en Elasticsearch para el término exacto (match_phrase).
    """
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "url": {"type": "text"},
                        "keyword": {"type": "text"},
                        "source": {"type": "text"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
        )

    try:
        # Usar `match_phrase` para buscar el término exacto
        es_results = es.search(index=index_name, body={
            "query": {
                "match_phrase": {
                    "keyword": q.lower()  # Buscar el término exacto
                }
            },
            "size": 100
        })

        if es_results["hits"]["hits"]:
            results = [
                {
                    "source": "elasticsearch",
                    "data": hit["_source"]
                }
                for hit in es_results["hits"]["hits"]
                if hit["_source"]["keyword"] == q.lower()  # Asegurarse de que coincide exactamente
            ]
            return "Results fetched from Elasticsearch", results, len(results)

        # Si no hay resultados
        return "No results in Elasticsearch", [], 0

    except Exception as e:
        raise RuntimeError(f"Error searching in Elasticsearch: {e}")