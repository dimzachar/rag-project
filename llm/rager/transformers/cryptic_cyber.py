import hashlib
from typing import Any, Dict, List

def generate_document_id(doc: Dict[str, Any]) -> str:
    combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id

@transformer
def chunk_documents(data: Any) -> List[Dict[str, Any]]:
    documents = []
    
    if isinstance(data, dict):
        for doc in data.get('documents', []):
            doc['course'] = data.get('course', '')
            doc['document_id'] = generate_document_id(doc)
            documents.append(doc)
    
    elif isinstance(data, list):
        for course_dict in data:
            if isinstance(course_dict, dict):
                for doc in course_dict.get('documents', []):
                    doc['course'] = course_dict.get('course', '')
                    doc['document_id'] = generate_document_id(doc)
                    documents.append(doc)
    
    print(len(documents))
    return documents
