import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import logging
from time import sleep  # 修改导入语句

class HuggingFaceModelFetcher:
    def __init__(self, config_path="config/config.json"):
        self.logger = self.setup_logger()
        self.config = self.load_config(config_path)
        self.url = self.get_subscription_url("Hugging Face Models - Deepseek")
        self.session = requests.Session()  # 使用会话以保持连接

    def setup_logger(self):
        """设置日志记录"""
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def load_config(self, config_path):
        """加载配置文件"""
        if not os.path.exists(config_path):
            self.logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self.logger.info(f"Config file loaded successfully from {config_path}")
            return json.load(f)

    def get_subscription_url(self, name):
        """从 subscriptions 列表中获取指定订阅源的 URL"""
        for sub in self.config.get("subscriptions", []):
            if sub.get("name") == name:
                self.logger.info(f"Found subscription URL for {name}")
                return sub.get("url")
        self.logger.error(f"Subscription '{name}' not found in config.")
        raise ValueError(f"Subscription '{name}' not found in config.")

    def fetch_model_stats(self, url):
        """获取模型统计信息"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            stats = {}
            
            # 获取点赞数
            likes_button = soup.find("button", {"title": "See users who liked this repository"})
            self.logger.info(f"likes_button ---->  {likes_button}")
            if likes_button:
                likes_text = likes_button.get_text(strip=True)
                self.logger.info(f"Found likes text: {likes_text}")
                # 转换数字格式（如 "3.72k" 转换为 3720）
                if 'k' in likes_text.lower():
                    stats["likes"] = float(likes_text.lower().replace('k', '')) * 1000
                else:
                    stats["likes"] = float(likes_text)
            
            # 获取关注者数
            followers_button = soup.find("button", {"title": "Show DeepSeek's followers"})
            self.logger.info(f"followers_button ---->  {followers_button}")
            if followers_button:
                followers_text = followers_button.get_text(strip=True)
                self.logger.info(f"Found followers text: {followers_text}")
                # 转换数字格式（如 "50.6k" 转换为 50600）
                if 'k' in followers_text.lower():
                    stats["followers"] = float(followers_text.lower().replace('k', '')) * 1000
                else:
                    stats["followers"] = float(followers_text)
            
            self.logger.info(f"Final model stats: {stats}")
            return stats
        except Exception as e:
            self.logger.error(f"Error fetching repo stats for {url}: {e}")
            return {}

    def fetch_model_details(self, model_url):
        """获取模型详细信息"""
        try:
            response = self.session.get(model_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            details = {}
            
            # 获取 Introduction 部分
            intro_section = soup.find("h2", class_="relative group flex items-center")
            self.logger.info(f"Introduction section found: {intro_section}")
            
            if intro_section and "Introduction" in intro_section.get_text():
                intro_content = []
                current = intro_section.find_next_sibling()
                while current and not (current.name == "h2" and "Model Summary" in current.get_text()):
                    if current.name == "p":
                        text = current.get_text(strip=True)
                        if text:  # 只添加非空文本
                            intro_content.append(text)
                    current = current.find_next_sibling()
                
                if intro_content:
                    details["introduction"] = "\n".join(intro_content)
                    self.logger.info(f"Introduction content: {details['introduction']}")
                else:
                    self.logger.info("No introduction content found in paragraphs")
                    details["introduction"] = "Not found..."
            else:
                self.logger.info("Introduction section not found")
                details["introduction"] = "Not found..."
            
            # 添加日志输出以便调试
            self.logger.info(f"Fetched details for {model_url}:")
            
            
            
            return details
        except Exception as e:
            self.logger.error(f"Error fetching details for {model_url}: {e}")
            return {}

    def fetch(self):
        """抓取 Hugging Face Deepseek 模型的最新发布信息"""
        self.logger.info(f"Fetching data from {self.url}")
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching Hugging Face Models: {e}")
            return {"models": [], "model_stats": {}}  # 返回正确的数据结构

        soup = BeautifulSoup(response.text, "html.parser")
        models = []

        model_list = soup.find(id="models")
        if not model_list:
            self.logger.error("No model list found on the page")
            return {"models": [], "model_stats": {}}  # 返回模型统计信息

        for model_card in model_list.find_all("article", class_="overview-card-wrapper"):
            title_element = model_card.find("h4", class_="text-md")
            time_element = model_card.find("time")
            self.logger.info(f"Fetched title_element {title_element}，time_element {time_element}.")
            if title_element:
                title = title_element.text.strip()
                link = f"https://huggingface.co{model_card.find('a')['href']}"

                # 获取更新时间
                if time_element:
                    try:
                        time = time_element["datetime"]
                        time_obj = datetime.fromisoformat(time)  # 将 ISO 格式字符串转换为 datetime 对象
                    except ValueError as e:
                        self.logger.warning(f"Error parsing time for model '{title}': {e}")
                        time_obj = datetime.now()  # 如果时间格式不对，则使用当前时间
                else:
                    self.logger.info(f"No time found for model '{title}', setting default time as now.")
                    time_obj = datetime.now()  # 如果没有时间，则使用当前时间

                # 获取模型详细信息
                self.logger.info(f"Fetching details for model: {title}")
                details = self.fetch_model_details(link)
                
                # 获取仓库统计信息（点赞数和关注者数）
                self.logger.info(f"Fetching model stats for model: {title}")
                model_stats = self.fetch_model_stats(link)
                
                # 添加延迟以避免请求过快
                sleep(1)

                model_data = {
                    "title": title,
                    "link": link,
                    "time": time_obj,
                    "details": details,
                    "model_stats": model_stats
                }
                models.append(model_data)

        # 返回模型列表
        result = {
            "models": models
        }

        self.logger.info(f"Fetched {len(models)} models.")
        return result
        