import json
import azure.functions as func
from dotenv import load_dotenv
import os
import logging
import colorlog
import time
from summarization_class import Summarizer

class DurationFormatter(colorlog.ColoredFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()

    def format(self, record):
        duration = time.time() - self.start_time
        self.start_time = time.time()
        record.duration = "{:.1f}".format(duration)
        return super().format(record)
    
# content_chunked is an array of strings
class Data:
    def __init__(self, content_chunked):
        self.content_chunked = content_chunked

class Record:
    def __init__(self, recordId, data):
        self.recordId = recordId
        self.data = data

handler = colorlog.StreamHandler()
handler.setFormatter(DurationFormatter('%(log_color)s%(levelname)s: Previous Step Time: %(duration)s(seconds). Next Step: %(message)s',
            log_colors={
                            'DEBUG': 'cyan',
                            'INFO': 'green',
                            'WARNING': 'yellow',
                            'ERROR': 'red',
                            'CRITICAL': 'red,bg_white',
                        }))
logger: logging.Logger = colorlog.getLogger("__INDEXER__")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
    
def summarize_document(record, summarizer):
    """Summarize a document using a given summarizer."""
    documentcontent = Data(**record.data)
    documentchunks = documentcontent.content_chunked
    summary = summarizer.summarize(documentchunks)
    logger.info(f"Summarizer Response: {summary}")
    return summary

app = func.FunctionApp()

@app.route(route="doc_summarizer",methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def doc_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Python HTTP trigger function processed a request.')
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
        logger.error(f"Error parsing request body: {e}")
        return func.HttpResponse(f"Error parsing request body: {e}", status_code=400)

    # Call summarizer
    summarizer = Summarizer(key, endpoint)
    try:
        summary = summarize_document(record, summarizer)
    except Exception as e:
        logger.error(f"Error summarizing document: {e}")
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
    logger.info(f"Complete Response: {response}")

    return func.HttpResponse(json.dumps(response), mimetype="application/json", status_code=200)