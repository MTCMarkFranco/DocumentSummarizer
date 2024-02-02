from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import json

class Summarizer:
    def __init__(self,  key, endpoint):
        self.text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    def summarize(self, text):
        summarizerResponse = None
                
        # Create a list of documents. Each document is a dictionary with an 'id' and 'text' field.
        documents = [{'id': '12','text': text }]
        
        poller = self.text_analytics_client.begin_abstract_summary(
            documents=documents,
            language='en',
            sentence_count=4
            )
        abstract_summary_results = poller.result()
        for result in abstract_summary_results:
            if result.kind == "AbstractiveSummarization":
                summarizerResponse = result.summaries[0].text
            elif result.is_error is True:
                summarizerResponse = "...Is an error with code '{}' and message '{}'".format(
                    result.error.code, result.error.message
                )
        return summarizerResponse