import requests
from bs4 import BeautifulSoup

class HuggingFaceFetcher:
    def __init__(self):
        self.base_url = "https://huggingface.co"
        self.blog_url = f"{self.base_url}/blog"

    def fetch_articles(self):
        try:
            response = requests.get(self.blog_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching Hugging Face Blog: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        articles = []

        # 解析第一种 HTML 结构（包含 <a> 标签和 <h4> 标题）
        for article in soup.find_all("a", class_="relative block px-3 py-2 cursor-pointer"):
            title_element = article.find("h4")
            time_element = article.find("time")
            if title_element and time_element:
                title = title_element.text.strip()
                time = time_element["datetime"]
                link = self.base_url + article["href"]
                articles.append({"title": title, "link": link, "time": time})

        # 解析第二种 HTML 结构（包含 JSON 数据）
        for article in soup.find_all("div", class_="SVELTE_HYDRATER"):
            try:
                data_props = article["data-props"]
                blog_data = eval(data_props.replace("true", "True").replace("false", "False"))["blog"]
                title = blog_data["title"]
                slug = blog_data["slug"]
                time = blog_data["publishedAt"]
                link = f"{self.base_url}/blog/{slug}"
                articles.append({"title": title, "link": link, "time": time})
            except Exception as e:
                print(f"Error parsing article data: {e}")

        return articles

