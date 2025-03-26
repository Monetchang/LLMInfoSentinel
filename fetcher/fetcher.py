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

    def fetch_model_details(self, model_url):
        """获取模型详细信息"""
        try:
            response = self.session.get(model_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            details = {}
            
            # 获取模型描述
            description_elem = soup.find("div", class_="prose")
            if description_elem:
                details["description"] = description_elem.get_text(strip=True)
            
            # 获取模型标签
            tags_elem = soup.find("div", class_="flex flex-wrap gap-2")
            if tags_elem:
                details["tags"] = [tag.get_text(strip=True) for tag in tags_elem.find_all("span")]
            
            # 获取模型大小
            size_elem = soup.find("div", string=lambda text: text and "Size" in text)
            if size_elem:
                details["size"] = size_elem.get_text(strip=True)
            
            # 获取许可证信息
            license_elem = soup.find("div", string=lambda text: text and "License" in text)
            if license_elem:
                details["license"] = license_elem.get_text(strip=True)
            
            # 获取下载次数
            downloads_elem = soup.find("div", string=lambda text: text and "Downloads" in text)
            if downloads_elem:
                details["downloads"] = downloads_elem.get_text(strip=True)
            
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
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        models = []

        model_list = soup.find(id="models")
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
                
                # 添加延迟以避免请求过快
                sleep(1)  # 使用导入的 sleep 函数

                model_data = {
                    "title": title,
                    "link": link,
                    "time": time_obj,
                    "details": details
                }
                models.append(model_data)

        self.logger.info(f"Fetched {len(models)} models.")
        return models
        