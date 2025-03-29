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
    def __init__(self, config):
        self.logger = self.setup_logger()
        if isinstance(config, str):
            self.config = self.load_config(config)
        else:
            self.config = config
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
        # 加载本地模型数据
        self.existing_models = self.load_existing_models()

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

    def fetch_model_info(self, model_url, fetch_introduction=False):
        """获取模型的所有信息（包括统计信息和详细信息）
        Args:
            model_url: 模型页面的URL
            fetch_introduction: 是否获取Introduction部分，默认为False
        """
        try:
            response = self.session.get(model_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            model_info = {}
            
            # 获取统计信息
            stats = {}
            # 获取点赞数
            likes_button = soup.find("button", {"title": "See users who liked this repository"})
            if likes_button:
                likes_text = likes_button.get_text(strip=True)
                self.logger.info(f"Found likes text: {likes_text}")
                stats["likes"] = likes_text
            
            # 获取关注者数
            followers_button = soup.find("button", {"title": "Show DeepSeek's followers"})
            if followers_button:
                followers_text = followers_button.get_text(strip=True)
                self.logger.info(f"Found followers text: {followers_text}")
                stats["followers"] = followers_text
            
            model_info["model_stats"] = stats
            
            # 只在需要时获取 Introduction 部分
            if fetch_introduction:
                model_info["introduction"] = self.fetch_model_introduction(soup)
            else:
                model_info["introduction"] = "Not fetched"
            
            # 添加日志输出以便调试
            self.logger.info(f"Fetched info for {model_url} (introduction: {'fetched' if fetch_introduction else 'skipped'})")
            
            return model_info
        except Exception as e:
            self.logger.error(f"Error fetching info for {model_url}: {e}")
            return {"introduction": "Error fetching details", "model_stats": {}}

    def fetch_model_introduction(self, soup):
        """获取模型的Introduction部分
        Args:
            soup: BeautifulSoup对象，包含模型页面的HTML内容
        Returns:
            str: 模型的Introduction内容，如果未找到则返回"Not found..."
        """
        try:
            intro_section = soup.find("h2", class_="relative group flex items-center")
            
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
                    introduction = "\n".join(intro_content)
                    self.logger.info(f"Introduction content: {introduction}")
                    return introduction
                else:
                    self.logger.info("No introduction content found in paragraphs")
                    return "Not found..."
            else:
                self.logger.info("Introduction section not found")
                return "Not found..."
        except Exception as e:
            self.logger.error(f"Error fetching introduction: {e}")
            return "Error fetching introduction"

    def expand_models(self, models_div, subscription_url):
        """
        Find expand button, click it to load more models, then process all model articles.
        """
        try:
            # 使用 Selenium 打开页面
            self.driver.get(subscription_url)
            
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
            
            # 点击按钮前等待一下
            sleep(2)
            
            # 点击按钮
            expand_button.click()
            
            # 等待更长时间让新内容加载
            sleep(5)
            
            # 等待新内容加载，确保在 models_div 内
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#models article.group\\/repo")))
            
            # 只在 models_div 内获取所有模型文章
            model_articles = models_div.find_elements(By.CSS_SELECTOR, "article.group\\/repo")
            self.logger.info(f"Found {len(model_articles)} model articles in models_div")
            
            return model_articles
                
        except Exception as e:
            self.logger.error(f"Error in expand_models: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []

    def load_existing_models(self):
        """加载本地存储的模型数据"""
        try:
            if os.path.exists("data/models.json"):
                with open("data/models.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 返回按订阅源组织的模型数据
                    return data.get("subscriptions", {})
            return {}
        except Exception as e:
            self.logger.error(f"Error loading existing models: {str(e)}")
            return {}

    def fetch(self, fetch_introduction=False):
        """获取所有订阅源的模型列表
        Args:
            fetch_introduction: 是否获取Introduction部分，默认为False
        """
        max_retries = 3
        retry_delay = 5  # seconds
        
        try:
            all_models = {}
            
            # 遍历所有订阅源
            for subscription in self.config.get("subscriptions", []):
                subscription_name = subscription.get("name")
                subscription_url = subscription.get("url")
                
                if not subscription_name or not subscription_url:
                    self.logger.error(f"Invalid subscription configuration: {subscription}")
                    continue
                
                self.logger.info(f"Processing subscription: {subscription_name}")
                
                # 获取该订阅源的现有模型
                existing_subscription_models = self.existing_models.get(subscription_name, {})
                
                try:
                    for attempt in range(max_retries):
                        try:
                            response = requests.get(subscription_url, headers=self.headers)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # 首先找到 id 为 "models" 的 div
                            models_div = soup.find("div", id="models")
                            if not models_div:
                                self.logger.error(f"Could not find div with id='models' for {subscription_name}")
                                continue
                            
                            # 处理所有模型
                            model_articles = self.expand_models(models_div, subscription_url)
                            subscription_models = []
                            new_models = []
                            
                            for article in model_articles:
                                try:
                                    # 获取标题和链接
                                    title_element = article.find_element(By.CSS_SELECTOR, "h4.text-md.truncate.font-mono")
                                    title = title_element.text.strip()
                                    link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                                    
                                    # 检查是否是新增模型
                                    if title not in existing_subscription_models:
                                        self.logger.info(f"Found new model in {subscription_name}: {title}")
                                        # 获取模型所有信息
                                        model_info = self.fetch_model_info(link, fetch_introduction)
                                        model_info["title"] = title
                                        model_info["link"] = link
                                        model_info["subscription"] = subscription_name
                                        
                                        # 添加较长的延迟以避免请求过快
                                        sleep(3)  # 增加到3秒
                                        
                                        new_models.append(model_info)
                                    else:
                                        # 使用本地存储的模型数据
                                        subscription_models.append(existing_subscription_models[title])
                                    
                                except Exception as e:
                                    self.logger.error(f"Error processing model article in {subscription_name}: {str(e)}")
                                    continue
                            
                            # 合并新旧模型数据
                            subscription_models.extend(new_models)
                            
                            # 更新该订阅源的模型数据
                            all_models[subscription_name] = {
                                model["title"]: model for model in subscription_models
                            }
                            
                            # 打印新增模型数量
                            if new_models:
                                self.logger.info(f"Found {len(new_models)} new models in {subscription_name}")
                            else:
                                self.logger.info(f"No new models found in {subscription_name}")
                            
                            break  # 成功获取数据，跳出重试循环
                            
                        except Exception as e:
                            self.logger.error(f"Error fetching data for {subscription_name} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                            if attempt < max_retries - 1:
                                sleep(retry_delay)
                            else:
                                self.logger.error(f"Max retries reached for {subscription_name}. Giving up.")
                
                except Exception as e:
                    self.logger.error(f"Error processing subscription {subscription_name}: {str(e)}")
                    continue
            
            # 更新本地存储的模型数据
            with open("data/models.json", "w", encoding="utf-8") as f:
                json.dump({"subscriptions": all_models}, f, indent=2, ensure_ascii=False)
            
            return {"subscriptions": all_models}
            
        finally:
            # 在所有操作完成后关闭浏览器
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")
        