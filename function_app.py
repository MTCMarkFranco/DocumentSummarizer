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
                
app = func.FunctionApp()

@app.route(route="doc_summarizer",methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def doc_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # Load environment variables from .env file
    load_dotenv()
    key = os.getenv('LANG_KEY')
    endpoint = os.getenv('LANG_ENDPOINT')

    # Get the Request Body
    req_body = req.get_json()
    first_item = req_body.get('values', [{}])[0]
    record = Record(**first_item)
    documentcontent = Data(**record.data)
    
    # Two Pieces of Info We Need
    recordid = record.recordId
    document = documentcontent.merged_content
       
    # call summarizer
    summarizer = Summarizer(key, endpoint)
    summary = summarizer.summarize(document)
    
    logging.log(logging.INFO, f"Summarizer Response: {summary}")
    
    response = {
        "values": [
            {
                "recordId": recordid,
                "data": {
                    "summary": summary
                },
                "errors": [],
                "warnings": []
            }
        ]
    }
    logging.log(logging.INFO, f"Complete Response: {response}")

    return func.HttpResponse(f"{response}", mimetype="application/json", status_code=200)
    
    
    
    
    
   