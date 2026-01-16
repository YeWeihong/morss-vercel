# Morss Vercel 部署指南

## 什么是 Vercel？

[Vercel](https://vercel.com/) 是一个现代化的云平台，专为前端开发者和 Jamstack 应用设计。它提供：

- **零配置部署**：从 Git 仓库自动部署
- **全球 CDN**：自动分发到全球边缘网络
- **自动 HTTPS**：免费 SSL 证书
- **无服务器函数**：支持 Python、Node.js 等后端
- **免费套餐**：个人项目完全免费

## Morss 可以部署在 Vercel 上吗？

**可以！** 本项目已经配置好了 Vercel 部署支持。

Morss 是一个 Python WSGI 应用，通过 Vercel 的 Python Serverless 函数功能，可以轻松部署到 Vercel 平台。

## 快速开始

### 方式一：一键部署（最简单）

点击下方按钮，立即部署到 Vercel：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YeWeihong/morss)

步骤：
1. 点击按钮
2. 使用 GitHub 账号登录 Vercel（如果还没有账号）
3. 选择仓库名称（或使用默认名称）
4. 点击 "Deploy" 开始部署
5. 等待 2-3 分钟，部署完成
6. 获得一个 `https://your-project.vercel.app` 域名

### 方式二：使用 Vercel CLI

如果你习惯使用命令行工具：

```bash
# 1. 安装 Vercel CLI（需要先安装 Node.js）
npm i -g vercel

# 2. 克隆项目
git clone https://github.com/YeWeihong/morss.git
cd morss

# 3. 登录 Vercel
vercel login

# 4. 部署项目
vercel

# 按照提示操作：
# - Set up and deploy? Yes
# - Which scope? 选择你的账号
# - Link to existing project? No
# - What's your project's name? morss（或自定义）
# - In which directory? ./（当前目录）
# - Want to override the settings? No

# 5. 部署到生产环境
vercel --prod
```

### 方式三：从 GitHub 导入

1. Fork 本仓库到你的 GitHub 账号
2. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
3. 点击 "New Project"
4. 选择 "Import Git Repository"
5. 找到你 fork 的 `morss` 仓库，点击 "Import"
6. Vercel 会自动检测 `vercel.json` 配置
7. 点击 "Deploy" 开始部署

## 配置说明

### 项目结构

部署到 Vercel 需要以下文件（已包含在本项目中）：

```
morss/
├── api/
│   └── index.py          # Vercel serverless 函数入口
├── morss/                # Morss 核心代码
├── www/                  # 静态文件（前端页面）
├── vercel.json           # Vercel 配置文件
├── requirements.txt      # Python 依赖
└── .vercelignore         # 忽略不需要部署的文件
```

### vercel.json 配置

```json
{
  "version": 2,
  "name": "morss",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "CACHE": "diskcache",
    "CACHE_SIZE": "104857600",
    "MAX_ITEM": "50",
    "MAX_TIME": "30",
    "TIMEOUT": "10"
  }
}
```

配置说明：
- `builds`: 指定构建 Python serverless 函数
- `routes`: 将所有请求路由到 Python 函数
- `env`: 默认环境变量（可在 Vercel Dashboard 中覆盖）

### 环境变量配置

在 Vercel Dashboard 中配置环境变量：

1. 进入项目设置：`Settings` → `Environment Variables`
2. 添加以下变量（可选）：

#### 缓存配置（可选但推荐）

**默认情况**：Morss 使用内存缓存，每次请求独立，无持久化。

**推荐配置**：使用外部 Redis 实现跨请求缓存

```bash
# Redis 配置（推荐）
CACHE=redis
REDIS_HOST=your-redis.upstash.io
REDIS_PORT=6379
REDIS_PWD=your-password
REDIS_DB=0
```

**注意**：
- 磁盘缓存（`diskcache`）在 Vercel serverless 环境中**不起作用**（每次请求会重置）
- 如果不配置外部 Redis，将使用内存缓存（每次请求独立）
- 外部 Redis 可以显著提升性能，避免重复抓取

#### 性能配置（已在 vercel.json 中设置默认值）

```bash
# 限制抓取数量（重要！Vercel 有执行时间限制）
MAX_ITEM=30             # 最多抓取 30 篇文章（默认）
MAX_TIME=20             # 最多花费 20 秒抓取（默认）

# HTTP 超时
TIMEOUT=8               # 每个请求最多等待 8 秒（默认）

# 总时间限制
LIM_TIME=25             # 整个处理过程不超过 25 秒（默认）
LIM_ITEM=50             # 最多处理 50 个条目（默认）
```

**说明**：这些值已经在 `vercel.json` 中配置为默认值，适合 Hobby 计划的 10 秒限制。如果需要调整，可以在 Vercel Dashboard 中覆盖。

#### 调试配置

```bash
# 调试模式（仅开发环境使用）
DEBUG=1

# 忽略 SSL 证书错误（不推荐）
IGNORE_SSL=0
```

## 使用方法

部署成功后，访问你的 Vercel 域名，使用方式与本地部署相同：

### 基本格式

```
https://your-project.vercel.app/https://example.com/feed.xml
```

### 带参数

```
# 获取完整文章内容
https://your-project.vercel.app/:clip/https://example.com/feed.xml

# 输出 JSON 格式
https://your-project.vercel.app/:format=json/https://example.com/feed.xml

# 自定义 XPath（| 代表 /）
https://your-project.vercel.app/:items=||div[@class='post']/https://example.com
```

### 访问工具

```
# XPath 选择器工具
https://your-project.vercel.app/xpath-selector.html

# 帮助文档
https://your-project.vercel.app/XPATH_CUSTOM_FEEDS_CN.md
```

## 重要限制与注意事项

### Vercel Serverless 限制

Vercel 的 serverless 函数有以下限制：

1. **执行时间限制**
   - Hobby（免费）计划：**10 秒**
   - Pro 计划：60 秒
   - Enterprise 计划：900 秒
   
   ⚠️ **这是最重要的限制**！如果抓取时间超过限制，函数会被强制终止。

2. **内存限制**
   - 所有计划：1024 MB
   - 处理大型 RSS 订阅源可能超出内存限制

3. **存储限制**
   - Serverless 函数是**无状态**的
   - 每次请求都会重新启动
   - 磁盘缓存在请求结束后会丢失

4. **并发限制**
   - Hobby 计划：1000 次/小时
   - Pro 计划：更高限制

### 推荐配置

针对 Vercel 的限制，推荐以下配置：

```bash
# 严格限制执行时间（Hobby 计划）
MAX_TIME=8              # 抓取时间限制 8 秒
MAX_ITEM=20             # 最多抓取 20 篇文章
LIM_TIME=9              # 总时间限制 9 秒
TIMEOUT=5               # HTTP 超时 5 秒

# 使用外部 Redis（强烈推荐）
CACHE=redis
REDIS_HOST=...          # 见下文推荐服务
```

### 最佳实践

1. **使用外部 Redis 缓存**
   
   由于 serverless 函数无状态，强烈推荐使用外部 Redis：
   
   - [Upstash](https://upstash.com/)（推荐）
     - 专为 serverless 设计
     - 免费套餐：10,000 次请求/天
     - 延迟低，全球分布
   
   - [Redis Labs](https://redis.com/)
     - 免费 30MB 存储
     - 企业级可靠性
   
   - [Railway](https://railway.app/)
     - 简单易用
     - 免费 500 小时/月

2. **限制抓取数量**
   
   ```bash
   MAX_ITEM=30           # 根据订阅源大小调整
   MAX_TIME=20           # 留有余量，避免超时
   ```

3. **针对小订阅源优化**
   
   Vercel 更适合处理：
   - 小型个人博客 RSS（< 20 条目）
   - 新闻网站摘要（< 50 条目）
   - 特定主题订阅源
   
   不适合：
   - 大型新闻网站完整订阅（> 100 条目）
   - 需要抓取全文的大型订阅源
   - 高频率更新的订阅源

4. **监控和调试**
   
   在 Vercel Dashboard 中查看：
   - `Functions` 标签：查看函数执行时间和错误
   - `Logs` 标签：查看详细日志
   - 设置 `DEBUG=1` 环境变量查看更多信息

## 替代方案

如果 Vercel 的限制不能满足你的需求，考虑以下替代方案：

### 1. Vercel Pro 计划

- 执行时间：60 秒（远大于 Hobby 的 10 秒）
- 费用：$20/月
- 适合：中等规模使用

### 2. Docker 部署（VPS）

适合高流量、大型订阅源：

```bash
# 使用 Docker 在任何 VPS 上部署
docker run -d -p 8000:8000 \
  -e CACHE=redis \
  -e REDIS_HOST=... \
  pictuga/morss
```

推荐 VPS 提供商：
- DigitalOcean（$5/月起）
- Linode（$5/月起）
- Vultr（$3.5/月起）
- Oracle Cloud（免费套餐）

### 3. Railway

Railway 支持 Docker，没有 10 秒限制：

1. 访问 [Railway.app](https://railway.app/)
2. 从 GitHub 导入项目
3. Railway 会自动检测 Dockerfile
4. 免费 500 小时/月

### 4. Google Cloud Run

支持容器，更灵活的限制：

```bash
gcloud run deploy morss \
  --image gcr.io/YOUR_PROJECT/morss \
  --platform managed \
  --memory 1Gi \
  --timeout 300s
```

## 常见问题

### 1. 部署失败："Build exceeded maximum duration"

**原因**：构建时间超过限制（通常是 lxml 编译过慢）

**解决方案**：
- 使用预编译的依赖（已在 `requirements.txt` 中配置）
- 如果仍然失败，可能需要升级到 Pro 计划

### 2. 请求超时："Function execution timed out"

**原因**：函数执行超过 10 秒

**解决方案**：
```bash
# 减小这些值
MAX_ITEM=15
MAX_TIME=8
TIMEOUT=5
```

### 3. 缓存不工作

**原因**：Serverless 函数无状态，默认使用内存缓存（每次请求独立）

**解决方案**：
```bash
# 使用外部 Redis（需要先在 requirements.txt 中添加 redis 依赖）
CACHE=redis
REDIS_HOST=your-redis.upstash.io
REDIS_PORT=6379
REDIS_PWD=your-password
```

**注意**：如果需要使用 Redis，需要：
1. 在项目中创建/修改 `requirements.txt`，添加 `redis` 依赖
2. 或者在 Vercel 项目设置中配置 `pip install redis` 作为构建命令

### 4. 内存不足："Function exceeded memory limit"

**原因**：处理大型订阅源超过 1GB 内存

**解决方案**：
- 减小 `MAX_ITEM` 和 `LIM_ITEM`
- 使用 Docker 部署到 VPS

### 5. 某些网站无法抓取

**原因**：
- 网站有反爬虫机制
- 请求超时

**解决方案**：
- 增加 `TIMEOUT` 值（但注意总执行时间）
- 使用 VPS 部署以避免 IP 被封
- 查看 [CRAWLER_ANTI_SCRAPING_CN.md](CRAWLER_ANTI_SCRAPING_CN.md)

### 6. 如何绑定自定义域名？

1. 在 Vercel Dashboard 进入项目设置
2. 点击 `Domains` 标签
3. 输入你的域名（如 `morss.example.com`）
4. 按提示在 DNS 提供商处添加 CNAME 记录
5. 等待 DNS 生效（几分钟到几小时）

### 7. 如何添加可选依赖（Redis/diskcache）？

默认的 `requirements.txt` 只包含核心依赖。如果需要使用 Redis 或 diskcache：

**方法一**：Fork 后修改 requirements.txt

```bash
# 1. Fork 项目到你的 GitHub
# 2. 编辑 requirements.txt，添加：
redis
diskcache

# 3. 提交并推送
# 4. 从你的 fork 部署到 Vercel
```

**方法二**：配置构建命令（不推荐，因为每次部署都要安装）

在 Vercel 项目设置中：
1. 进入 `Settings` → `General`
2. 找到 `Build Command`
3. 设置为：`pip install redis diskcache`

**推荐**：只在需要时添加依赖。如果使用外部 Redis，添加 `redis`；如果不需要缓存，使用默认的内存缓存即可。

## 更新部署

### 自动更新（推荐）

从 GitHub 导入的项目，Vercel 会自动监听 Git 提交：

1. 在本地或 GitHub 上更新代码
2. Push 到 GitHub
3. Vercel 自动检测并重新部署

### 手动更新

使用 Vercel CLI：

```bash
# 在项目目录中
vercel --prod
```

## 性能优化建议

1. **使用 Redis 缓存**
   ```bash
   CACHE=redis
   REDIS_HOST=xxx.upstash.io
   ```

2. **合理设置限制**
   ```bash
   MAX_ITEM=20      # 平衡速度和完整性
   MAX_TIME=8       # 留有余量
   LIM_ITEM=30      # 防止处理过多条目
   ```

3. **禁用调试模式**
   ```bash
   DEBUG=0          # 生产环境必须关闭
   ```

4. **使用代理（如果需要）**
   ```bash
   HTTP_PROXY=http://proxy.example.com:8080
   ```

## 总结

### Vercel 适合的场景

✅ 个人使用，轻量级 RSS 订阅  
✅ 小型订阅源（< 30 条目）  
✅ 快速部署，无需维护服务器  
✅ 免费使用，自动 HTTPS  
✅ 全球 CDN 加速

### Vercel 不适合的场景

❌ 大型订阅源（> 100 条目）  
❌ 需要长时间抓取（> 10 秒）  
❌ 高频率访问（> 1000 次/小时）  
❌ 需要持久化存储（除非用外部 Redis）

### 推荐部署选择

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 个人轻量使用 | **Vercel** | 免费、简单、自动 HTTPS |
| 个人重度使用 | Vercel Pro | 60 秒执行时间 |
| 小团队/小型生产 | Railway / Render | 支持 Docker，更灵活 |
| 大型生产环境 | VPS + Docker | 完全控制，无限制 |

## 相关文档

- **[部署指南.md](部署指南.md)** - 完整部署文档（包含其他平台）
- **[快速部署.md](快速部署.md)** - 快速命令参考
- **[README.md](README.md)** - 项目说明
- **[XPATH_CUSTOM_FEEDS_CN.md](XPATH_CUSTOM_FEEDS_CN.md)** - XPath 使用指南
- **[CRAWLER_ANTI_SCRAPING_CN.md](CRAWLER_ANTI_SCRAPING_CN.md)** - 爬虫机制说明

## 获取帮助

- **GitHub Issues**: https://github.com/YeWeihong/morss/issues
- **原项目主页**: https://morss.it/
- **Vercel 文档**: https://vercel.com/docs

---

**版权声明**：本项目基于 [pictuga/morss](https://git.pictuga.com/pictuga/morss) 修改。原作者：pictuga，许可证：GNU AGPLv3
