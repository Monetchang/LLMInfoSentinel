from fetcher.fetcher import HuggingFaceFetcher

def main():
    print("Fetching latest Hugging Face Blog articles...\n")
    
    fetcher = HuggingFaceFetcher()
    articles = fetcher.fetch_articles()

    if not articles:
        print("No articles found or failed to fetch data.")
        return

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Published on: {article['time']}")
        print(f"   Link: {article['link']}\n")

if __name__ == "__main__":
    main()
