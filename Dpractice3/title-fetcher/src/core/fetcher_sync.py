# 同步版本 - 理解HTTP请求基础

import httpx
from selectolax.parser import HTMLParser

def fetch_title_sync(url: str) -> dict:
    """
    最简单的同步爬虫函数
    知识点：函数定义，异常处理，字典返回值
    """
    try:
        # 发送HTTP GET请求（知识点：HTTP协议、GET方法、超时机制）
        resp = httpx.get(url, timeout = 10.0, follow_redirects = True)

        # 解析HTML （知识点：HTML结构、title标签）
        tree = HTMLParser(resp.text)
        title_node = tree.css_first("title")

        return {
            "url": str(resp.url),
            "title": title_node.text(deep = True) if title_node else "",
            "status_code": resp.status_code
        }
    except Exception as e:
        # 异常处理：网络错误、超时、解析错误等
        return{
            "url": url,
            "title": "",
            "status_code": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    test_url =[
        "https://example.com",
        "https://baidu.com",
        "https://this-domain-does-not-exist-12345.com"
    ]
    result = fetch_title_sync(test_url[0])
    print(result)
    result = fetch_title_sync(test_url[1])
    print(result)
    result = fetch_title_sync(test_url[2])
    print(result)
