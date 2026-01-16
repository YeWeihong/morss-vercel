# Morss 自定义 XPath 规则详解

## 概述

Morss 支持从任何网页创建 RSS 订阅源，通过自定义 XPath 规则来提取内容。这个功能非常强大，可以让你为没有 RSS 订阅的网站创建订阅源。

## 什么是 XPath？

XPath（XML Path Language）是一种在 XML/HTML 文档中查找信息的语言。它使用路径表达式来选择节点或节点集。

### 基本 XPath 语法

```xpath
/           # 从根节点选择
//          # 从匹配选择的当前节点选择文档中的节点，不考虑它们的位置
.           # 选择当前节点
..          # 选择当前节点的父节点
@           # 选择属性

# 示例：
//div                    # 选择所有 div 元素
//div[@class="title"]    # 选择 class 属性为 "title" 的所有 div 元素
//a/@href                # 选择所有 a 元素的 href 属性
//div[@id="content"]//p  # 选择 id 为 "content" 的 div 内的所有 p 元素
```

## Morss 自定义订阅源参数

### 必需参数

#### `--items` (必需)
这是**唯一必需的参数**，用于激活自定义订阅源功能。它定义了如何找到页面中的每个"条目"（文章/项目）。

**XPath 规则**：匹配所有 RSS 条目的 XPath 表达式

**示例**：
```bash
# 匹配所有 class 包含 "title" 的元素
--items="//div[contains(@class, 'title')]"

# 匹配所有 class 精确为 "post" 的 div
--items="//div[@class='post']"

# 匹配 id 为 "main" 的 div 中的所有 article 元素
--items="//div[@id='main']//article"
```

### 可选参数

#### `--item_link`
定义如何从每个条目中提取链接。

**默认值**：`(.|.//a|ancestor::a)/@href`（当前节点的 href，或子节点 a 的 href，或祖先 a 的 href）

**示例**：
```bash
--item_link=".//a/@href"              # 条目内第一个链接
--item_link=".//@data-url"            # 条目内 data-url 属性
--item_link=".//h2/a/@href"           # 条目内 h2 标签中的链接
```

#### `--item_title`
定义如何提取条目标题。

**默认值**：`.`（当前节点的文本内容）

**示例**：
```bash
--item_title="./h2"                   # 条目内的 h2 标签文本
--item_title=".//span[@class='name']" # 条目内 class 为 name 的 span
--item_title="./a"                    # 条目内第一个链接的文本
```

#### `--item_content`
定义如何提取条目的详细内容。

**默认值**：无（如果不指定，morss 会尝试从链接页面提取完整内容）

**示例**：
```bash
--item_content=".//div[@class='summary']"  # 条目内的摘要
--item_content="./p"                       # 条目内的段落
```

#### `--item_time`
定义如何提取条目的发布时间。

**默认值**：无

Morss 支持多种时间格式，会自动解析。

**示例**：
```bash
--item_time=".//span[@class='date']"     # 日期文本
--item_time=".//@data-timestamp"          # 时间戳属性
```

#### `--mode`
指定解析器类型。

**选项**：`xml`、`html`、`json`

**默认值**：自动检测

- `html`：用于普通 HTML 网页（最常用）
- `xml`：用于 XML 格式的数据
- `json`：用于 JSON 格式的数据

#### 订阅源级别参数

这些参数定义整个订阅源的元数据：

- `--title`：订阅源标题（默认：`//head/title`）
- `--desc`：订阅源描述（默认：`//head/meta[@name="description"]/@content`）

## Web 服务器 URL 格式

当通过 HTTP 访问 morss 时，参数通过 URL 传递，格式如下：

```
http://morss.example.com/:参数1:参数2=值/目标URL
```

### URL 编码规则

1. **斜杠替换**：在 URL 中，`/` 必须替换为 `|`（管道符）
   - 原因：`/` 在 URL 路径中有特殊含义
   - morss 会自动将 `|` 转换回 `/`

2. **URL 编码**：特殊字符需要进行 URL 编码
   - `[` → `%5B`
   - `]` → `%5D`
   - `=` → `%3D`
   - `"` → `%22`
   - 空格 → `%20`

### 实际示例解析

用户提供的示例：
```
https://morss.it/:items=%7C%7C*[class=title]/https://www.163.com/dy/media/T1486465837470.html
```

**解码过程**：

1. **URL 解码**：`%7C%7C*[class=title]` → `||*[class=title]`
2. **管道转斜杠**：`||*[class=title]` → `//*[class=title]`
3. **最终 XPath**：`//*[class=title]`

**含义**：
- `//*`：选择文档中的任何元素
- `[class=title]`：class 属性包含 "title" 的元素

在 HTML 模式下，morss 会自动优化 `[class=title]` 为更精确的匹配：
```xpath
[@class and contains(concat(" ", normalize-space(@class), " "), " title ")]
```

这样可以正确匹配 `class="post title"` 或 `class="title featured"` 这样的多类名情况。

## 完整示例

### 示例 1：简单的博客订阅

假设博客 HTML 结构如下：
```html
<div id="posts">
    <article class="post">
        <h2><a href="/post/1">文章标题 1</a></h2>
        <p class="summary">文章摘要...</p>
        <span class="date">2024-01-01</span>
    </article>
    <article class="post">
        <h2><a href="/post/2">文章标题 2</a></h2>
        <p class="summary">文章摘要...</p>
        <span class="date">2024-01-02</span>
    </article>
</div>
```

**CLI 命令**：
```bash
morss \
  --items="//article[@class='post']" \
  --item_title="./h2/a" \
  --item_link="./h2/a/@href" \
  --item_content="./p[@class='summary']" \
  --item_time="./span[@class='date']" \
  --mode=html \
  https://example.com/blog
```

**Web URL**（需要 URL 编码）：
```
https://morss.it/:items=%7C%7Carticle%5B%40class%3D%27post%27%5D:item_title=.%7Ch2%7Ca:item_link=.%7Ch2%7Ca%7C%40href:item_content=.%7Cp%5B%40class%3D%27summary%27%5D:item_time=.%7Cspan%5B%40class%3D%27date%27%5D:mode=html/https://example.com/blog
```

### 示例 2：列表页面

假设新闻网站结构如下：
```html
<div class="news-list">
    <div class="news-item">
        <a href="/news/1" class="title">新闻标题 1</a>
    </div>
    <div class="news-item">
        <a href="/news/2" class="title">新闻标题 2</a>
    </div>
</div>
```

**CLI 命令**：
```bash
morss \
  --items="//div[@class='news-item']" \
  --item_title=".//a[@class='title']" \
  --item_link=".//a[@class='title']/@href" \
  --mode=html \
  https://example.com/news
```

**简化 Web URL**：
```
https://morss.it/:items=%7C%7Cdiv%5B%40class%3D%27news-item%27%5D:item_title=.%7C%7Ca%5B%40class%3D%27title%27%5D:item_link=.%7C%7Ca%5B%40class%3D%27title%27%5D%7C%40href:mode=html/https://example.com/news
```

### 示例 3：使用 class 简写

Morss 支持简化的 class 匹配语法（仅在 HTML 模式下）：

**标准 XPath**：
```xpath
//div[@class and contains(concat(" ", normalize-space(@class), " "), " post ")]
```

**Morss 简写**：
```xpath
//div[class=post]
```

**用户的例子**：
```
:items=||*[class=title]
```
等价于标准 XPath：
```xpath
//*[@class and contains(concat(" ", normalize-space(@class), " "), " title ")]
```

## 调试技巧

### 1. 使用浏览器开发者工具

1. 打开目标网页
2. 按 F12 打开开发者工具
3. 点击"元素"选择器（或按 Ctrl+Shift+C）
4. 点击页面上要提取的内容
5. 在开发者工具中右键点击高亮的 HTML 元素
6. 选择"复制" → "复制 XPath" 或 "复制完整 XPath"

**注意**：浏览器生成的 XPath 通常很长，需要简化。

### 2. 测试 XPath 表达式

在浏览器控制台中测试 XPath：
```javascript
// 测试 XPath 是否匹配元素
$x("//div[@class='post']")

// 查看匹配的元素数量
$x("//div[@class='post']").length

// 查看第一个匹配元素
$x("//div[@class='post']")[0]
```

### 3. 使用 morss 调试模式

```bash
# 设置 DEBUG 环境变量
DEBUG=1 morss --items="//div[@class='post']" https://example.com

# 或者通过 Web URL
https://morss.it/:debug:items=...
```

### 4. 渐进式构建规则

1. 先只设置 `--items`，确保能匹配到条目
2. 然后添加 `--item_title`
3. 再添加 `--item_link`
4. 最后添加 `--item_content` 和 `--item_time`

## 常见 XPath 模式

### 选择器模式

```xpath
# 按 ID 选择
//div[@id='content']

# 按 class 选择（精确匹配）
//div[@class='post']

# 按 class 选择（包含匹配）
//div[contains(@class, 'post')]

# 按 class 选择（Morss HTML 简写）
//div[class=post]

# 按属性选择
//div[@data-id='123']

# 按文本内容选择
//div[contains(text(), '关键词')]

# 选择第一个子元素
//div[@class='list']/*[1]

# 选择最后一个子元素
//div[@class='list']/*[last()]

# 选择前3个元素
//div[@class='list']/*[position() <= 3]
```

### 组合选择

```xpath
# 父子关系（直接子元素）
//div[@class='parent']/div[@class='child']

# 后代关系（任意层级）
//div[@class='parent']//div[@class='descendant']

# 兄弟关系（紧随其后）
//div[@class='first']/following-sibling::div[1]

# 多条件（AND）
//div[@class='post' and @data-status='published']

# 多条件（OR）
//div[@class='post' or @class='article']
```

### 提取数据

```xpath
# 提取文本内容
//div[@class='title']              # 返回元素（morss 会提取文本）
//div[@class='title']/text()       # 直接返回文本

# 提取属性
//a/@href                          # 链接地址
//img/@src                         # 图片地址
//div/@data-id                     # 自定义属性

# 提取第一个匹配
(//div[@class='post'])[1]

# 从当前节点提取（相对路径）
.//a/@href                         # 当前节点下的链接
./h2                               # 当前节点的直接子元素 h2
../div                             # 当前节点的兄弟节点 div
```

## XPath 函数

Morss 支持常用的 XPath 函数：

```xpath
# 字符串函数
contains(@class, 'post')           # 包含检查
starts-with(@class, 'post')        # 开头检查
normalize-space(text())            # 去除首尾空格
concat('a', 'b')                   # 字符串连接

# 位置函数
position()                         # 当前位置
last()                             # 最后位置
count(//div)                       # 计数

# 逻辑函数
not(@class)                        # 取反
```

## 高级技巧

### 1. 处理动态 class 名

如果 class 名包含动态部分（如 `post-123`）：
```xpath
//div[starts-with(@class, 'post-')]
//div[contains(@class, 'post-')]
```

### 2. 排除某些元素

```xpath
# 排除 class 为 'ad' 的 div
//div[@class='post' and not(contains(@class, 'ad'))]

# 排除包含特定子元素的项
//div[@class='post' and not(.//div[@class='sponsored'])]
```

### 3. 选择多个不同类型的元素

```xpath
# 选择所有 h1, h2, h3
//*[self::h1 or self::h2 or self::h3]

# 选择所有 article 和 div.post
//article | //div[@class='post']
```

### 4. 处理命名空间

如果 HTML 使用了 XML 命名空间（不常见），需要使用前缀：
```xpath
//atom:entry        # Atom 格式
//rdf:item          # RDF 格式
```

Morss 已经预定义了常用命名空间（见 `feeds.py` 中的 `NSMAP`）。

## 故障排除

### 问题：XPath 没有匹配到任何元素

**解决方案**：
1. 检查 HTML 结构是否与预期一致（使用浏览器开发者工具）
2. 确认 `--mode` 参数正确（HTML 页面应使用 `html` 模式）
3. 尝试更简单的 XPath 表达式逐步调试
4. 检查是否有 JavaScript 动态加载的内容（morss 只能访问初始 HTML）

### 问题：URL 编码后的 XPath 不工作

**解决方案**：
1. 确保 `/` 替换为 `|`
2. 使用在线 URL 编码工具编码特殊字符
3. 测试时先用 CLI 命令验证 XPath 正确性
4. 在浏览器地址栏中完整复制粘贴 URL（不要手动输入）

### 问题：提取的内容不完整或包含多余内容

**解决方案**：
1. 使用更精确的 XPath（添加更多限定条件）
2. 调整相对路径（使用 `./` 限定在当前节点内）
3. 使用 `text()` 只提取文本内容
4. 考虑使用 `--item_content` 让 morss 从链接页面提取完整内容

### 问题：时间格式无法识别

**解决方案**：
1. Morss 支持多种时间格式，但如果是特殊格式可能失败
2. 确保提取的是时间文本，而不是包含其他内容的元素
3. 检查是否提取了正确的属性（如 `@datetime` vs `text()`）

## 预定义规则

Morss 在 `feedify.ini` 中预定义了一些常用网站的规则，包括：

- Twitter
- Google 搜索
- DuckDuckGo 搜索
- 标准 RSS/Atom 格式

你可以参考这些规则来学习如何编写自定义规则：

```bash
# 查看预定义规则
cat /path/to/morss/morss/feedify.ini
```

## 进一步学习

### XPath 教程资源

- [W3Schools XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)（英文）
- [MDN XPath 文档](https://developer.mozilla.org/zh-CN/docs/Web/XPath)（中文）
- [XPath 在线测试工具](https://www.freeformatter.com/xpath-tester.html)

### 实践建议

1. 从简单的网站开始练习
2. 先在浏览器控制台测试 XPath
3. 使用 CLI 模式调试，确认无误后再转换为 Web URL
4. 保存成功的规则配置供以后使用

## 总结

XPath 自定义订阅源是 Morss 最强大的功能之一，让你可以：

✅ 为任何网站创建 RSS 订阅源
✅ 精确控制提取哪些内容
✅ 组合多个数据源
✅ 过滤和转换内容

关键要点：
1. `--items` 是唯一必需的参数
2. 在 Web URL 中，`/` 必须替换为 `|`
3. 特殊字符需要 URL 编码
4. HTML 模式支持简化的 class 匹配语法
5. 使用浏览器开发者工具辅助编写 XPath

通过掌握 XPath 规则，你可以为几乎任何网站创建自定义 RSS 订阅源！
