import requests
from bs4 import BeautifulSoup
import time

class Fetcher:
    def __init__(self, sources):
        self.sources = sources

    def fetch_data(self):
        for source in self.sources:
            if source["type"] == "rss":
                self.fetch_rss(source["url"])
            elif source["type"] == "html":
                self.fetch_html(source["url"])

    def fetch_rss(self, url):
        response = requests.get(url)
        print(f"Fetched data from RSS: {url}")

    def fetch_html(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data from HTML: {url}")
