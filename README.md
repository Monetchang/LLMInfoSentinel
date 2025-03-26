# LLMInfoSentinel

LLMInfoSentinel 是一个用于监控和收集 LLM 模型信息的工具，目前支持从 Hugging Face 抓取 Deepseek 模型的最新信息。

## 功能特点

- 自动抓取 Hugging Face Deepseek 模型信息
- 获取模型详细信息（描述、标签、大小、许可证、下载次数等）
- 支持订阅管理
- 数据保存为 JSON 格式
- 完善的日志记录系统

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/LLMInfoSentinel.git
cd LLMInfoSentinel
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

直接运行主程序：
```bash
python main.py
```

### 订阅管理

添加新的订阅源：
```bash
python main.py --add-subscription --name "订阅名称" --url "订阅URL"
```

删除订阅源：
```bash
python main.py --remove-subscription --name "订阅名称"
```

列出所有订阅源：
```bash
python main.py --list-subscriptions
```

## 配置文件

配置文件位于 `config/config.json`，包含以下内容：
```json
{
    "subscriptions": [
        {
            "name": "Hugging Face Models - Deepseek",
            "url": "https://huggingface.co/deepseek-ai",
            "type": "html"
        }
    ],
    "notifications": {
        "method": "email",
        "email": "your-email@example.com"
    }
}
```

## 输出数据

抓取的数据将保存在 `data/models.json` 文件中，格式如下：
```json
[
    {
        "title": "模型名称",
        "link": "模型链接",
        "time": "更新时间",
        "details": {
            "description": "模型描述",
            "tags": ["标签1", "标签2", ...],
            "size": "模型大小",
            "license": "许可证信息",
            "downloads": "下载次数"
        }
    }
]
```

## 开发计划

- [ ] 支持更多模型源
- [ ] 添加数据分析和可视化功能
- [ ] 实现邮件通知功能
- [ ] 添加定时任务支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
