from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import logging

class Summarizer:
    def __init__(self,  key, endpoint):
        self.text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        )
        self.logger = logging.getLogger("__INDEXER__")

    def summarize_chunk(self, documentchunk):
        
        document_chunk_record = [{'id': '1','text': documentchunk }]

        try:
            poller = self.text_analytics_client.begin_abstract_summary(
                documents=document_chunk_record,
                language='en',
                sentence_count=4
            )
            abstract_summary_results = poller.result()
        except Exception as e:
            logging.error(f"Error in summarization: {e}")
            return f"Error in summar: {e}"

        for result in abstract_summary_results:
            if result.kind == "AbstractiveSummarization":
                return result.summaries[0].text
            elif result.is_error is True:
                return "...Is an error with code '{}' and message '{}'".format(
                    result.error.code, result.error.message
        )