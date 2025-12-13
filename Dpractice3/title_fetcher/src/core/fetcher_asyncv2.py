# 批量爬取与进度条
import asyncio
import time
import httpx
from selectolax.parser import HTMLParser
from tqdm.asyncio import tqdm_asyncio

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

async def batch_fetch(urls: list[str], max_concurrent: int = 10) -> list[dict]:
    """
    带并发控制的批量爬取
    知识点：信号量（Semaphore)控制并发
    """
    # 信号量：限制同时运行的协程数量
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url: str):
        async with semaphore:
            return await fetch_title_async(url)

    # 创建所有任务
    tasks = [fetch_with_semaphore(url) for url in urls]

    # tqdm_asyncio.gather：带进度条的并发执行
    results = await tqdm_asyncio.gather(
        *tasks,
        desc = "爬取进度",
        total = len(urls)
    )

    for r in results:
        print(f"✓ {r['url'][:40]} {r['title'][:40]} -> {r['status_code']}")

    return results

async def test_batch():
    # 生成100个测试URL
    # test_urls = [f"https://httpbingo.org/status/200" for _ in range(10)]
    test_urls = [f"https://baidu.com" for _ in range(10)]

    start1 = time.time()
    results = await batch_fetch(test_urls, max_concurrent = 20)
    end = time.time()

    print(f"\n爬取100个页面，耗时：{end - start1:.2f}秒")
    print(f"成功：{sum(1 for r in results if r['status_code'] == 200)}个")

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
    # asyncio.run(main())
    asyncio.run(test_batch())