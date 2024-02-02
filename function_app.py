import azure.functions as func
import datetime
import json
import logging

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
    logging.error('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    first_item = req_body.get('values', [{}])[0]
    record = Record(**first_item)
    documentcontent = Data(**record.data)
    
    # Two Pieces of Info We Need
    recordid = record.recordId
    document = documentcontent.merged_content
    
    
    summary = "The Summary of the Document that will be returned for every document"
    
    response = {
        "values": [
            {
                "recordId": recordid,
                "data": {
                    "extractivesummary": summary
                },
                "errors": [],
                "warnings": []
            }
        ]
    }
    logging.log(logging.INFO, f"Response: {response}")

    return func.HttpResponse(f"{response}", mimetype="application/json", status_code=200)
    
    
    
    
    
   