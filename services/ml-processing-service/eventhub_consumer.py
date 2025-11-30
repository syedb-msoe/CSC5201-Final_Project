from form_recognizer import extract_text
from cosmos_client import save_result

def start_event_consumer():
    print("EventHub consumer running (mock)")

    # Mock event
    event = {
        "documentId": "mock-doc",
        "blobUrl": "mock://blob/test.pdf"
    }

    print("Processing event:", event)

    extracted = extract_text(event["blobUrl"])
    save_result(event["documentId"], extracted)