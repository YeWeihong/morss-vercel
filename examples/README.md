# Morss 使用示例

本目录包含 morss 各种功能的示例代码。

## 可用示例

### web_proxy_example.py

演示如何使用 `web_proxy` 功能通过代理访问网站。

**运行方法**：

```bash
# 从项目根目录运行
PYTHONPATH=. python3 examples/web_proxy_example.py
```

**包含的示例**：

1. 基本的 URL 拼接
2. 从代理 URL 中提取目标网站
3. 处理不同类型的链接（相对链接、目标域绝对链接、外部域绝对链接）
4. URL 编码转换示例
5. 使用 Options 对象配置

**相关文档**：
- [WEB_PROXY_FEATURE_CN.md](../WEB_PROXY_FEATURE_CN.md) - Web Proxy 功能详细文档（中文）
- [WEB_PROXY_FEATURE.md](../WEB_PROXY_FEATURE.md) - Web Proxy feature documentation (English)

## 添加新示例

欢迎贡献更多示例！新示例应该：

1. 有清晰的注释和文档字符串
2. 包含多个使用场景
3. 易于运行和理解
4. 在文件头部说明功能和用法

## 其他资源

- [XPATH_CUSTOM_FEEDS_CN.md](../XPATH_CUSTOM_FEEDS_CN.md) - XPath 自定义规则详解
- [README.md](../README.md) - Morss 项目主文档
