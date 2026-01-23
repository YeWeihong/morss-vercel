# Web Proxy 快速参考指南

这是一份快速参考指南，帮助你快速上手使用 morss 的 Web Proxy 功能。

> 📖 **完整文档**: [WEB_PROXY_FEATURE_CN.md](WEB_PROXY_FEATURE_CN.md)

## 🎯 核心概念

`web_proxy` 参数让你能够通过第三方代理服务访问网站，同时确保提取的链接正确拼接代理前缀。

## ⚡ 快速开始

### 1. 基本用法（CLI）

```bash
morss \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/feed.xml
```

### 2. 与自定义 XPath 结合（CLI）

```bash
morss \
  --items="//article[@class='post']" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --mode=html \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/
```

### 3. Web URL 格式

```
https://your-morss.vercel.app/:web_proxy=代理前缀/目标URL
```

**重要**: 在 URL 中，`/` 必须替换为 `|`

```
https://your-morss.vercel.app/:web_proxy=https:||proxy.com|https|target.com/https://target.com/
```

## 📋 URL 编码速查表

| 原始字符 | 替换为 |
|---------|--------|
| `/`     | `\|`    |
| `[`     | `%5B`  |
| `]`     | `%5D`  |
| `=`     | `%3D`  |
| `"`     | `%22`  |
| `'`     | `%27`  |
| 空格    | `%20`  |

## 💡 实际示例

### 示例 1: 通过代理访问 misskon.com

**CLI 命令**:
```bash
morss \
  --items="//div[@class='item-list']/*" \
  --item_title=".//h2/a" \
  --item_link=".//h2/a/@href" \
  --mode=html \
  --web_proxy=https://morss.saha.qzz.io/https/misskon.com \
  https://misskon.com/
```

**Web URL** (URL 编码):
```
https://morss.saha.qzz.io/:items=%7C%7C*%5B%40class%3D%22item-list%22%5D:item_title=.%7C%7Ch2%7Ca:item_link=.%7C%7Ch2%7Ca%7C%40href:mode=html:web_proxy=https:%7C%7Cmorss.saha.qzz.io%7Chttps%7Cmisskon.com/https://misskon.com/
```

### 示例 2: 简单的代理访问

**原始 URL**: `https://target.com/feed.xml`
**代理服务**: `https://proxy.com/https/target.com`

**Morss 命令**:
```bash
morss --web_proxy=https://proxy.com/https/target.com https://target.com/feed.xml
```

**Web URL**:
```
https://your-morss.vercel.app/:web_proxy=https:||proxy.com|https|target.com/https://target.com/feed.xml
```

## 🔧 常见问题速查

### 问题：链接无法访问
✅ **检查**: `web_proxy` 参数是否包含完整的代理前缀（包括协议和目标域名）

### 问题：提取不到内容
✅ **检查**: XPath 规则是否正确
✅ **方法**: 先不使用 `web_proxy` 测试 XPath，确认无误后再添加

### 问题：URL 编码错误
✅ **检查**: 是否将 `/` 替换为 `|`
✅ **检查**: 是否对特殊字符进行了 URL 编码

### 问题：只有标题没有内容
✅ **说明**: 这是正常行为，morss 会访问链接获取完整内容
✅ **选项**: 使用 `--item_content` 从列表页提取摘要
✅ **选项**: 使用 `--proxy` 参数不获取完整内容

## 🚀 调试技巧

### 1. 启用调试日志
```bash
DEBUG=1 morss --web_proxy=... --items=... https://target.com/
```

### 2. 分步测试
```bash
# 步骤 1: 测试 XPath（不带 web_proxy）
morss --items="//article" --mode=html https://target.com/

# 步骤 2: 添加 web_proxy
morss --items="//article" --mode=html --web_proxy=... https://target.com/
```

### 3. 验证代理 URL
在浏览器中手动访问代理 URL，确认可以正常访问。

## 📚 相关文档

- **[WEB_PROXY_FEATURE_CN.md](WEB_PROXY_FEATURE_CN.md)** - 完整详细文档
- **[XPATH_CUSTOM_FEEDS_CN.md](XPATH_CUSTOM_FEEDS_CN.md)** - XPath 自定义规则详解
- **[examples/web_proxy_example.py](examples/web_proxy_example.py)** - 可运行的示例脚本

## 🔗 支持的代理 URL 模式

### 模式 1: 完整 URL 路径
```
https://proxy.com/view/http://target.com
https://proxy.com/view/https://target.com
```

### 模式 2: 协议和域名分离
```
https://proxy.com/123/http/target.com
https://proxy.com/123/https/target.com
```

两种模式都能正确识别和处理。

## 💻 Python 代码示例

```python
from morss.morss import Options, web_proxy_join, extract_target_from_proxy

# 创建配置
options = Options(
    web_proxy="https://proxy.com/https/target.com",
    items="//article[@class='post']",
    mode="html"
)

# URL 拼接
result = web_proxy_join("https://proxy.com/https/target.com", "/article/123")
# → "https://proxy.com/https/target.com/article/123"

# 提取目标域
target = extract_target_from_proxy("https://proxy.com/https/target.com")
# → "https://target.com"
```

## 🎓 学习路径

1. ✅ 阅读本快速指南了解基本概念
2. ✅ 运行示例脚本: `PYTHONPATH=. python3 examples/web_proxy_example.py`
3. ✅ 尝试简单的 CLI 命令
4. ✅ 学习 URL 编码规则
5. ✅ 构造自己的 Web URL
6. ✅ 阅读完整文档了解高级功能

---

**最后更新**: 2024-01
**版本**: 1.0

如有问题，请参考 [完整文档](WEB_PROXY_FEATURE_CN.md) 或在 [GitHub Issues](https://github.com/YeWeihong/morss-vercel/issues) 提问。
