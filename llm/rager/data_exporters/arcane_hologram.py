from typing import Dict, List, Union
import numpy as np
from elasticsearch import Elasticsearch
from datetime import datetime

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from mage_ai.data_preparation.variable_manager import set_global_variable

@data_exporter
def elasticsearch(
    documents: List[Dict[str, Union[Dict, List[int], np.ndarray, str]]], *args, **kwargs,
):
    """
    Exports document data to an Elasticsearch database.
    """

    # Get connection parameters
    connection_string = kwargs.get('connection_string', 'http://elasticsearch:9200')
    index_name_prefix = kwargs.get('index_name', 'documents')
    number_of_shards = kwargs.get('number_of_shards', 1)
    number_of_replicas = kwargs.get('number_of_replicas', 0)
    
    # Include timestamp in index name
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_name = f"{index_name_prefix}_{current_time}"
    print("Index name:", index_name)
    
    # Save the index name in a global variable
    set_global_variable('nebulous_enigma', 'index_name', index_name)

    # Elasticsearch client setup
    es_client = Elasticsearch(connection_string)
    print(f'Connecting to Elasticsearch at {connection_string}')

    # Define index settings without embedding
    index_settings = {
        "settings": {
            "number_of_shards": number_of_shards,
            "number_of_replicas": number_of_replicas,
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "section": {"type": "text"},
                "question": {"type": "text"},
                "course": {"type": "keyword"},
                "document_id": {"type": "keyword"}
            }
        }
    }

    # Create index if it does not exist
    if not es_client.indices.exists(index=index_name):
        es_client.indices.create(index=index_name, body=index_settings)
        print('Index created with properties:', index_settings)

    # Index documents
    print(f'Indexing {len(documents)} documents to Elasticsearch index {index_name}')
    for document in documents:
        print(f'Indexing document {document["document_id"]}')
        es_client.index(index=index_name, document=document)
    
    # Print the last document
    if documents:
        print('Last document:', documents[-1])
