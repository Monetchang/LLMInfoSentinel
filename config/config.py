import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.config_data = self.load_config()

    def load_config(self):
        """加载 JSON 配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件未找到: {self.config_file}")

        with open(self.config_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_subscriptions(self):
        return self.config_data.get("subscriptions", [])

    def get_login_info(self):
        return self.config_data.get("login", {})
