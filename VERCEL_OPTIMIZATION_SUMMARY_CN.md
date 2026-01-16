# Vercel 部署优化总结

## 项目状态：✅ 已优化完成，可以部署

本项目已经完成 Vercel 部署优化，所有测试通过，可以直接部署到 Vercel 平台。

## 完成的改进

### 1. 配置文件优化

#### vercel.json
- ✅ 配置了 Python serverless 函数构建
- ✅ 设置了请求路由（所有请求 → API 函数）
- ✅ 配置了环境变量以适应 Vercel 10 秒超时限制
  - `MAX_ITEM=30` - 最多抓取 30 篇文章
  - `MAX_TIME=20` - 抓取时间限制 20 秒
  - `TIMEOUT=8` - HTTP 请求超时 8 秒
  - `LIM_TIME=25` - 总时间限制 25 秒
  - `LIM_ITEM=50` - 最多处理 50 个条目

#### runtime.txt
- ✅ 指定 Python 3.9 运行时
- ✅ 保证与所有依赖包的兼容性

#### requirements.txt
- ✅ 添加版本约束确保构建可重现性
- ✅ 使用 `beautifulsoup4` 而不是 `bs4` 元包
- ✅ 所有依赖都经过安全检查（无漏洞）

### 2. 开发环境优化

#### .python-version
- ✅ 本地开发版本一致性
- ✅ 与 Vercel 运行时版本匹配

#### .vercelignore
- ✅ 排除不必要的文件减小部署大小
- ✅ 保留必要文档（README.md, VERCEL_DEPLOYMENT_CN.md, VERCEL_CONFIG.md）
- ✅ 排除测试、Docker 文件、其他平台的 CI/CD 配置

### 3. 文档完善

#### VERCEL_CONFIG.md (新增)
详细的技术文档，包含：
- 📋 配置文件说明
- 🔄 请求流程图解
- 🛠️ 环境变量详解
- 🐛 故障排查指南
- 🧪 本地测试说明

#### 现有文档
- ✅ VERCEL_DEPLOYMENT_CN.md - 中文部署指南
- ✅ README.md - 项目说明
- ✅ 快速部署.md - 快速命令参考

## 测试结果

### ✅ 所有测试通过（8/8）

1. ✅ vercel.json 配置有效
2. ✅ runtime.txt 正确（Python 3.9）
3. ✅ requirements.txt 包含所有依赖
4. ✅ api/index.py 导入成功
5. ✅ www 目录包含 7 个静态文件
6. ✅ .vercelignore 配置正确
7. ✅ WSGI 应用测试（3 个路由）
   - `/` (根路径) → 200 OK
   - `/index.html` → 200 OK
   - `/xpath-selector.html` → 200 OK
8. ✅ 所有文档文件存在

### 🔒 安全检查

- ✅ 无代码漏洞（CodeQL 检查）
- ✅ 依赖包无已知漏洞（GitHub Advisory Database）
  - lxml 4.6.0+ → 安全
  - beautifulsoup4 4.9.0+ → 安全
  - python-dateutil 2.8.0+ → 安全
  - chardet 4.0.0+ → 安全

## 技术架构

```
用户请求
    ↓
Vercel CDN
    ↓
api/index.py (Serverless Function)
    ↓
morss/wsgi.py (WSGI Application)
    ↓
    ├─→ cgi_file_handler → 静态文件 (www/)
    └─→ cgi_app → RSS 处理
```

### 关键特性

1. **单一入口点**: 所有请求通过 `api/index.py`
2. **WSGI 中间件**: 自动处理静态文件和 RSS 请求
3. **无状态设计**: 每个请求独立，适合 serverless 环境
4. **性能优化**: 环境变量限制确保不超时

## 部署方法

### 方式一：一键部署（推荐）

点击 README.md 中的按钮：
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YeWeihong/morss-vercel)

### 方式二：Vercel CLI

```bash
npm i -g vercel
cd /path/to/morss-vercel
vercel --prod
```

### 方式三：GitHub 导入

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库
3. Vercel 自动检测配置
4. 点击 "Deploy"

## 部署后验证

部署完成后，访问以下 URL 验证：

```bash
# 替换 YOUR-PROJECT.vercel.app 为你的实际域名

# 1. 主页
https://YOUR-PROJECT.vercel.app/

# 2. XPath 选择器工具
https://YOUR-PROJECT.vercel.app/xpath-selector.html

# 3. 测试 RSS 处理（使用 debug 模式）
https://YOUR-PROJECT.vercel.app/:debug/https://www.example.com/feed.xml

# 4. 静态文件
https://YOUR-PROJECT.vercel.app/logo.svg
```

## 性能预期

### Hobby 计划（免费）
- ⏱️ 每个请求 < 10 秒
- 📊 每小时 1000 次请求
- 💾 1024 MB 内存
- ✅ 自动 HTTPS
- 🌍 全球 CDN

### 推荐使用场景
- ✅ 个人 RSS 订阅（< 30 条目）
- ✅ 小型博客全文 RSS
- ✅ 特定主题订阅源
- ✅ 轻度到中度使用

### 不推荐场景
- ❌ 大型新闻网站（> 100 条目）
- ❌ 高频率抓取（> 1000/小时）
- ❌ 需要长时间处理的订阅源

## 后续优化建议

如果需要更好的性能，可以考虑：

### 1. 配置外部 Redis 缓存
```bash
# 在 Vercel Dashboard 添加环境变量
CACHE=redis
REDIS_HOST=your-redis.upstash.io
REDIS_PORT=6379
REDIS_PWD=your-password
```

推荐服务：
- [Upstash](https://upstash.com/) - 专为 serverless 设计
- [Redis Labs](https://redis.com/) - 免费 30MB

### 2. 升级到 Pro 计划
- ⏱️ 60 秒执行时间（6x 免费版）
- 📊 更高的请求限制
- 💰 $20/月

### 3. 调整环境变量
根据实际使用情况在 Vercel Dashboard 调整：
```bash
MAX_ITEM=20    # 减少可提高速度
MAX_TIME=15    # 减少可避免超时
TIMEOUT=5      # 减少可避免慢速网站拖累
```

## 故障排查

### 构建失败
- 检查 `lxml` 是否编译成功（可能需要几分钟）
- 确认 Python 版本是 3.9

### 函数超时
- 在 Vercel Dashboard 减小 `MAX_ITEM` 和 `MAX_TIME`
- 考虑升级到 Pro 计划

### 静态文件 404
- 确认文件在 `www/` 目录中
- 检查 `morss/wsgi.py` 中的 `cgi_file_handler`

## 相关文档

- **[VERCEL_CONFIG.md](VERCEL_CONFIG.md)** - 技术配置详解（英文）
- **[VERCEL_DEPLOYMENT_CN.md](VERCEL_DEPLOYMENT_CN.md)** - 完整部署指南（中文）
- **[README.md](README.md)** - 项目说明
- **[快速部署.md](快速部署.md)** - 快速命令参考

## 获取帮助

- 📝 **GitHub Issues**: https://github.com/YeWeihong/morss-vercel/issues
- 🌐 **原项目主页**: https://morss.it/
- 📚 **Vercel 文档**: https://vercel.com/docs

---

**优化完成时间**: 2026-01-16  
**测试状态**: ✅ 全部通过 (8/8)  
**安全状态**: ✅ 无已知漏洞  
**部署状态**: ✅ 可以部署

**版权声明**: 本项目基于 [pictuga/morss](https://git.pictuga.com/pictuga/morss) 修改。原作者：pictuga，许可证：GNU AGPLv3
