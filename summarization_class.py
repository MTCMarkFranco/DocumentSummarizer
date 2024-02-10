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
        """Summarize a single chunk of a document."""
        documentchunkrecord = [{'id': '1','text': documentchunk }]

        try:
            poller = self.text_analytics_client.begin_abstract_summary(
                documents=documentchunkrecord,
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
          
    def summarize(self, documentchunks):
        """Summarize a list of document chunks."""
        summarizerResponses = []
        
        # need to test if documentchunks is a list of strings or just a string
        if isinstance(documentchunks, str):
            documentchunks = [documentchunks]
        
        for documentchunk in documentchunks:
            summary = self.summarize_chunk(documentchunk)
            summarizerResponses.append(summary)

        if len(summarizerResponses) == 1:
            return summarizerResponses[0]
        elif summarizerResponses:
            summarizerResponses = ' '.join(summarizerResponses)
            final_summary = self.summarize_chunk(summarizerResponses)
            return final_summary
        else:
            return "No summarizer responses found."

        