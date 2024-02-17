from ast import Dict
import json
from attr import dataclass, field
import azure.functions as func
from dotenv import load_dotenv
import os
import logging
import colorlog
import time
from typing import List, Any, Optional

#local imports
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
    
class InputData:
    def __init__(self, text):
        self.text = text

class InputRecord:
    def __init__(self, recordId, data):
        self.recordId = recordId
        self.data = data
        
@dataclass
class Error:
    message: str

@dataclass
class Warning:
    message: str

@dataclass
class Data:
    summary: str

@dataclass
class Value:
    recordId: str
    data: Data
    errors: List[Error]
    warnings: List[Warning]
        

handler = colorlog.StreamHandler()
console_handler = logging.StreamHandler()
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
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

app = func.FunctionApp()

@app.route(route="doc_summarizer",methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def doc_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Python HTTP trigger function processed a request.')
    # Load environment variables from .env file
    load_dotenv()
    key = os.getenv('LANG_KEY')
    endpoint = os.getenv('LANG_ENDPOINT')

    logger.info(req.get_json())
    # Get the merged_content from the request body
    try:
        req_body = req.get_json()
        logger.info(f"Request Body: {json.dumps(req_body)}")
        values = req_body.get('values', [{}])
        records = [InputRecord(**value) for value in values]
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return func.HttpResponse(f"Error parsing request body: {e}", status_code=400)

    # Call summarizer
    try:
        responseRecords = []
        summarizer = Summarizer(key, endpoint)
        
        for record in records:
            dataSection = InputData(**record.data)
            record_id = record.recordId
            document_chunk = dataSection.text
            chunksummary = summarizer.summarize_chunk(document_chunk)
            logger.info(f"Summary : {chunksummary}")
            responseRecord = Value(recordId=record_id, data={"summary": chunksummary}, errors=None, warnings=None)
            responseRecords.append(responseRecord)
        
        response = { "values": [record.__dict__ for record in responseRecords]}
        
        # Send the summary back
        logger.info(f"Complete Response: {response}")
        return func.HttpResponse(json.dumps(response), mimetype="application/json", status_code=200)    
        
        
    except Exception as e:
        logger.error(f"Error summarizing document: {e}")
        return func.HttpResponse(f"Error summarizing document: {e}", status_code=500)
