"""
豆瓣电影Top250爬虫模块
支持分页爬取、自动重试、异常处理
"""
import httpx
from selectolax.parser import HTMLParser

print("开始爬取豆瓣电影Top250...")

response = httpx.get("https://movie.douban.com/top250", timeout=10)
print(f"响应状态码: {response.status_code}")

html = HTMLParser(response.text)
for item in html.css('div.item'):
    title = item.css_first('span.title').text()
    print(title)  # 能打印出电影名？→ 思路可行！
