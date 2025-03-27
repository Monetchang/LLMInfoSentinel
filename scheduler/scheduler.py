import schedule
import time
import json
import os
from datetime import datetime
import logging
from typing import Dict, List
from fetcher.fetcher import HuggingFaceModelFetcher

class ModelScheduler:
    def __init__(self, config_path="config/config.json"):
        self.logger = self.setup_logger()
        self.config_path = config_path
        self.models_file = "data/models.json"
        self.fetcher = HuggingFaceModelFetcher(config_path)
        
    def setup_logger(self):
        """设置日志记录"""
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def load_existing_models(self) -> Dict[str, dict]:
        """加载现有的模型数据"""
        if os.path.exists(self.models_file):
            with open(self.models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"models": []}

    def save_models(self, models_data: dict):
        """保存模型数据到文件"""
        os.makedirs(os.path.dirname(self.models_file), exist_ok=True)
        with open(self.models_file, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, indent=2, ensure_ascii=False, default=str)

    def compare_models(self, existing_models: List[dict], new_models: List[dict]) -> List[dict]:
        """比较现有模型和新模型，返回新增的模型"""
        existing_titles = {model['title'] for model in existing_models}
        new_models_list = []
        
        for model in new_models:
            if model['title'] not in existing_titles:
                new_models_list.append(model)
        
        return new_models_list

    def notify_new_models(self, new_models: List[dict]):
        """通知新增的模型"""
        if new_models:
            self.logger.info("\n=== New Models Found ===")
            for model in new_models:
                self.logger.info(f"\nTitle: {model['title']}")
                self.logger.info(f"Link: {model['link']}")
                self.logger.info(f"Time: {model['time']}")
                if model.get('model_stats'):
                    self.logger.info(f"Likes: {model['model_stats'].get('likes', 'N/A')}")
                    self.logger.info(f"Followers: {model['model_stats'].get('followers', 'N/A')}")
            self.logger.info("\n=====================\n")
        else:
            self.logger.info("No new models found.")

    def check_new_models(self):
        """检查新模型的主函数"""
        self.logger.info("Starting model check...")
        
        # 加载现有模型数据
        existing_data = self.load_existing_models()
        existing_models = existing_data.get("models", [])
        
        # 获取新模型数据
        new_data = self.fetcher.fetch()
        new_models = new_data.get("models", [])
        
        # 比较并找出新模型
        new_models_list = self.compare_models(existing_models, new_models)
        
        # 通知新模型
        self.notify_new_models(new_models_list)
        
        # 保存新的模型数据
        self.save_models(new_data)
        
        self.logger.info("Model check completed.")

    def run(self):
        """运行调度器"""
        self.logger.info("Starting scheduler...")
        
        # 设置每天执行一次
        schedule.every().day.at("00:00").do(self.check_new_models)
        
        # 立即执行一次检查
        self.check_new_models()
        
        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = ModelScheduler()
    scheduler.run()
