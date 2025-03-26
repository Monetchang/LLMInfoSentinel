# Changelog

## [1.0.0] - 2024-03-24

### Added
- 初始版本发布
- 支持从 Hugging Face 抓取 Deepseek 模型信息
- 支持获取模型详细信息，包括：
  - 模型描述
  - 模型标签
  - 模型大小
  - 许可证信息
  - 下载次数
- 支持订阅管理功能：
  - 添加订阅源
  - 删除订阅源
  - 列出所有订阅源
- 支持将抓取的数据保存为 JSON 格式

### Changed
- 优化了日志记录系统
- 使用 requests.Session 提高请求效率
- 添加请求延迟以避免访问过快

### Fixed
- 修复了 datetime 对象 JSON 序列化问题
- 修复了 time.sleep 导入问题

### Technical Details
- 使用 BeautifulSoup4 进行网页解析
- 实现了优雅的错误处理机制
- 支持配置文件管理 