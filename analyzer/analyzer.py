from summarizer import Summarizer

class Analyzer:
    def __init__(self):
        self.summarizer = Summarizer()

    def analyze(self, data):
        summaries = []
        for article in data:
            summary = self.summarizer(article["content"])
            summaries.append(summary)
        return summaries
