# Web Proxy 代理功能详解

## 目录

- [什么是 Web Proxy 功能](#什么是-web-proxy-功能)
- [为什么需要 Web Proxy](#为什么需要-web-proxy)
- [基本使用方法](#基本使用方法)
- [与自定义 XPath 规则结合使用](#与自定义-xpath-规则结合使用)
- [完整示例](#完整示例)
- [参数说明](#参数说明)
- [URL 编码规则](#url-编码规则)
- [常见使用场景](#常见使用场景)
- [故障排除](#故障排除)
- [技术原理](#技术原理)

## 什么是 Web Proxy 功能

Web Proxy（网页代理）功能允许你通过第三方代理服务访问被封锁或无法直接访问的网站，同时确保 morss 正确处理从页面中提取的链接。

### 使用场景

- 目标网站在你的地区无法访问
- 需要通过代理服务器访问内容
- 使用在线网页代理工具（如 `sitedl.westpan.me`、`saha.qzz.io` 等）

### 解决的问题

当你使用网页代理访问网站时，提取的相对链接（如 `/article/123.html`）需要特殊处理。如果不使用 `web_proxy` 参数，morss 可能会错误地将链接解析为：
```
https://sitedl.westpan.me/article/123.html  ❌ 错误
```

而实际上应该是：
```
https://sitedl.westpan.me/123/https/target.com/article/123.html  ✅ 正确
```

`web_proxy` 参数就是为了解决这个问题。

## 为什么需要 Web Proxy

### 传统 URL 解析的问题

在标准的 RSS 订阅源中，morss 使用 Python 的 `urljoin()` 函数来解析相对链接：

```python
# 标准行为（没有 web_proxy 时）
feedurl = "http://target.com/feed"
relative_link = "/article/123.html"
结果 = urljoin(feedurl, relative_link)  
# → "http://target.com/article/123.html"
```

但是当使用网页代理时，这种标准解析会出错：

```python
# 使用代理时的问题
feedurl = "https://proxy.com/view/http://target.com/feed"
relative_link = "/article/123.html"
结果 = urljoin(feedurl, relative_link)
# → "https://proxy.com/article/123.html"  ❌ 错误！
# 应该是："https://proxy.com/view/http://target.com/article/123.html"
```

### Web Proxy 参数的解决方案

使用 `web_proxy` 参数，morss 会正确拼接代理前缀和相对链接：

```python
# 使用 web_proxy 参数
web_proxy = "https://proxy.com/view/http://target.com"
relative_link = "/article/123.html"
结果 = web_proxy + relative_link
# → "https://proxy.com/view/http://target.com/article/123.html"  ✅ 正确！
```

## 基本使用方法

### 命令行使用

```bash
morss \
  --web_proxy=https://proxy.com/view/http://target.com \
  https://target.com/feed.xml
```

### Web URL 使用

```
https://your-morss-instance.vercel.app/:web_proxy=PROXY_PREFIX/TARGET_URL
```

**重要**：在 URL 中，`/` 必须替换为 `|`（管道符）

```
https://your-morss-instance.vercel.app/:web_proxy=https:||proxy.com|view|http:||target.com/TARGET_URL
```

### 基本示例

假设你想通过 `sitedl.westpan.me` 代理访问 `t66y.com` 的内容：

```
https://your-morss.vercel.app/:web_proxy=https:||sitedl.westpan.me|123|https|t66y.com/https://t66y.com/feed.xml
```

## 与自定义 XPath 规则结合使用

`web_proxy` 参数可以与自定义 XPath 规则（`--items` 等）结合使用，为没有 RSS 订阅源的网站创建订阅，同时通过代理访问。

### 基本语法

```
https://morss.example.com/:参数1:参数2:web_proxy=代理前缀/目标网站URL
```

### 参数组合顺序

```
/:items=XPath规则:item_title=规则:item_link=规则:web_proxy=代理前缀:mode=html/目标URL
```

## 完整示例

### 示例 1：使用代理访问 misskon.com

这是根据你提供的 URL 改编的完整示例。

#### 目标

通过代理访问 `https://misskon.com/`，提取文章列表并创建 RSS 订阅源。

#### 网页结构

假设 `misskon.com` 的 HTML 结构如下：

```html
<div class="item-list">
    <div class="post">
        <h2><a href="/article/1">文章标题 1</a></h2>
        <p>文章摘要...</p>
    </div>
    <div class="post">
        <h2><a href="/article/2">文章标题 2</a></h2>
        <p>文章摘要...</p>
    </div>
</div>
```

#### XPath 规则

```bash
# CLI 命令格式
morss \
  --items="//div[@class='item-list']/*" \
  --item_title=".//h2/a" \
  --item_link=".//h2/a/@href" \
  --mode=html \
  --web_proxy=https://morss.saha.qzz.io/https/misskon.com \
  https://misskon.com/
```

#### Web URL 格式（已编码）

```
https://morss.saha.qzz.io/:items=%7C%7C*%5B%40class%3D%22item-list%22%5D:item_title=.%7C%7Ch2%7Ca:item_link=.%7C%7Ch2%7Ca%7C%40href:mode=html:web_proxy=https:%7C%7Cmorss.saha.qzz.io%7Chttps%7Cmisskon.com/https://misskon.com/
```

#### 解码后的 URL 结构

```
/:items=||*[@class="item-list"]
:item_title=.||h2|a
:item_link=.||h2|a|@href
:mode=html
:web_proxy=https:||morss.saha.qzz.io||https||misskon.com
/https://misskon.com/
```

#### 工作原理

1. **Morss 访问目标 URL**：`https://misskon.com/`（可能通过代理）
2. **使用 XPath 提取条目**：`//div[@class='item-list']/*` 找到所有文章
3. **提取标题**：`.//h2/a` 从每个条目中获取标题
4. **提取链接**：`.//h2/a/@href` 从每个条目中获取链接（可能是相对链接如 `/article/1`）
5. **应用 web_proxy**：
   - 如果链接是相对的（`/article/1`），拼接为：
     ```
     https://morss.saha.qzz.io/https/misskon.com/article/1
     ```
   - 如果链接是绝对的且来自目标域（`https://misskon.com/article/1`），转换为：
     ```
     https://morss.saha.qzz.io/https/misskon.com/article/1
     ```
   - 如果链接来自其他域（`https://example.com/page`），保持不变

### 示例 2：使用代理访问论坛

假设要通过 `sitedl.westpan.me` 代理访问某个论坛：

#### HTML 结构

```html
<div id="posts">
    <article class="thread">
        <h3><a href="/thread/123">讨论主题 1</a></h3>
        <span class="author">作者名</span>
        <span class="date">2024-01-15</span>
    </article>
</div>
```

#### CLI 命令

```bash
morss \
  --items="//article[@class='thread']" \
  --item_title="./h3/a" \
  --item_link="./h3/a/@href" \
  --item_time="./span[@class='date']" \
  --mode=html \
  --web_proxy=https://sitedl.westpan.me/123/https/forum.example.com \
  https://forum.example.com/
```

#### Web URL（URL 编码）

```
https://your-morss.vercel.app/:items=%7C%7Carticle%5B%40class%3D%27thread%27%5D:item_title=.%7Ch3%7Ca:item_link=.%7Ch3%7Ca%7C%40href:item_time=.%7Cspan%5B%40class%3D%27date%27%5D:mode=html:web_proxy=https:%7C%7Csitedl.westpan.me%7C123%7Chttps%7Cforum.example.com/https://forum.example.com/
```

#### 简化的 Web URL（使用管道符）

```
https://your-morss.vercel.app/:items=||article[@class='thread']:item_title=.|h3|a:item_link=.|h3|a|@href:item_time=.|span[@class='date']:mode=html:web_proxy=https:||sitedl.westpan.me|123|https|forum.example.com/https://forum.example.com/
```

注意：实际使用时仍需进行 URL 编码。

### 示例 3：简单的新闻列表

针对简单的新闻网站结构：

#### HTML 结构

```html
<ul class="news-list">
    <li>
        <a href="/news/1" class="title">新闻标题 1</a>
    </li>
    <li>
        <a href="/news/2" class="title">新闻标题 2</a>
    </li>
</ul>
```

#### CLI 命令

```bash
morss \
  --items="//ul[@class='news-list']/li" \
  --item_title=".//a[@class='title']" \
  --item_link=".//a[@class='title']/@href" \
  --mode=html \
  --web_proxy=https://proxy.example.com/http/news.example.com \
  https://news.example.com/
```

## 参数说明

### `web_proxy` 参数

指定网页代理的前缀 URL。morss 会将提取的相对链接拼接到这个前缀后面。

**格式**：
```
web_proxy=代理服务器URL/协议/目标网站域名
```

**常见代理模式**：

1. **模式 1**：完整 URL 路径
   ```
   https://proxy.com/view/http://target.com
   https://proxy.com/view/https://target.com
   ```

2. **模式 2**：协议和域名分离
   ```
   https://proxy.com/123/http/target.com
   https://proxy.com/123/https/target.com
   ```

### 与其他参数结合

`web_proxy` 可以与以下参数结合使用：

- `--items`：定义条目的 XPath 规则（必需）
- `--item_title`：标题提取规则
- `--item_link`：链接提取规则
- `--item_content`：内容提取规则
- `--item_time`：时间提取规则
- `--mode`：解析模式（html/xml/json）

### 参数顺序

参数可以按任意顺序排列，例如：

```
/:items=...:web_proxy=...:mode=html/URL
/:web_proxy=...:items=...:mode=html/URL
/:mode=html:items=...:web_proxy=.../URL
```

所有顺序都有效。

## URL 编码规则

### 为什么需要 URL 编码

在 Web URL 中传递参数时，特殊字符需要编码，因为它们在 URL 中有特殊含义。

### 编码对照表

| 字符 | URL 编码 | 说明 |
|------|----------|------|
| `/`  | `%2F` 或 `\|` | 斜杠（在参数值中使用管道符替代）|
| `:`  | `%3A` | 冒号 |
| `[`  | `%5B` | 左方括号 |
| `]`  | `%5D` | 右方括号 |
| `=`  | `%3D` | 等号（在 XPath 表达式中） |
| `"`  | `%22` | 双引号 |
| `'`  | `%27` | 单引号 |
| 空格 | `%20` | 空格 |
| `\|` | `%7C` | 管道符（如果不作为 `/` 的替代） |

### Morss 特殊规则：管道符替代

Morss 支持使用 `|`（管道符）替代 `/`（斜杠），这样可以避免 URL 路径解析问题。

**转换规则**：
```
/ → |
```

**示例**：
```
原始：//div[@class='post']
转换：||div[@class='post']
```

Morss 会自动将 `|` 转回 `/`。

### 编码示例

#### 原始命令

```bash
--items="//div[@class='post']"
--web_proxy=https://proxy.com/https/target.com
```

#### 转换为 URL

**步骤 1**：将 `/` 替换为 `|`

```
items=||div[@class='post']
web_proxy=https:||proxy.com|https|target.com
```

**步骤 2**：URL 编码特殊字符

```
items=%7C%7Cdiv%5B%40class%3D%27post%27%5D
web_proxy=https:%7C%7Cproxy.com%7Chttps%7Ctarget.com
```

**步骤 3**：组合完整 URL

```
https://morss.example.com/:items=%7C%7Cdiv%5B%40class%3D%27post%27%5D:web_proxy=https:%7C%7Cproxy.com%7Chttps%7Ctarget.com/https://target.com/
```

### 在线编码工具

你可以使用以下在线工具进行 URL 编码：

- [URL Encoder/Decoder](https://www.urlencoder.org/)
- [FreeFormatter URL Encoder](https://www.freeformatter.com/url-encoder.html)

### Python 编码脚本

如果你需要频繁编码，可以使用这个 Python 脚本：

```python
from urllib.parse import quote

# 原始 XPath
xpath = "//div[@class='post']"

# 替换 / 为 |
xpath_pipe = xpath.replace('/', '|')

# URL 编码
xpath_encoded = quote(xpath_pipe, safe='')

print(f"原始：{xpath}")
print(f"管道：{xpath_pipe}")
print(f"编码：{xpath_encoded}")
```

## 常见使用场景

### 场景 1：访问地区限制的网站

某些网站在特定地区不可用，可以通过代理访问：

```bash
morss \
  --web_proxy=https://proxy.com/view/http://blocked-site.com \
  http://blocked-site.com/feed.xml
```

### 场景 2：为没有 RSS 的代理网站创建订阅

目标网站没有 RSS，且需要通过代理访问：

```bash
morss \
  --items="//article[@class='post']" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --mode=html \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/
```

### 场景 3：确保图片和资源也通过代理加载

使用 `web_proxy` 后，不仅文章链接会通过代理，文章中的图片和其他资源（如果来自目标域）也会自动转换为代理 URL，确保可以正常加载。

## 故障排除

### 问题 1：链接无法访问

**症状**：生成的 RSS 订阅源中的链接无法打开。

**可能原因**：
1. `web_proxy` 参数格式不正确
2. URL 编码有误
3. 代理前缀不完整

**解决方案**：
1. 检查 `web_proxy` 参数是否包含完整的代理前缀
2. 确保 `/` 已替换为 `|`
3. 验证 URL 编码正确
4. 在浏览器中手动测试代理 URL 是否有效

**示例**：

错误的 `web_proxy`：
```
web_proxy=https://proxy.com
```

正确的 `web_proxy`：
```
web_proxy=https://proxy.com/https/target.com
```

### 问题 2：提取不到任何条目

**症状**：RSS 订阅源为空或只有基本信息。

**可能原因**：
1. XPath 规则不正确
2. 网站结构与预期不符
3. 代理返回的 HTML 结构与原网站不同

**解决方案**：
1. 首先不使用 `web_proxy`，测试 XPath 规则是否正确
2. 使用浏览器访问代理 URL，检查 HTML 结构
3. 使用 `DEBUG=1` 环境变量查看详细日志：
   ```bash
   DEBUG=1 morss --items="..." --web_proxy="..." https://target.com/
   ```

### 问题 3：相对链接解析错误

**症状**：生成的链接格式不正确，缺少代理前缀或路径错误。

**可能原因**：
1. 忘记添加 `web_proxy` 参数
2. `web_proxy` 前缀不完整（缺少目标域名）

**解决方案**：
1. 确保添加了 `web_proxy` 参数
2. 验证 `web_proxy` 包含完整路径，包括协议和域名
3. 检查提取的链接是否为相对链接（以 `/` 开头）

### 问题 4：URL 太长导致请求失败

**症状**：浏览器或服务器返回 414 错误（URL 太长）。

**可能原因**：
URL 参数过多或 XPath 表达式过长。

**解决方案**：
1. 简化 XPath 表达式
2. 使用 CLI 命令而非 Web URL
3. 在服务器端配置更大的 URL 长度限制

### 问题 5：无法获取完整内容

**症状**：RSS 订阅源中只有标题和链接，没有完整内容。

**说明**：
这是正常行为。默认情况下，morss 会：
1. 提取列表页的基本信息（标题、链接）
2. 访问每个链接获取完整内容

如果你希望直接从列表页提取摘要，使用 `--item_content` 参数：

```bash
morss \
  --items="//article" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --item_content="./p[@class='summary']" \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/
```

如果不想获取完整内容（只要列表信息），使用 `--proxy` 参数：

```bash
morss \
  --items="//article" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --proxy \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/
```

**注意**：`--proxy` 和 `--web_proxy` 是不同的参数：
- `--proxy`：不获取文章完整内容（原有功能）
- `--web_proxy`：指定网页代理前缀（新功能）

## 技术原理

### URL 解析逻辑

Morss 在处理链接时遵循以下逻辑：

#### 1. 没有 `web_proxy` 参数（标准行为）

```python
from urllib.parse import urljoin

feedurl = "http://target.com/feed"
item_link = "/article/123.html"

# 使用标准 urljoin
result = urljoin(feedurl, item_link)
# → "http://target.com/article/123.html"
```

#### 2. 使用 `web_proxy` 参数

**情况 A：相对链接**

```python
web_proxy = "https://proxy.com/https/target.com"
item_link = "/article/123.html"  # 相对链接（无协议）

# 拼接代理前缀
result = web_proxy.rstrip('/') + item_link
# → "https://proxy.com/https/target.com/article/123.html"
```

**情况 B：目标域的绝对链接**

```python
web_proxy = "https://proxy.com/https/target.com"
item_link = "https://target.com/article/123.html"  # 绝对链接（目标域）

# 提取目标域：https://target.com
target_base = extract_target_from_proxy(web_proxy)
# → "https://target.com"

# 检查链接是否以目标域开头
if item_link.startswith(target_base):
    # 提取路径部分
    path = item_link[len(target_base):]  # → "/article/123.html"
    # 拼接代理前缀
    result = web_proxy.rstrip('/') + path
    # → "https://proxy.com/https/target.com/article/123.html"
```

**情况 C：外部域的绝对链接**

```python
web_proxy = "https://proxy.com/https/target.com"
item_link = "https://example.com/page.html"  # 绝对链接（外部域）

# 不来自目标域，保持不变
result = item_link
# → "https://example.com/page.html"
```

### 代理前缀提取算法

Morss 使用 `extract_target_from_proxy()` 函数从代理 URL 中提取目标网站：

```python
def extract_target_from_proxy(web_proxy):
    """
    从代理 URL 中提取目标网站的基础 URL
    
    示例：
    'https://proxy.com/https/target.com' -> 'https://target.com'
    'https://proxy.com/view/http://target.com' -> 'http://target.com'
    """
    # 模式 1：查找 /http:// 或 /https://
    for protocol in ['https://', 'http://']:
        search_str = '/' + protocol
        idx = web_proxy.rfind(search_str)
        if idx != -1:
            return web_proxy[idx + 1:]  # 提取完整 URL
    
    # 模式 2：查找 /http/ 或 /https/ 分离模式
    parts = web_proxy.split('/')
    for i, part in enumerate(parts[3:], start=3):
        if part in ('http', 'https'):
            if i + 1 < len(parts):
                protocol = part
                domain = parts[i + 1]
                return f"{protocol}://{domain}"
    
    return None
```

### 支持的代理 URL 模式

Morss 支持两种常见的代理 URL 模式：

**模式 1：完整 URL 路径**（最常见）
```
https://proxy.com/view/http://target.com
https://proxy.com/view/https://target.com
```

**模式 2：协议和域名分离**
```
https://proxy.com/123/http/target.com
https://proxy.com/123/https/target.com
```

这两种模式都能被正确识别和处理。

### 与标准 URL 解析的区别

| 特性 | 标准解析（无 `web_proxy`） | Web Proxy 解析（有 `web_proxy`） |
|------|---------------------------|----------------------------------|
| 相对链接 | 使用 `urljoin(feedurl, link)` | 拼接 `web_proxy + link` |
| 目标域绝对链接 | 保持不变 | 转换为代理 URL |
| 外部域绝对链接 | 保持不变 | 保持不变 |
| 适用场景 | 直接访问网站 | 通过代理访问网站 |

## 进阶技巧

### 1. 调试 XPath 和 web_proxy

建议分步测试：

**步骤 1**：测试不带 `web_proxy` 的 XPath 规则

```bash
morss \
  --items="//div[@class='post']" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --mode=html \
  https://target.com/
```

**步骤 2**：确认 XPath 正确后，添加 `web_proxy`

```bash
morss \
  --items="//div[@class='post']" \
  --item_title="./h2" \
  --item_link="./a/@href" \
  --mode=html \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/
```

### 2. 使用环境变量启用详细日志

```bash
DEBUG=1 morss --web_proxy=... --items=... https://target.com/
```

这会显示：
- 提取的条目数量
- 每个条目的链接
- URL 解析结果

### 3. 生成不同格式的输出

```bash
# JSON 格式
morss --format=json --web_proxy=... --items=... https://target.com/

# CSV 格式
morss --format=csv --web_proxy=... --items=... https://target.com/

# HTML 格式
morss --format=html --web_proxy=... --items=... https://target.com/
```

### 4. 限制获取的条目数量

使用环境变量控制性能：

```bash
# 最多获取 5 篇文章的完整内容
MAX_ITEM=5 morss --web_proxy=... --items=... https://target.com/

# 最多处理 10 个条目
LIM_ITEM=10 morss --web_proxy=... --items=... https://target.com/
```

### 5. 保存生成的 RSS 到文件

```bash
morss --web_proxy=... --items=... https://target.com/ > output.xml
```

## 与其他 Morss 功能的配合

### 配合 `--clip` 参数

将完整内容追加到原始摘要后：

```bash
morss \
  --clip \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/feed.xml
```

### 配合 `--search` 参数

过滤包含特定关键词的条目：

```bash
morss \
  --search="关键词" \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/feed.xml
```

### 配合 `--resolve` 参数

解析跟踪链接为直接链接：

```bash
morss \
  --resolve \
  --web_proxy=https://proxy.com/https/target.com \
  https://target.com/feed.xml
```

## 总结

### 关键要点

1. ✅ **`web_proxy` 解决代理访问时的链接解析问题**
2. ✅ **相对链接会拼接代理前缀**
3. ✅ **目标域的绝对链接会转换为代理 URL**
4. ✅ **外部域的绝对链接保持不变**
5. ✅ **可与自定义 XPath 规则结合使用**
6. ✅ **在 Web URL 中，`/` 必须替换为 `|`**

### 使用流程

1. 确定目标网站和代理服务
2. 编写 XPath 规则（如需自定义）
3. 构造 `web_proxy` 参数
4. 测试 CLI 命令
5. 转换为 Web URL（替换 `/` 为 `|`，URL 编码）
6. 添加到 RSS 阅读器

### 最佳实践

- 先用 CLI 命令测试，确认无误后再转换为 Web URL
- 分步调试：先测试 XPath，再添加 `web_proxy`
- 使用 `DEBUG=1` 查看详细日志
- 保存成功的配置供以后使用
- 定期检查代理服务是否仍然有效

## 相关文档

- **[XPATH_CUSTOM_FEEDS_CN.md](XPATH_CUSTOM_FEEDS_CN.md)** - XPath 自定义规则详解
- **[WEB_PROXY_FEATURE.md](WEB_PROXY_FEATURE.md)** - Web Proxy 功能技术文档（英文）
- **[README.md](README.md)** - Morss 项目主文档

## 获取帮助

如果遇到问题：

1. 查看 [故障排除](#故障排除) 部分
2. 使用 `DEBUG=1` 启用详细日志
3. 在 [GitHub Issues](https://github.com/YeWeihong/morss-vercel/issues) 提问
4. 参考其他文档了解 XPath 和 Morss 的其他功能

---

**最后更新**：2024-01

**文档版本**：1.0

希望这份文档能帮助你成功使用 Web Proxy 功能！🎉
