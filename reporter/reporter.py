import json
import os

class JSONReporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # 确保目录存在

    def save_json_report(self, data, filename="huggingface_articles.json"):
        """将数据存储到 JSON 文件"""
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Report saved: {file_path}")
