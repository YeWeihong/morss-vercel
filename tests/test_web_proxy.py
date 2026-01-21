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
    """Test ItemFix function with absolute link and web_proxy - should NOT apply proxy to absolute URLs"""
    from morss.morss import ItemFix
    
    # Create mock item with absolute link
    item = MockItem(link="http://example.com/article/123.html", title="Test Article")
    
    # Create options with web_proxy
    options = Options(web_proxy="https://proxy.com/view/http://target.com")
    
    # Call ItemFix
    result = ItemFix(item, options, feedurl="http://target.com")
    
    # Absolute URLs should NOT be modified when web_proxy is used
    assert result.link == "http://example.com/article/123.html"
