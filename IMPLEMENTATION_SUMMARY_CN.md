# 功能实现说明

## 概述

本次更新为 Morss 项目添加了缺失的 XPath 选择器工具，并提供了关于项目爬虫机制和反爬策略的详细中文文档。

## 您提出的三个问题的答案

### 1. 原版 morss.it 网站上的 XPath 选择器功能是否内置在项目中？

**答：❌ 之前没有，✅ 现在已添加**

原版 morss.it 网站上确实有一个可视化的 XPath 选择器工具，但这个功能之前并未包含在开源代码库中。本次更新已经实现了这个功能：

- **访问地址**：部署后访问 `http://localhost:8000/xpath-selector.html`
- **功能特性**：
  - 输入目标网页 URL
  - 按步骤点击页面元素进行选择
  - 自动生成 XPath 规则
  - 提供编码后的 Morss 订阅 URL
  - 一键复制和测试功能

**使用限制**：
- 由于浏览器 CORS（跨域资源共享）安全限制，部分网站无法直接在工具中加载
- 对于这些网站，工具会提示使用浏览器开发者工具（F12）手动获取 XPath
- 详细的使用说明和替代方案已包含在工具界面中

### 2. 项目是否使用 requests 库？项目是怎么爬虫的？

**答：没有使用 requests 库，使用的是 Python 标准库中的 urllib**

Morss 项目使用 Python 内置的 `urllib`/`urllib2`（Python 2）或 `urllib.request`（Python 3）进行 HTTP 请求，而不是第三方的 `requests` 库。

**为什么不用 requests？**

1. **减少外部依赖**：urllib 是 Python 标准库的一部分，无需额外安装
2. **轻量级部署**：减小 Docker 镜像大小，加快安装速度
3. **功能充足**：urllib 提供了 Morss 所需的所有 HTTP 功能
4. **更好的控制**：可以更底层地控制 HTTP 请求细节

**爬虫工作原理**：

项目的 HTTP 请求处理核心在 `morss/crawler.py` 文件中：

1. 使用 `custom_opener()` 创建自定义的 URL opener
2. 添加各种处理器（Cookie、重定向、Gzip 等）
3. 发送 HTTP 请求获取内容
4. 自动处理编码、压缩、缓存等问题
5. 使用 `readabilite.py` 中的算法提取文章正文

详细技术说明请查看 `CRAWLER_ANTI_SCRAPING_CN.md` 文档。

### 3. 对于反爬机制有哪些策略？

**答：实现了多种反爬虫应对策略**

Morss 项目实现了以下反爬虫策略：

#### HTTP 层面策略

1. **User-Agent 轮换**
   - 随机选择 10+ 种真实浏览器的 User-Agent
   - 模拟 Chrome、Firefox、Safari 等主流浏览器
   - 包含完整的系统信息和版本号

2. **Cookie 支持**
   - 自动保存服务器设置的 Cookie
   - 在后续请求中自动发送
   - 支持会话级别的 Cookie 管理

3. **HTTP 重定向处理**
   - 自动跟随 301/302/303/307/308 重定向
   - 支持 meta refresh 重定向
   - 避免重定向死循环

4. **Gzip 压缩**
   - 自动检测和解压 gzip 编码
   - 减少网络传输时间

5. **字符编码检测**
   - 支持 UTF-8、GBK、GB2312 等多种编码
   - 自动检测和转换字符编码

#### 应用层面策略

6. **HTTP 缓存机制**
   - 支持 ETag 和 Last-Modified 头
   - 三种缓存后端：内存、Redis、磁盘
   - 避免重复请求同一资源

7. **请求超时控制**
   - 默认 4 秒超时
   - 可自定义超时时间
   - 避免程序挂起

8. **请求频率限制**
   - 支持请求间隔延迟
   - 可通过参数或环境变量配置
   - 避免被识别为恶意爬虫

9. **Referer 处理**
   - 自动设置合适的 Referer 头
   - 模拟正常的浏览器行为

10. **智能内容提取**
    - 基于内容密度的启发式算法
    - 自动识别文章主体内容
    - 排除广告、侧边栏等无关内容

#### 高级策略

11. **代理支持**
    - 支持 HTTP/HTTPS 代理
    - 通过环境变量配置

12. **自定义 XPath**
    - 精确指定内容提取位置
    - 适应各种网页结构

更多详细信息请查看 `CRAWLER_ANTI_SCRAPING_CN.md` 文档。

## 新增文件说明

### 1. www/xpath-selector.html
可视化 XPath 选择器工具，提供友好的界面帮助用户生成 XPath 规则。

**功能**：
- 输入目标网页 URL
- 按步骤点击选择页面元素
- 自动生成 XPath 表达式
- 生成可用的 Morss 订阅 URL
- 提供使用说明和示例

### 2. CRAWLER_ANTI_SCRAPING_CN.md
全面的爬虫机制和反爬策略中文文档。

**内容**：
- 为什么使用 urllib 而不是 requests
- HTTP 请求的核心实现
- 10+ 种反爬虫策略详解
- 环境变量配置说明
- 命令行参数汇总
- 最佳实践建议
- 故障排查指南

### 3. www/ 目录下的文档副本
将主要的 Markdown 文档复制到 www/ 目录，使其可以通过 Web 服务器访问：
- `XPATH_CUSTOM_FEEDS_CN.md` - XPath 自定义规则详解
- `XPATH_CUSTOM_FEEDS.md` - XPath 规则详解（英文）
- `CRAWLER_ANTI_SCRAPING_CN.md` - 爬虫与反爬策略

### 4. .gitignore
添加 Python 构建产物的忽略规则，避免提交不必要的文件。

## 修改的文件

### www/index.html
在主页添加了 XPath 选择器工具的醒目链接。

### README.md
- 更新功能特性列表，突出 XPath 选择器工具
- 添加反爬虫策略的说明
- 添加新文档的链接

## 如何使用

### 使用 XPath 选择器工具

1. 启动 Morss 服务器：
   ```bash
   # 方式 1：使用 gunicorn（推荐）
   gunicorn --bind 0.0.0.0:8000 morss
   
   # 方式 2：使用 Python
   python -m morss.wsgi
   
   # 方式 3：使用 Docker
   docker run -p 8000:8000 morss
   ```

2. 在浏览器中访问：
   ```
   http://localhost:8000/xpath-selector.html
   ```

3. 按照界面提示操作：
   - 输入要抓取的网页 URL
   - 点击"加载网页"
   - 依次点击页面元素选择 items、title、link 等
   - 复制生成的 Morss URL

### 阅读文档

启动服务器后，可以通过以下 URL 访问文档：

- XPath 规则详解（中文）：`http://localhost:8000/XPATH_CUSTOM_FEEDS_CN.md`
- 爬虫机制详解（中文）：`http://localhost:8000/CRAWLER_ANTI_SCRAPING_CN.md`

或者直接在代码库根目录查看对应的 Markdown 文件。

### 配置反爬虫策略

#### 设置请求延迟
```bash
# 方式 1：环境变量
export DELAY=2
morss http://example.com/feed.xml

# 方式 2：命令行参数
morss --delay=2 http://example.com/feed.xml
```

#### 使用代理
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
morss http://example.com/feed.xml
```

#### 配置缓存
```bash
# 使用磁盘缓存
export CACHE=diskcache
export CACHE_DIR=/path/to/cache
morss http://example.com/feed.xml

# 使用 Redis 缓存
export CACHE=redis
export REDIS_URL=redis://localhost:6379
morss http://example.com/feed.xml
```

更多配置选项请查看 `CRAWLER_ANTI_SCRAPING_CN.md` 文档。

## 测试验证

所有新增功能已经过测试验证：

✅ XPath 选择器工具界面正常加载
✅ 工具可以生成正确的 XPath 规则
✅ Morss URL 编码正确
✅ 文档可以通过 Web 服务器访问
✅ 主页链接正常工作

## 总结

本次更新完整回答了您提出的三个问题：

1. **XPath 选择器**：已添加可视化工具
2. **HTTP 库**：使用 urllib 而非 requests，原因和实现已详细说明
3. **反爬策略**：实现了 10+ 种策略，并提供了全面的中文文档

所有功能都经过测试，可以立即在本地部署使用。

如有任何问题或需要进一步的说明，请随时提出！
