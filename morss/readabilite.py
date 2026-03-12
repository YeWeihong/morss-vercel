# This file is part of morss
#
# Copyright (C) 2013-2020 pictuga <contact@pictuga.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

import html as _html_module
import json
import re
from urllib.parse import urljoin

import bs4.builder._lxml
import lxml.etree
import lxml.html
import lxml.html.soupparser

# 尝试导入 trafilatura 作为主提取引擎；若未安装则退回原有算法
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

# trafilatura 提取结果的最短有效长度（字符数）；低于此值视为提取失败，回退到原有算法
MIN_TRAFILATURA_RESULT_LENGTH = 200

# 图片页识别阈值（字符数）；trafilatura 结果低于此值时启用图片提取模式
PHOTO_PAGE_THRESHOLD = 150

# BeautifulSoup 图片筛选的最小宽度（像素）；明确小于此值的图片视为图标/缩略图
MIN_IMAGE_WIDTH = 400

# 用于过滤广告/logo/图标等无意义图片的 URL 关键词
_BAD_IMAGE_RE = re.compile(
    r'ad[s_/-]|logo|avatar|icon|banner|tracking|pixel|1x1|spinner|placeholder',
    re.I,
)

# 匹配 og:image meta 标签（两种属性顺序均支持）
_OG_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:'
    r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']'
    r'|content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']'
    r')',
    re.I | re.S,
)

# 匹配 <img src="..."> 中的 src 属性（含 <img> 整体替换）
_IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
_IMG_SRC_ATTR_RE = re.compile(r'(<img\b[^>]+\bsrc=["\'])([^"\']+)(["\'])', re.I)

# trafilatura 使用 <graphic> 标签表示图片，需转换为标准 <img>
_GRAPHIC_TAG_RE = re.compile(r'<graphic\b([^>]*)>', re.I)

# Markdown 格式的图片引用：![alt](url)
_MARKDOWN_IMAGE_RE = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')


def _is_valid_image_src(src):
    """判断图片 URL 是否有效（排除 data URI、广告图片等）。"""
    if not src or src.startswith('data:'):
        return False
    if _BAD_IMAGE_RE.search(src):
        return False
    return True


def _get_og_image(html_str, base_url=None):
    """从原始 HTML 中提取 og:image 元标签中的图片 URL。"""
    m = _OG_IMAGE_RE.search(html_str)
    if m:
        src = m.group(1) or m.group(2)
        if src:
            return urljoin(base_url, src) if base_url else src
    return None


def _convert_graphic_to_img(html_str):
    """将 trafilatura 输出中的 <graphic ...> 标签转换为标准 <img ...> 标签。"""
    return _GRAPHIC_TAG_RE.sub(lambda m: '<img' + m.group(1) + '>', html_str)


def _extract_image_srcs(html_str, base_url=None):
    """从 HTML 字符串中提取所有 <img src="..."> 的绝对 URL 列表（过滤无效图片）。"""
    srcs = _IMG_SRC_RE.findall(html_str)
    result = []
    for src in srcs:
        if not _is_valid_image_src(src):
            continue
        result.append(urljoin(base_url, src) if base_url else src)
    return result


def _extract_images_bs4(html_str, base_url=None):
    """使用 BeautifulSoup 从原始 HTML 提取大图列表（宽度 ≥400 或无尺寸信息）。"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_str, 'html.parser')
        images = []
        for img in soup.find_all('img'):
            src = (
                img.get('src')
                or img.get('data-src')
                or img.get('data-original')
                or ''
            ).strip()
            if not src or not _is_valid_image_src(src):
                continue
            if base_url:
                src = urljoin(base_url, src)
            # 过滤明显小图（宽度 < MIN_IMAGE_WIDTH px）
            try:
                width = int(img.get('width', 0))
                if 0 < width < MIN_IMAGE_WIDTH:
                    continue
            except (ValueError, TypeError):
                pass
            images.append(src)
        return images
    except Exception:
        return []


def _make_images_absolute(html_str, base_url):
    """将 HTML 字符串中所有 <img src="..."> 的相对 URL 替换为绝对 URL。"""
    def _replace(m):
        abs_src = urljoin(base_url, m.group(2))
        return m.group(1) + abs_src + m.group(3)
    return _IMG_SRC_ATTR_RE.sub(_replace, html_str)


class CustomTreeBuilder(bs4.builder._lxml.LXMLTreeBuilder):
    def default_parser(self, encoding):
        return lxml.html.HTMLParser(target=self, remove_comments=True, remove_pis=True, encoding=encoding)


def parse(data, encoding=None):
    kwargs = {'from_encoding': encoding} if encoding else {}
    return lxml.html.soupparser.fromstring(data, builder=CustomTreeBuilder, **kwargs)


def count_words(string):
    """ Quick word count

    Simply assumes that all words are 5 letter long.
    And so in about every language (sorry chinese).
    Basically skips spaces in the count. """

    if string is None:
        return 0

    string = string.strip()

    i = 0
    count = 0

    try:
        while True:
            if string[i] not in "\r\n\t ":
                count += 1
                i += 6
            else:
                i += 1
    except IndexError:
        pass

    return count


def count_content(node):
    # count words and imgs
    return count_words(node.text_content()) + len(node.findall('.//img'))


class_bad = ['comment', 'community', 'extra', 'foot',
    'sponsor', 'pagination', 'pager', 'tweet', 'twitter', 'com-', 'masthead',
    'media', 'meta', 'related', 'shopping', 'tags', 'tool', 'author', 'about',
    'head', 'robots-nocontent', 'combx', 'disqus', 'menu', 'remark', 'rss',
    'shoutbox', 'sidebar', 'ad-', 'agegate', 'popup', 'sharing', 'share',
    'social', 'contact', 'footnote', 'outbrain', 'promo', 'scroll', 'hidden',
    'widget', 'hide']

regex_bad = re.compile('|'.join(class_bad), re.I)

class_good = ['and', 'article', 'body', 'column', 'main',
    'shadow', 'content', 'entry', 'hentry', 'main', 'page', 'pagination',
    'post', 'text', 'blog', 'story', 'par', 'editorial']

regex_good = re.compile('|'.join(class_good), re.I)


tags_dangerous = ['script', 'head', 'iframe', 'object', 'style', 'link', 'meta']

tags_junk = tags_dangerous + ['noscript', 'param', 'embed', 'layer', 'applet',
    'form', 'input', 'textarea', 'button', 'footer']

tags_bad = tags_junk + ['a', 'aside']

tags_good = ['h1', 'h2', 'h3', 'article', 'p', 'cite', 'section', 'figcaption',
    'figure', 'em', 'strong', 'pre', 'br', 'hr', 'headline']

tags_meaning = ['a', 'abbr', 'address', 'acronym', 'audio', 'article', 'aside',
    'b', 'bdi', 'bdo', 'big', 'blockquote', 'br', 'caption', 'cite', 'center',
    'code', 'col', 'colgroup', 'data', 'dd', 'del', 'details', 'description',
    'dfn', 'dl', 'font', 'dt', 'em', 'figure', 'figcaption', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd', 'li', 'main', 'mark',
    'nav', 'ol', 'p', 'pre', 'q', 'ruby', 'rp', 'rt', 's', 'samp', 'small',
    'source', 'strike', 'strong', 'sub', 'summary', 'sup', 'table', 'tbody',
    'td', 'tfoot', 'th', 'thead', 'time', 'tr', 'track', 'tt', 'u', 'ul', 'var',
    'wbr', 'video']
    # adapted from tt-rss source code, to keep even as shells

tags_void = ['img', 'hr', 'br'] # to keep even if empty


attributes_fine = ['title', 'src', 'href', 'type', 'value']


def score_node(node):
    " Score individual node "

    score = 0
    class_id = (node.get('class') or '') + (node.get('id') or '')

    if (isinstance(node, lxml.html.HtmlComment)
            or isinstance(node, lxml.html.HtmlProcessingInstruction)):
        return 0

    if node.tag in tags_dangerous:
        return 0

    if node.tag in tags_junk:
        score += -1 # actuall -2 as tags_junk is included tags_bad

    if node.tag in tags_bad:
        score += -1

    if regex_bad.search(class_id):
        score += -1

    if node.tag in tags_good:
        score += 4

    if regex_good.search(class_id):
        score += 3

    wc = count_words(node.text_content())

    score += min(int(wc/10), 3) # give 1pt bonus for every 10 words, max of 3

    if wc != 0:
        wca = count_words(' '.join([x.text_content() for x in node.findall('.//a')]))
        score = score * ( 1 - 2 * float(wca)/wc )

    return score


def score_all(node):
    " Fairly dumb loop to score all worthwhile nodes. Tries to be fast "

    for child in node:
        score = score_node(child)
        set_score(child, score, 'morss_own_score')

        if score > 0 or len(list(child.iterancestors())) <= 2:
            spread_score(child, score)
            score_all(child)


def set_score(node, value, label='morss_score'):
    try:
        node.attrib[label] = str(float(value))

    except KeyError:
        # catch issues with e.g. html comments
        pass


def get_score(node):
    return float(node.attrib.get('morss_score', 0))


def incr_score(node, delta):
    set_score(node, get_score(node) + delta)


def get_all_scores(node):
    return {x:get_score(x) for x in list(node.iter()) if get_score(x) != 0}


def spread_score(node, score):
    " Spread the node's score to its parents, on a linear way "

    delta = score / 2

    for ancestor in [node,] + list(node.iterancestors()):
        if score >= 1 or ancestor is node:
            incr_score(ancestor, score)

            score -= delta

        else:
            break


def clean_root(root, keep_threshold=None):
    for node in list(root):
        # bottom-up approach, i.e. starting with children before cleaning current node
        clean_root(node, keep_threshold)
        clean_node(node, keep_threshold)


def clean_node(node, keep_threshold=None):
    parent = node.getparent()

    # remove comments
    if (isinstance(node, lxml.html.HtmlComment)
            or isinstance(node, lxml.html.HtmlProcessingInstruction)):
        parent.remove(node)
        return

    if parent is None:
        # this is <html/> (or a removed element waiting for GC)
        return

    # remove dangerous tags, no matter what
    if node.tag in tags_dangerous:
        parent.remove(node)
        return

    # high score, so keep
    if keep_threshold is not None and keep_threshold > 0 and get_score(node) >= keep_threshold:
        return

    gdparent = parent.getparent()

    # remove shitty tags
    if node.tag in tags_junk:
        parent.remove(node)
        return

    # remove shitty class/id FIXME TODO too efficient, might want to add a toggle
    class_id = node.get('class', '') + node.get('id', '')
    if len(regex_bad.findall(class_id)) >= 2:
        node.getparent().remove(node)
        return

    # remove shitty link
    if node.tag == 'a' and len(list(node.iter())) > 3:
        parent.remove(node)
        return

    # remove if too many kids & too high link density
    wc = count_words(node.text_content())
    if wc != 0 and len(list(node.iter())) > 3:
        wca = count_words(' '.join([x.text_content() for x in node.findall('.//a')]))
        if float(wca)/wc > 0.8:
            parent.remove(node)
            return

    # squash text-less elements shells
    if node.tag in tags_void:
        # keep 'em
        pass
    elif node.tag in tags_meaning:
        # remove if content-less
        if not count_content(node):
            parent.remove(node)
            return
    else:
        # squash non-meaningful if no direct text
        content = (node.text or '') + ' '.join([child.tail or '' for child in node])
        if not count_words(content):
            node.drop_tag()
            return

    # for http://vice.com/fr/
    if node.tag == 'img' and 'data-src' in node.attrib:
        node.attrib['src'] = node.attrib['data-src']

    # clean the node's attributes
    for attrib in node.attrib:
        if attrib not in attributes_fine:
            del node.attrib[attrib]

    # br2p
    if node.tag == 'br':
        if gdparent is None:
            return

        if not count_words(node.tail):
            # if <br/> is at the end of a div (to avoid having <p/>)
            return

        else:
            # set up new node
            new_node = lxml.html.Element(parent.tag)
            new_node.text = node.tail

            for child in node.itersiblings():
                new_node.append(child)

            # delete br
            node.tail = None
            parent.remove(node)

            gdparent.insert(gdparent.index(parent)+1, new_node)


def lowest_common_ancestor(node_a, node_b, max_depth=None):
    ancestors_a = list(node_a.iterancestors())
    ancestors_b = list(node_b.iterancestors())

    if max_depth is not None:
        ancestors_a = ancestors_a[:max_depth]
        ancestors_b = ancestors_b[:max_depth]

    ancestors_a.insert(0, node_a)
    ancestors_b.insert(0, node_b)

    for ancestor_a in ancestors_a:
        if ancestor_a in ancestors_b:
            return ancestor_a

    return node_a # should always find one tho, at least <html/>, but needed for max_depth


def get_best_node(html, threshold=5):
    # score all nodes
    score_all(html)

    # rank all nodes (largest to smallest)
    ranked_nodes = sorted(html.iter(), key=lambda x: get_score(x), reverse=True)

    # minimum threshold
    if not len(ranked_nodes) or get_score(ranked_nodes[0]) < threshold:
        return None

    # take common ancestor or the two highest rated nodes
    if len(ranked_nodes) > 1:
        best = lowest_common_ancestor(ranked_nodes[0], ranked_nodes[1], 3)

    else:
        best = ranked_nodes[0]

    return best


def _get_article_readabilite(data, url=None, encoding_in=None, encoding_out='unicode', debug=False, threshold=5, xpath=None):
    """原有 readabilite 启发式算法，返回 unicode 字符串或 None。"""
    html = parse(data, encoding_in)

    if xpath is not None:
        xpath_match = html.xpath(xpath)

        if len(xpath_match):
            best = xpath_match[0]

        else:
            best = get_best_node(html, threshold)

    else:
        best = get_best_node(html, threshold)

    if best is None:
        return None

    # clean up
    if not debug:
        keep_threshold = get_score(best) * 3/4
        clean_root(best, keep_threshold)

    # check for spammy content (links only)
    wc = count_words(best.text_content())
    wca = count_words(' '.join([x.text_content() for x in best.findall('.//a')]))

    if not debug and (wc - wca < 50 or float(wca) / wc > 0.3):
        return None

    # fix urls
    if url:
        best.make_links_absolute(url)

    raw = lxml.etree.tostring(best if not debug else html, method='html', encoding='unicode')
    return raw


def _get_article_data(data, url=None, encoding_in=None, debug=False, threshold=5, xpath=None):
    """内部使用的文章提取函数，返回包含正文和图片信息的字典。

    Returns:
        dict with keys:
            'content'    : 提取到的 HTML 字符串（unicode），失败时为 None
            'main_image' : 主图片 URL（og:image 优先），无则为 None
            'images'     : 正文中所有图片的绝对 URL 列表
    """
    # 统一转换为字符串
    if isinstance(data, (bytes, bytearray)):
        html_str = data.decode(encoding_in or 'utf-8', errors='replace')
    else:
        html_str = data

    # 优先从原始页面中提取 og:image
    main_image = _get_og_image(html_str, url)
    content_html = None
    images = []

    # ── 第一步：尝试 trafilatura（仅在非调试、非自定义 xpath 模式下）────────────
    if TRAFILATURA_AVAILABLE and not debug and xpath is None:
        try:
            trafilatura_result = trafilatura.extract(
                html_str,
                url=url,
                include_comments=False,
                include_formatting=True,
                include_images=True,
                output_format='html',
                favor_recall=True,
            )

            if trafilatura_result and len(trafilatura_result) >= PHOTO_PAGE_THRESHOLD:
                # 结果足够丰富：转换 <graphic> → <img>，提取图片列表
                content_html = _convert_graphic_to_img(trafilatura_result)
                images = _extract_image_srcs(content_html, url)
                if not main_image and images:
                    main_image = images[0]

            else:
                # 结果过短（图片为主页面）：切换图片提取模式
                # 先尝试 trafilatura JSON 格式（text 字段包含 Markdown 图片引用）
                try:
                    json_result = trafilatura.extract(
                        html_str,
                        url=url,
                        include_images=True,
                        output_format='json',
                        include_formatting=True,
                        favor_recall=True,
                    )
                    if json_result:
                        json_data = json.loads(json_result)
                        md_srcs = _MARKDOWN_IMAGE_RE.findall(json_data.get('text', ''))
                        images = [
                            urljoin(url, src) if url else src
                            for src in md_srcs
                            if _is_valid_image_src(src)
                        ]
                except Exception:
                    pass

                # 若 JSON 方式未找到图片，回退到 BeautifulSoup 解析原始 HTML
                if not images:
                    images = _extract_images_bs4(html_str, url)

                if images:
                    if not main_image:
                        main_image = images[0]
                    # 生成以图片为主的简单 HTML（URL 转义防止 XSS）
                    content_html = '\n'.join(
                        '<p><img src="{}" alt=""/></p>'.format(_html_module.escape(img, quote=True))
                        for img in images
                    )
                elif trafilatura_result:
                    # 有短结果但无图：保留短结果
                    content_html = _convert_graphic_to_img(trafilatura_result)

        except Exception:
            # trafilatura 任何异常都回退到 readabilite，保证函数不崩溃
            pass
    # ────────────────────────────────────────────────────────────────────────────

    # ── 第二步（兜底）：原有 readabilite 启发式算法 ──────────────────────────────
    if content_html is None:
        content_html = _get_article_readabilite(
            data, url=url, encoding_in=encoding_in, debug=debug,
            threshold=threshold, xpath=xpath,
        )
        if content_html:
            # 从 readabilite 结果中补充图片列表
            images = _extract_image_srcs(content_html, url)
            if not main_image and images:
                main_image = images[0]
    # ────────────────────────────────────────────────────────────────────────────

    # 确保正文中所有图片 src 为绝对 URL
    if content_html and url:
        content_html = _make_images_absolute(content_html, url)

    return {'content': content_html, 'main_image': main_image, 'images': images}


def get_article(data, url=None, encoding_in=None, encoding_out='unicode', debug=False, threshold=5, xpath=None):
    " Input a raw html string, returns a raw html string of the article "

    result = _get_article_data(
        data, url=url, encoding_in=encoding_in, debug=debug,
        threshold=threshold, xpath=xpath,
    )
    content = result['content']

    if content is None:
        return None

    if encoding_out == 'unicode':
        return content
    else:
        return content.encode(encoding_out)


def get_article_trafilatura_only(data, url=None, encoding_in=None):
    """仅使用 trafilatura 提取正文，供调试对比使用（不影响生产逻辑）。"""
    if not TRAFILATURA_AVAILABLE:
        return None
    if isinstance(data, bytes):
        html_str = data.decode(encoding_in or 'utf-8', errors='replace')
    else:
        html_str = data
    return trafilatura.extract(
        html_str,
        url=url,
        include_comments=False,
        include_formatting=True,
        output_format='html',
        favor_recall=True,
    )


if __name__ == '__main__':
    import sys

    from . import crawler

    req = crawler.adv_get(sys.argv[1] if len(sys.argv) > 1 else 'https://morss.it')
    article = get_article(req['data'], url=req['url'], encoding_in=req['encoding'], encoding_out='unicode')

    if sys.flags.interactive:
        print('>>> Interactive shell: try using `article`')

    else:
        print(article)
