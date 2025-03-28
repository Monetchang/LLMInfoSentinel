import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import logging
from time import sleep
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class HuggingFaceModelFetcher:
    def __init__(self, config_path="config/config.json"):
        self.logger = self.setup_logger()
        self.config = self.load_config(config_path)
        self.url = self.config["subscriptions"][0]["url"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()
        # 初始化 Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

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
                stats["likes"] = likes_text
            
            # 获取关注者数
            followers_button = soup.find("button", {"title": "Show DeepSeek's followers"})
            self.logger.info(f"followers_button ---->  {followers_button}")
            if followers_button:
                followers_text = followers_button.get_text(strip=True)
                self.logger.info(f"Found followers text: {followers_text}")
                stats["followers"] = followers_text
            
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

    def expand_models(self, models_div):
        """
        Find expand button, click it to load more models, then process all model articles.
        """
        try:
            # 使用 Selenium 打开页面
            self.driver.get(self.url)
            
            # 等待页面加载完成，使用更精确的选择器
            models_div = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#models"))
            )
            
            # 使用更精确的选择器查找展开按钮
            expand_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    "div#models button.mx-2.flex.h-8.flex-none.items-center.rounded-lg.px-2\\.5.font-medium.text-gray-800"
                ))
            )
            
            # 获取按钮文本
            button_text = expand_button.text.replace('\n', ' ').strip()
            self.logger.info(f"Found expand button with text: '{button_text}'")
            
            # 点击按钮前等待一下
            sleep(2)
            
            # 点击按钮
            expand_button.click()
            
            # 等待更长时间让新内容加载
            sleep(5)
            
            # 等待新内容加载
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.group\\/repo")))
            
            # 获取所有模型文章
            model_articles = self.driver.find_elements(By.CSS_SELECTOR, "article.group\\/repo")
            self.logger.info(f"Found {len(model_articles)} model articles")
            
            # 打印每个文章的标题，用于调试
            for article in model_articles:
                try:
                    title_element = article.find_element(By.CSS_SELECTOR, "h4.text-md.truncate.font-mono")
                    title = title_element.text.strip()
                    self.logger.info(f"Article title: {title}")
                except Exception as e:
                    self.logger.error(f"Error getting article title: {str(e)}")
            
            return model_articles
                
        except Exception as e:
            self.logger.error(f"Error in expand_models: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []

    def fetch(self):
        """获取模型列表"""
        max_retries = 3
        retry_delay = 5  # seconds
        
        try:
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Fetching data from {self.url} (attempt {attempt + 1}/{max_retries})")
                    response = requests.get(self.url, headers=self.headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 首先找到 id 为 "models" 的 div
                    models_div = soup.find("div", id="models")
                    if not models_div:
                        self.logger.error("Could not find div with id='models'")
                        return {"models": []}
                    
                    # 处理所有模型
                    model_articles = self.expand_models(models_div)
                    models = []
                    
                    for article in model_articles:
                        try:
                            # 获取标题和链接
                            title_element = article.find_element(By.CSS_SELECTOR, "h4.text-md.truncate.font-mono")
                            title = title_element.text.strip()
                            link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                            
                            self.logger.info(f"Processing model: {title}")
                            
                            # 获取模型详情
                            model_details = self.fetch_model_details(link)
                            model_details["title"] = title
                            model_details["link"] = link
                            
                            # 获取模型统计信息
                            model_stats = self.fetch_model_stats(link)
                            model_details["model_stats"] = model_stats
                            
                            models.append(model_details)
                            
                            # 添加较长的延迟以避免请求过快
                            sleep(3)  # 增加到3秒
                            
                        except Exception as e:
                            self.logger.error(f"Error processing model article: {str(e)}")
                            continue
                    
                    self.logger.info(f"Fetched {len(models)} models.")
                    return {"models": models}
                    
                except Exception as e:
                    self.logger.error(f"Error fetching data (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        self.logger.info(f"Retrying in {retry_delay} seconds...")
                        sleep(retry_delay)
                    else:
                        self.logger.error("Max retries reached. Giving up.")
                        return {"models": []}
        finally:
            # 在所有操作完成后关闭浏览器
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")
        