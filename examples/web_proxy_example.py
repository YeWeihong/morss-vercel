#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Proxy 功能示例脚本

这个脚本演示如何使用 morss 的 web_proxy 功能来通过代理访问网站
"""

from morss.morss import Options, web_proxy_join, extract_target_from_proxy

def example_1_basic_web_proxy_join():
    """示例 1: 基本的 web_proxy_join 使用"""
    print("\n=== 示例 1: 基本的 URL 拼接 ===")
    
    web_proxy = "https://proxy.com/view/http://target.com"
    relative_link = "/article/123.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    print(f"代理前缀: {web_proxy}")
    print(f"相对链接: {relative_link}")
    print(f"拼接结果: {result}")
    print(f"✓ 成功拼接为代理 URL")


def example_2_extract_target():
    """示例 2: 从代理 URL 中提取目标网站"""
    print("\n=== 示例 2: 提取目标网站 ===")
    
    test_cases = [
        "https://proxy.saha.qzz.io/https/misskon.com",
        "https://sitedl.westpan.me/123/https/t66y.com",
        "https://proxy.com/view/http://target.com",
    ]
    
    for web_proxy in test_cases:
        target = extract_target_from_proxy(web_proxy)
        print(f"\n代理 URL: {web_proxy}")
        print(f"目标网站: {target}")


def example_3_complex_scenario():
    """示例 3: 复杂场景 - 处理不同类型的链接"""
    print("\n=== 示例 3: 处理不同类型的链接 ===")
    
    web_proxy = "https://morss.saha.qzz.io/https/misskon.com"
    target_base = extract_target_from_proxy(web_proxy)
    
    links = [
        ("/article/1", "相对链接"),
        ("https://misskon.com/article/2", "目标域的绝对链接"),
        ("https://example.com/page", "外部域的绝对链接"),
    ]
    
    print(f"代理前缀: {web_proxy}")
    print(f"目标域: {target_base}")
    print()
    
    for link, description in links:
        print(f"\n原始链接: {link} ({description})")
        
        # 判断链接类型
        if not link.startswith("http"):
            # 相对链接
            result = web_proxy_join(web_proxy, link)
            print(f"处理方式: 拼接代理前缀")
            print(f"结果: {result}")
        elif link.startswith(target_base):
            # 目标域的绝对链接
            path = link[len(target_base):]
            result = web_proxy_join(web_proxy, path)
            print(f"处理方式: 转换为代理 URL")
            print(f"结果: {result}")
        else:
            # 外部域的绝对链接
            result = link
            print(f"处理方式: 保持不变")
            print(f"结果: {result}")


def example_4_url_encoding():
    """示例 4: URL 编码示例"""
    print("\n=== 示例 4: URL 编码转换 ===")
    
    # 原始 XPath 规则
    original_items = "//div[@class='post']"
    original_web_proxy = "https://proxy.com/https/target.com"
    
    # 转换为 URL 格式（使用管道符替代斜杠）
    url_items = original_items.replace('/', '|')
    url_web_proxy = original_web_proxy.replace('/', '|')
    
    print(f"\n原始 items: {original_items}")
    print(f"URL 格式: {url_items}")
    print()
    print(f"原始 web_proxy: {original_web_proxy}")
    print(f"URL 格式: {url_web_proxy}")
    
    # 模拟完整 URL（简化版本，实际使用时还需要 URL 编码）
    morss_url = f":items={url_items}:web_proxy={url_web_proxy}"
    print(f"\nMorss URL 参数: {morss_url}")
    print(f"\n注意: 实际使用时还需要对特殊字符进行 URL 编码")


def example_5_with_options():
    """示例 5: 使用 Options 对象"""
    print("\n=== 示例 5: 使用 Options 对象 ===")
    
    # 创建带有 web_proxy 的 Options 对象
    options = Options(
        web_proxy="https://proxy.com/https/target.com",
        items="//article[@class='post']",
        item_title="./h2",
        item_link="./a/@href",
        mode="html"
    )
    
    print(f"web_proxy: {options.web_proxy}")
    print(f"items: {options.items}")
    print(f"item_title: {options.item_title}")
    print(f"item_link: {options.item_link}")
    print(f"mode: {options.mode}")
    print()
    print(f"✓ Options 对象配置完成")
    print(f"✓ 可以传递给 morss.process() 或 FeedFetch() 使用")


if __name__ == "__main__":
    print("=" * 60)
    print("Morss Web Proxy 功能示例")
    print("=" * 60)
    
    example_1_basic_web_proxy_join()
    example_2_extract_target()
    example_3_complex_scenario()
    example_4_url_encoding()
    example_5_with_options()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("详细文档请参考: WEB_PROXY_FEATURE_CN.md")
    print("=" * 60)
