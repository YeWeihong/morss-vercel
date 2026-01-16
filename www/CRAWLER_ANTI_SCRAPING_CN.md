# Morss 爬虫机制与反爬策略详解

## HTTP 请求库说明

### 为什么不使用 requests 库？

Morss 项目使用 Python 标准库中的 `urllib`/`urllib2`（Python 2）或 `urllib.request`（Python 3）来进行 HTTP 请求，**而不是 requests 库**。这样做的原因是：

1. **减少外部依赖**：urllib 是 Python 标准库的一部分，无需额外安装
2. **轻量级部署**：减小 Docker 镜像大小，加快安装速度
3. **足够的功能**：urllib 提供了 Morss 所需的所有 HTTP 功能
4. **更好的控制**：可以更底层地控制 HTTP 请求细节

### 核心实现位置

HTTP 请求处理的核心代码在 `morss/crawler.py` 文件中：

```python
# Python 2/3 兼容性导入
try:
    # python 2
    from urllib2 import (BaseHandler, HTTPCookieProcessor, HTTPRedirectHandler,
                         Request, addinfourl, build_opener, parse_http_list,
                         parse_keqv_list)
except ImportError:
    # python 3
    from urllib.request import (BaseHandler, HTTPCookieProcessor,
                                HTTPRedirectHandler, Request, addinfourl,
                                build_opener, parse_http_list, parse_keqv_list)
```

### 主要函数

- `get(url, **kwargs)` - 简单的 GET 请求
- `adv_get(url, post=None, timeout=None, **kwargs)` - 高级请求，返回详细信息
- `custom_opener(**kwargs)` - 创建自定义的 URL opener

## 反爬机制与应对策略

### 1. User-Agent 轮换

**问题**：许多网站会检查 User-Agent，拒绝或限制没有合法 User-Agent 的请求。

**Morss 的解决方案**：

```python
# 在 crawler.py 中定义了多个真实的 User-Agent
DEFAULT_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    # ... 更多真实的浏览器 User-Agent
]

# 每次请求随机选择一个 User-Agent
ua = random.choice(DEFAULT_UAS)
```

**如何使用**：
```bash
# 默认会自动轮换
morss http://example.com/feed.xml

# 也可以指定自定义 User-Agent
morss --user-agent="Mozilla/5.0 Custom" http://example.com/feed.xml
```

**实现细节**：
- 使用 `random.choice()` 随机选择 User-Agent
- 模拟真实浏览器，包括 Chrome、Firefox、Safari 等
- 包含完整的系统信息和浏览器版本号

### 2. HTTP 重定向处理

**问题**：网站可能使用 301/302 重定向进行跟踪或防止直接访问。

**Morss 的解决方案**：

```python
class CustomHTTPRedirectHandler(HTTPRedirectHandler):
    # 自动跟随重定向
    # 支持 301, 302, 303, 307, 308 状态码
    # 处理相对和绝对 URL
```

**特性**：
- 自动跟随 HTTP 重定向
- 支持 meta refresh 重定向
- 记录重定向链，避免死循环
- 保留完整的 URL 历史

### 3. Cookie 支持

**问题**：某些网站需要 Cookie 才能正常访问内容。

**Morss 的解决方案**：

```python
# 使用 HTTPCookieProcessor 自动处理 Cookie
opener = build_opener(HTTPCookieProcessor())
```

**特性**：
- 自动保存服务器设置的 Cookie
- 在后续请求中自动发送 Cookie
- 支持会话级别的 Cookie 管理

### 4. Gzip 压缩支持

**问题**：现代网站通常使用 gzip 压缩响应内容。

**Morss 的解决方案**：

```python
# 自动处理 gzip 压缩的内容
if con.headers.get('Content-Encoding') == 'gzip':
    data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
```

**特性**：
- 自动检测 gzip 编码
- 透明解压缩内容
- 减少网络传输时间

### 5. 字符编码检测

**问题**：网页可能使用各种字符编码（UTF-8, GBK, GB2312 等）。

**Morss 的解决方案**：

```python
import chardet

# 多重编码检测策略
# 1. 从 HTTP 头 Content-Type 获取
# 2. 从 HTML meta 标签获取
# 3. 使用 chardet 自动检测
encoding = chardet.detect(data)['encoding']
```

**支持的编码**：
- UTF-8
- GBK, GB2312, GB18030（中文）
- ISO-8859-1（西欧）
- 其他各种编码

### 6. HTTP 缓存机制

**问题**：频繁请求同一资源浪费带宽，可能被服务器封禁。

**Morss 的解决方案**：

实现了完整的 HTTP 缓存系统（在 `caching.py` 和 `crawler.py` 中）：

```python
# 支持 ETag
if 'etag' in con.headers:
    cache['etag'] = con.headers['etag']

# 支持 Last-Modified
if 'last-modified' in con.headers:
    cache['last-modified'] = con.headers['last-modified']

# 在下次请求时使用
if cache.get('etag'):
    req.add_header('If-None-Match', cache['etag'])
if cache.get('last-modified'):
    req.add_header('If-Modified-Since', cache['last-modified'])
```

**缓存后端支持**：

1. **内存缓存**（默认）
   ```bash
   # 默认就是内存缓存
   morss http://example.com/feed.xml
   ```

2. **Redis 缓存**
   ```bash
   # 需要环境变量
   export CACHE=redis
   export REDIS_URL=redis://localhost:6379
   morss http://example.com/feed.xml
   ```

3. **磁盘缓存**
   ```bash
   # 持久化缓存
   export CACHE=diskcache
   export CACHE_DIR=/path/to/cache
   morss http://example.com/feed.xml
   ```

**缓存控制参数**：
- `--cache` - 优先使用缓存
- `--force` - 强制刷新，忽略缓存
- `LIM_TIME` 环境变量 - 设置缓存过期时间

### 7. 请求超时控制

**问题**：某些网站响应很慢，可能导致程序挂起。

**Morss 的解决方案**：

```python
# 默认超时设置
TIMEOUT = 4  # 秒

# 可以通过参数调整
con = opener.open(url, data=post, timeout=timeout)
```

**使用方法**：
```bash
# 自定义超时（秒）
morss --timeout=10 http://example.com/feed.xml
```

### 8. 请求频率限制

**问题**：快速连续请求可能被识别为爬虫并被封禁。

**Morss 的解决方案**：

```python
# 在 morss.py 中定义
DELAY = 0  # 默认延迟（秒）

# 在批量处理时添加延迟
time.sleep(DELAY)
```

**使用方法**：
```bash
# 设置请求间隔（秒）
morss --delay=2 http://example.com/feed.xml
```

**环境变量控制**：
```bash
export DELAY=2
```

### 9. Referer 处理

**问题**：某些网站检查 Referer 头来防止直接访问。

**Morss 的解决方案**：

在请求文章内容时，会自动设置 Referer 为 RSS feed 的 URL：

```python
# 自动设置 Referer
req.add_header('Referer', feed_url)
```

### 10. 内容提取算法

**问题**：从复杂的网页中提取正文内容。

**Morss 的解决方案**：

使用 `readabilite.py` 中实现的启发式算法：

```python
# 基于内容密度和标签权重的算法
# 1. 分析 HTML 结构
# 2. 计算每个元素的内容分数
# 3. 识别主要内容区域
# 4. 排除广告、侧边栏、导航栏
# 5. 保留有意义的标签（p, h1-h6, img, a 等）
```

**自定义内容提取**：
```bash
# 使用 XPath 精确指定内容位置
morss --xpath="//div[@id='article-content']" http://example.com/feed.xml
```

## 高级反爬策略

### 1. 处理 JavaScript 动态加载

**限制**：Morss 本身不执行 JavaScript，只能访问初始 HTML。

**解决方案**：

对于 JavaScript 渲染的内容，可以：

1. **查找 API 接口**：许多网站的数据来自 JSON API
   ```bash
   # 直接访问 API 并使用 JSON 模式
   morss --mode=json --items="data.[]" http://api.example.com/posts
   ```

2. **使用预渲染服务**（需自己搭建）：
   ```bash
   # 通过预渲染服务
   morss http://prerender.example.com/render?url=http://target.com
   ```

3. **寻找移动版或 AMP 版本**：
   ```bash
   # 移动版通常是纯 HTML
   morss http://m.example.com/feed
   ```

### 2. IP 封禁应对

**如果 IP 被封禁**：

1. **使用代理**：
   ```bash
   # HTTP 代理
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   morss http://example.com/feed.xml
   ```

2. **调整请求频率**：
   ```bash
   # 增加延迟
   export DELAY=5
   # 设置更长的缓存时间
   export LIM_TIME=3600  # 1小时
   ```

3. **使用多个 Morss 实例**：
   部署多个实例，分散请求压力

### 3. 验证码处理

**限制**：Morss 无法自动处理验证码。

**解决方案**：

1. **避免触发验证码**：
   - 降低请求频率
   - 使用更真实的 User-Agent
   - 保持 Cookie 会话

2. **寻找无验证码的入口**：
   - RSS feed 本身通常没有验证码
   - API 接口可能不需要验证码

3. **手动获取 Cookie**：
   如果网站需要登录，可以手动获取 Cookie 后配置到 Morss

### 4. 处理付费墙/登录墙

**对于需要登录的内容**：

当前版本的 Morss 不直接支持登录，但可以：

1. **手动配置 Cookie**（需修改代码）
2. **使用已登录的浏览器会话**（需要扩展）
3. **寻找公开的内容源**

## 环境变量配置汇总

```bash
# 缓存设置
export CACHE=diskcache           # 缓存类型：memory, redis, diskcache
export CACHE_DIR=/path/to/cache  # 磁盘缓存目录
export REDIS_URL=redis://...     # Redis 连接 URL

# 请求控制
export DELAY=2                   # 请求间隔（秒）
export TIMEOUT=10                # 请求超时（秒）

# 限制设置
export LIM_TIME=3600             # 缓存过期时间（秒）
export LIM_ITEM=100              # 最大处理文章数
export LIM_CACHE=1000            # 缓存容量限制

# 代理设置
export HTTP_PROXY=http://...     # HTTP 代理
export HTTPS_PROXY=http://...    # HTTPS 代理
```

## 命令行参数汇总

```bash
# 基础参数
morss [选项] <RSS_URL>

# 常用选项
--cache              # 优先使用缓存
--force              # 强制刷新，忽略缓存
--debug              # 调试模式
--silent             # 静默模式

# 内容控制
--xpath=<XPATH>      # 自定义内容提取规则
--keep               # 保留原始内容
--nolink             # 不获取完整文章
--noref              # 不跟随重定向

# 自定义订阅源
--items=<XPATH>      # 条目选择器（必需）
--item_title=<XPATH> # 标题提取
--item_link=<XPATH>  # 链接提取
--item_content=<XPATH> # 内容提取
--mode=<MODE>        # 解析模式：html, xml, json

# 输出格式
--txt                # 纯文本输出
--json               # JSON 格式
--csv                # CSV 格式
--html               # HTML 格式（带样式）

# 其他
--user-agent=<UA>    # 自定义 User-Agent
--timeout=<秒>       # 超时时间
--delay=<秒>         # 请求延迟
```

## 最佳实践

### 1. 礼貌爬虫原则

- ✅ 遵守 robots.txt
- ✅ 设置合理的请求间隔
- ✅ 使用缓存避免重复请求
- ✅ 使用真实的 User-Agent
- ✅ 在合理的时间段访问（避免高峰期）

### 2. 性能优化

```bash
# 使用磁盘缓存（持久化）
export CACHE=diskcache
export CACHE_DIR=/var/cache/morss

# 增加缓存时间
export LIM_TIME=7200  # 2小时

# 限制并发
export LIM_ITEM=50    # 每次最多处理50篇文章

# Docker 部署
docker run -d \
  -p 8000:8000 \
  -e CACHE=diskcache \
  -e LIM_TIME=7200 \
  -v /var/cache/morss:/cache \
  morss
```

### 3. 故障排查

**问题：无法访问网站**
```bash
# 1. 检查网络连接
curl -I http://example.com

# 2. 尝试使用代理
export HTTP_PROXY=http://proxy:8080
morss http://example.com/feed.xml

# 3. 查看详细错误
morss --debug http://example.com/feed.xml
```

**问题：内容提取不准确**
```bash
# 1. 使用自定义 XPath
morss --xpath="//article" http://example.com/feed.xml

# 2. 查看原始 HTML
morss --debug --keep http://example.com/feed.xml

# 3. 使用浏览器开发者工具分析页面结构
```

**问题：请求被拒绝**
```bash
# 1. 检查 User-Agent
morss --user-agent="Mozilla/5.0 ..." http://example.com/feed.xml

# 2. 增加延迟
morss --delay=5 http://example.com/feed.xml

# 3. 使用缓存
morss --cache http://example.com/feed.xml
```

## 与 requests 库的对比

| 特性 | urllib（Morss 使用） | requests 库 |
|------|---------------------|------------|
| 安装 | 标准库，无需安装 | 需要 pip install |
| 体积 | 轻量级 | 较大 |
| API | 较底层 | 更友好 |
| 功能 | 完整但需要手动配置 | 开箱即用 |
| 性能 | 相当 | 相当 |
| 自定义 | 更灵活 | 稍受限 |

**Morss 选择 urllib 的原因**：
- ✅ 减少依赖
- ✅ 更小的镜像体积
- ✅ 更好的控制
- ✅ 足够满足需求

## 总结

Morss 通过以下机制实现可靠的网页爬取：

1. **HTTP 层面**：
   - User-Agent 轮换
   - Cookie 支持
   - 重定向处理
   - Gzip 解压
   - 超时控制

2. **应用层面**：
   - HTTP 缓存（ETag/Last-Modified）
   - 多种缓存后端
   - 智能内容提取
   - 字符编码检测

3. **反爬虫对策**：
   - 请求频率控制
   - 真实浏览器 UA
   - Referer 处理
   - 代理支持

4. **灵活性**：
   - 自定义 XPath
   - 多种输出格式
   - 丰富的配置选项

虽然 Morss 不使用 requests 库，但通过 urllib 和精心设计的处理器，实现了同样强大甚至更灵活的 HTTP 请求功能。

## 参考资源

- [官方文档](https://git.pictuga.com/pictuga/morss)
- [XPath 自定义规则详解](XPATH_CUSTOM_FEEDS_CN.md)
- [项目流程说明](项目流程说明.md)
- [urllib 文档](https://docs.python.org/3/library/urllib.html)
