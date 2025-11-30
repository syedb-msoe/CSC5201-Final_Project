_results = {}  # Local in-memory store

def save_result(doc_id, data):
    _results[doc_id] = data
    print("Saved:", data)

def get_result(doc_id):
    return _results.get(doc_id)