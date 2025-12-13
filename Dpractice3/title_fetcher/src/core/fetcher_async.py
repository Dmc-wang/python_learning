# 异步基础 - 理解async/await
import asyncio
import httpx
from selectolax.parser import HTMLParser

import sys
from pathlib import Path

# 计算并插入src路径
src_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(src_path))

from utils.logger import logger

async def fetch_title_async(url: str) -> dict:
    """
    异步版本：理解async/await的本质
    """
    logger.debug(f"开始爬取: {url}")

    # 知识点：AsyncClient是异步上下文管理器
    async with httpx.AsyncClient(timeout = 5.0, follow_redirects = True) as client:
        try:
            # await：挂起当前协程，等待网络I/O完成
            resp = await client.get(url)

            tree = HTMLParser(resp.text)
            title_node = tree.css_first("title")

            logger.info(f"✅ 成功: {str(resp.url)} -> {title_node.text(deep = True)[:40]}")

            return {
                "url": str(resp.url),
                "title": title_node.text(deep = True) if title_node else "",
                "status_code": resp.status_code,
                "error": None
            }

        except Exception as e:
            logger.error(f"❌ 失败: {url} - {e}")
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
        "https://example.com",
        "https://baidu.com",
        "https://example.com"
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