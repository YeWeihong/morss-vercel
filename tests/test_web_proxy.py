import pytest

from morss.morss import Options, web_proxy_join


class MockItem:
    """Mock item for testing ItemFix"""
    def __init__(self, link, title=None, desc=None, content=None):
        self.link = link
        self.title = title
        self.desc = desc
        self.content = content
        self.NSMAP = {}
    
    def rule_str(self, rule):
        return None


def test_web_proxy_join_basic():
    """Test basic web_proxy_join functionality"""
    web_proxy = "https://proxy.com/view/http://target.com"
    relative_link = "/foo/bar.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    assert result == "https://proxy.com/view/http://target.com/foo/bar.html"


def test_web_proxy_join_with_trailing_slash():
    """Test web_proxy_join with trailing slash in proxy"""
    web_proxy = "https://proxy.com/view/http://target.com/"
    relative_link = "/foo/bar.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    assert result == "https://proxy.com/view/http://target.com/foo/bar.html"


def test_web_proxy_join_without_leading_slash():
    """Test web_proxy_join with relative link missing leading slash"""
    web_proxy = "https://proxy.com/view/http://target.com"
    relative_link = "foo/bar.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    assert result == "https://proxy.com/view/http://target.com/foo/bar.html"


def test_web_proxy_join_both_slashes():
    """Test web_proxy_join with both trailing and leading slashes"""
    web_proxy = "https://proxy.com/view/http://target.com/"
    relative_link = "/foo/bar.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    # Should not have double slash
    assert result == "https://proxy.com/view/http://target.com/foo/bar.html"
    assert "//" not in result.replace("https://", "").replace("http://", "")


def test_web_proxy_join_complex_proxy():
    """Test web_proxy_join with complex proxy URL"""
    web_proxy = "https://sitedl.westpan.me/123/https/t66y.com"
    relative_link = "/article/123.html"
    
    result = web_proxy_join(web_proxy, relative_link)
    
    assert result == "https://sitedl.westpan.me/123/https/t66y.com/article/123.html"


def test_itemfix_with_web_proxy():
    """Test ItemFix function with web_proxy option"""
    from morss.morss import ItemFix
    
    # Create mock item with relative link
    item = MockItem(link="/article/123.html", title="Test Article")
    
    # Create options with web_proxy
    options = Options(web_proxy="https://proxy.com/view/http://target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="http://target.com")
    
    # Check that link was resolved using web_proxy
    assert result.link == "https://proxy.com/view/http://target.com/article/123.html"


def test_itemfix_without_web_proxy():
    """Test ItemFix function without web_proxy option (standard behavior)"""
    from morss.morss import ItemFix
    
    # Create mock item with relative link
    item = MockItem(link="/article/123.html", title="Test Article")
    
    # Create options without web_proxy
    options = Options()
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="http://target.com/feed")
    
    # Check that link was resolved using standard urljoin
    assert result.link == "http://target.com/article/123.html"


def test_itemfix_with_absolute_link_and_web_proxy():
    """Test ItemFix function with absolute link and web_proxy - external URLs should ALSO be proxied"""
    from morss.morss import ItemFix
    
    # Create mock item with absolute link from external domain
    item = MockItem(link="http://example.com/article/123.html", title="Test Article")
    
    # Create options with web_proxy
    options = Options(web_proxy="https://proxy.com/view/http://target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="http://target.com")
    
    # Absolute URLs from external domains should ALSO be proxied when web_proxy is used
    # The proxy format should convert the external URL to use the same proxy mechanism
    assert result.link == "https://proxy.com/view/http://example.com/article/123.html"


def test_itemfix_with_absolute_link_from_target_domain_and_web_proxy():
    """Test ItemFix function with absolute link from target domain with web_proxy - should convert to proxy URL"""
    from morss.morss import ItemFix
    
    # Create mock item with absolute link from target domain
    item = MockItem(link="http://target.com/article/123.html", title="Test Article")
    
    # Create options with web_proxy
    options = Options(web_proxy="https://proxy.com/view/http://target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="http://target.com")
    
    # Absolute URLs from target domain should be converted to use proxy
    assert result.link == "https://proxy.com/view/http://target.com/article/123.html"


def test_itemfix_with_absolute_link_from_target_domain_pattern2():
    """Test ItemFix with absolute link from target domain using protocol/domain pattern"""
    from morss.morss import ItemFix
    
    # Create mock item with absolute link from target domain
    item = MockItem(link="https://www.target.com/htm_data/2601/", title="Test Article")
    
    # Create options with web_proxy (pattern 2: https/domain)
    options = Options(web_proxy="https://proxy.saha.qzz.io/https/www.target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="https://www.target.com")
    
    # Absolute URLs from target domain should be converted to use proxy
    assert result.link == "https://proxy.saha.qzz.io/https/www.target.com/htm_data/2601/"


def test_itemfix_with_absolute_link_from_external_domain_pattern2():
    """Test ItemFix with absolute link from external domain using protocol/domain pattern"""
    from morss.morss import ItemFix
    
    # Create mock item with absolute link from external domain
    item = MockItem(link="https://external.com/page", title="Test Article")
    
    # Create options with web_proxy (pattern 2: https/domain)
    options = Options(web_proxy="https://proxy.saha.qzz.io/https/www.target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="https://www.target.com")
    
    # Absolute URLs from external domains should also be proxied
    assert result.link == "https://proxy.saha.qzz.io/https/external.com/page"


def test_convert_absolute_url_to_proxy_pattern1():
    """Test convert_absolute_url_to_proxy with pattern 1 (embedded ://)"""
    from morss.morss import convert_absolute_url_to_proxy
    
    web_proxy = "https://proxy.com/view/http://target.com"
    absolute_url = "https://example.com/page"
    
    result = convert_absolute_url_to_proxy(web_proxy, absolute_url)
    
    assert result == "https://proxy.com/view/https://example.com/page"


def test_convert_absolute_url_to_proxy_pattern2():
    """Test convert_absolute_url_to_proxy with pattern 2 (protocol/domain)"""
    from morss.morss import convert_absolute_url_to_proxy
    
    web_proxy = "https://proxy.saha.qzz.io/https/www.target.com"
    absolute_url = "https://external.com/page/123"
    
    result = convert_absolute_url_to_proxy(web_proxy, absolute_url)
    
    assert result == "https://proxy.saha.qzz.io/https/external.com/page/123"


def test_convert_absolute_url_to_proxy_pattern2_with_path():
    """Test convert_absolute_url_to_proxy with pattern 2 and arbitrary path in proxy"""
    from morss.morss import convert_absolute_url_to_proxy
    
    web_proxy = "https://sitedl.westpan.me/123/https/t66y.com"
    absolute_url = "https://cdn.example.com/image.jpg"
    
    result = convert_absolute_url_to_proxy(web_proxy, absolute_url)
    
    assert result == "https://sitedl.westpan.me/123/https/cdn.example.com/image.jpg"
