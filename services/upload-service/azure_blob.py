def upload_to_blob(doc_id, file):
    # LOCAL MOCK: Just pretend it's uploaded
    return f"mock://blob/{doc_id}/{file.filename}"