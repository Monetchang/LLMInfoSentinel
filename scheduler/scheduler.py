import time
from fetcher.fetcher import Fetcher
from analyzer.analyzer import Analyzer
from notifier.notifier import Notifier
from reporter.reporter import Reporter

class Scheduler:
    def __init__(self, config):
        self.config = config
        self.fetcher = Fetcher(config.get_subscriptions())
        self.analyzer = Analyzer()
        self.notifier = Notifier(config.get_notification_settings())
        self.reporter = Reporter()

    def run(self):
        while True:
            # 每天抓取数据
            self.fetcher.fetch_data()
            # 分析数据
            updates = self.analyzer.analyze(data)
            # 生成报告
            report = self.reporter.generate_report(updates)
            # 发送通知
            self.notifier.send_notification("LLM Updates", report)
            time.sleep(86400)  # 每24小时执行一次
