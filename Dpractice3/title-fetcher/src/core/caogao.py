# src/core/fetcher_async_real.py
import asyncio
import httpx
from selectolax.parser import HTMLParser
from typing import Dict, List
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_title_async_real(
        url: str,
        timeout: float = 15.0,
        semaphore: asyncio.Semaphore = None
) -> Dict:
    """
    真实场景异步爬虫（带并发控制）
    """
    # 前置清理
    url = url.strip()

    # 使用信号量限制并发
    if semaphore:
        async with semaphore:
            return await _do_fetch(url, timeout)
    else:
        return await _do_fetch(url, timeout)


async def _do_fetch(url: str, timeout: float) -> Dict:
    """实际执行爬取的逻辑"""
    try:
        logger.info(f"🌐 开始请求: {url}")

        # 配置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True
        ) as client:

            resp = await client.get(url, headers=headers)

            # 状态码检查
            if resp.status_code >= 400:
                logger.warning(f"⚠️ HTTP错误 {resp.status_code}: {url}")
                return {
                    "url": str(resp.url),
                    "title": "",
                    "status_code": resp.status_code,
                    "error": f"HTTP错误: {resp.status_code}",
                }

            # 解析HTML
            tree = HTMLParser(resp.text)

            # 多重标题提取策略
            title = ""
            for selector in ["title", "h1", 'meta[name="og:title"]']:
                node = tree.css_first(selector)
                if node:
                    if selector.startswith("meta"):
                        title = node.attributes.get("content", "")
                    else:
                        title = node.text(deep=True).strip()
                    if title:
                        break

            logger.info(f"✅ 成功: {url} -> {title[:30] or '(无标题)'}")

            return {
                "url": str(resp.url),
                "title": title,
                "status_code": resp.status_code,
                "error": None,
            }

    except Exception as e:
        logger.error(f"❌ 失败 {url}: {e}")
        return {
            "url": url,
            "title": "",
            "status_code": 0,
            "error": str(e)
        }


async def main_real():
    """主函数：测试真实网站并发"""

    # 真实网站列表
    real_urls = [
        "https://example.com",
        "https://www.github.com",
        "https://www.python.org",
        "https://httpbingo.org/json",
        "https://httpbingo.org/xml",
        "https://www.httpbingo.org/html",
        "https://www.wikipedia.org",
        "https://www.openai.com",
        "https://httpbingo.org/robots.txt",
        "https://httpbingo.org/status/200",
    ]

    print("🔥 真实网站并发测试...")
    print(f"{'=' * 70}")

    # 创建信号量：限制并发数（礼貌爬取）
    semaphore = asyncio.Semaphore(5)

    start = time.perf_counter()

    # 创建任务
    tasks = [fetch_title_async_real(url, semaphore=semaphore) for url in real_urls]

    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.perf_counter() - start

    # 统计结果
    success = sum(1 for r in results if r.get("error") is None)

    print(f"🎯 结果: {success}/{len(results)} 成功")
    print(f"⏱️  总耗时: {elapsed:.2f}秒")
    print(f"{'=' * 70}")

    # 打印详细结果
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("error") is None else "❌"
        title_preview = result.get("title", "")[:40] or result.get("error", "")
        print(f"{i:2d}. {status} [{result.get('status_code', 0):3d}] {title_preview}")

    print(f"{'=' * 70}")


# 运行
if __name__ == "__main__":
    asyncio.run(main_real())