from typing import Dict, List
from elasticsearch import Elasticsearch, exceptions

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def search(*args, **kwargs) -> List[Dict]:
    """
    Perform a text search query on Elasticsearch.
    """

    connection_string = kwargs.get('connection_string', 'http://elasticsearch:9200')
    index_name = kwargs.get('index_name', 'documents')
    user_query = kwargs.get('user_query', "When is the next cohort?")  # Default query if not provided
    top_k = kwargs.get('top_k', 5)
    chunk_column = kwargs.get('chunk_column')  # Field to return from the documents

    # Define the search query
    text_query = {
        "size": top_k,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": user_query,
                            "fields": ["question^3", "text", "section"],  # Fields to search
                            "type": "best_fields"
                        }
                    }
                ],
                "filter": [
                    {
                        "term": {
                            "course": "llm-zoomcamp"  # Filter condition (if any)
                        }
                    }
                ]
            }
        }
    }

    print("Sending text query:", text_query)

    es_client = Elasticsearch(connection_string)

    try:
        response = es_client.search(
            index=index_name,
            body=text_query
        )

        print("Raw response from Elasticsearch:", response)

        results = []
        for hit in response['hits']['hits']:
            source = hit.get('_source', {})
            if chunk_column in source:
                results.append({
                    "section": source.get("section"),
                    "question": source.get("question"),
                    "answer": source.get("text")[:60] + "...",  # Truncate text for readability
                    "document_id": source.get("document_id")
                })
            else:
                print(f"Warning: '{chunk_column}' not found in document ID {hit['_id']}. Available fields: {list(source.keys())}")

        return results

    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
