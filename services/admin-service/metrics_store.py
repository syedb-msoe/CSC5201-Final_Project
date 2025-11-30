metrics = {
    "upload_calls": 0,
    "ml_calls": 0,
    "results_calls": 0
}

def record(key: str):
    metrics[key] += 1