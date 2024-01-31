import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.route(route="doc_summarizer", auth_level=func.AuthLevel.FUNCTION)
def doc_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    document = req.params.get('document')
    if not document:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            document = req_body.get('document')

    if document:
        return func.HttpResponse(f"Hello, {document}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )