# 异步基础 - 理解async/await
import asyncio
import httpx
from selectolax.parser import HTMLParser

async def fetch_title_async(url: str) -> dict:
    """
    异步版本：理解async/await的本质
    """

    # 知识点：AsyncClient是异步上下文管理器
    async with httpx.AsyncClient(timeout = 5.0, follow_redirects = True) as client:
        try:
            # await：挂起当前协程，等待网络I/O完成
            resp = await client.get(url)

            tree = HTMLParser(resp.text)
            title_node = tree.css_first("title")

            return {
                "url": str(resp.url),
                "title": title_node.text(deep = True) if title_node else "",
                "status_code": resp.status_code,
                "error": None
            }

        except Exception as e:
            return {
                "url": str(url),
                "title": "",
                "status_code": 0,
                "error": str(e)
            }

async def main():
    """
    异步入口函数：理解事件循环
    """
    urls = [
        "https://httpbin.org/delay/1",  # 这个URL会延迟1秒返回
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]

    # 知识点：创建多个协程任务
    tasks = [fetch_title_async(url) for url in urls]

    # 并发执行所有任务（总耗时≈1秒，而不是3秒）
    results = await asyncio.gather(*tasks)

    for r in results:
        print(f"✓ {r['url'][:40]} -> {r['status_code']}")

# 运行异步函数的标准方式
if __name__ == "__main__":
    # 知识点：asyncio.run()启动事件循环
    asyncio.run(main())