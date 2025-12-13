import httpx
from urllib.parse import urljoin, urlparse


class RobotsChecker:
    """robots.txt检查器"""

    def __init__(self):
        self.parsers = {}  # 缓存robots.txt解析结果

    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        domain = urlparse(url).netloc

        if domain not in self.parsers:
            robots_url = urljoin(f"https://{domain}", "/robots.txt")
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(robots_url, timeout=5)
                    if resp.status_code == 200:
                        # 简单解析（生产环境可用urllib.robotparser）
                        if "User-agent: *" in resp.text and "Disallow: /" in resp.text:
                            self.parsers[domain] = False
                        else:
                            self.parsers[domain] = True
                    else:
                        self.parsers[domain] = True  # 没有robots.txt默认允许
            except:
                self.parsers[domain] = True

        return self.parsers[domain]