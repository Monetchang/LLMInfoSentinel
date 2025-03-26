from fetcher.fetcher import HuggingFaceModelFetcher
import json

if __name__ == "__main__":
    fetcher = HuggingFaceModelFetcher()
    models = fetcher.fetch()

    # 按时间排序
    models.sort(key=lambda x: x["time"], reverse=True)

    # 打印已抓取的模型信息
    for model in models:
        print(f"Title: {model['title']}")
        print(f"Link: {model['link']}")
        print(f"Time: {model['time']}")
        print("-" * 50)