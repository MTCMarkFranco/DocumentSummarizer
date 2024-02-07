import json
import azure.functions as func
from dotenv import load_dotenv
import os
import logging
from summarization_class import Summarizer

class Data:
    def __init__(self, merged_content):
        self.merged_content = merged_content

class Record:
    def __init__(self, recordId, data):
        self.recordId = recordId
        self.data = data

def summarize_document(record, summarizer):
    """Summarize a document using a given summarizer."""
    documentcontent = Data(**record.data)
    document = documentcontent.merged_content
    summary = summarizer.summarize(document)
    logging.info(f"Summarizer Response: {summary}")
    return summary

app = func.FunctionApp()

@app.route(route="doc_summarizer",methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def doc_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # Load environment variables from .env file
    load_dotenv()
    key = os.getenv('LANG_KEY')
    endpoint = os.getenv('LANG_ENDPOINT')

    # Get the merged_content from the request body
    try:
        req_body = req.get_json()
        first_item = req_body.get('values', [{}])[0]
        record = Record(**first_item)
    except Exception as e:
        logging.error(f"Error parsing request body: {e}")
        return func.HttpResponse(f"Error parsing request body: {e}", status_code=400)

    # Call summarizer
    summarizer = Summarizer(key, endpoint)
    try:
        summary = summarize_document(record, summarizer)
    except Exception as e:
        logging.error(f"Error summarizing document: {e}")
        return func.HttpResponse(f"Error summarizing document: {e}", status_code=500)

    # Send the summary back
    response = {
        "values": [
            {
                "recordId": record.recordId,
                "data": {
                    "summary": summary
                },
                "errors": [],
                "warnings": []
            }
        ]
    }
    logging.info(f"Complete Response: {response}")

    return func.HttpResponse(json.dumps(response), mimetype="application/json", status_code=200)