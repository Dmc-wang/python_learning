"""
豆瓣电影Top250爬虫模块
支持分页爬取、自动重试、异常处理
"""

import csv
import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any

import httpx
from selectolax.parser import HTMLParser

# ==================== 配置区域 ====================
# 根据记忆，您已熟悉基础配置，这次我们使用类封装

@dataclass
class DoubanConfig:
    """爬虫配置类"""
    base_url = "https://movie.douban.com/top250"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = 10.0  # 超时时间（秒）
    max_retries = 3  # 最大重试次数
    retry_delay = 2.0  # 重试延迟（秒）
    page_size = 25  # 每页电影数量
    max_pages = 10  # 最多爬取页数（共250部）


@dataclass
class Movie:
    """电影数据类"""
    rank: Optional[int] = None
    title: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    quote: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    actors: Optional[str] = None
    genres: Optional[str] = None
    duration: Optional[str] = None


# ==================== 核心爬虫类 ====================

class DoubanFetcher:
    """豆瓣电影爬虫类"""
    
    def __init__(self, config: Optional[DoubanConfig] = None):
        self.config = config or DoubanConfig()
        self.logger = self._setup_logger()
        self.client = httpx.Client(
            headers=self.config.headers,
            timeout=self.config.timeout,
            follow_redirects=True  # 根据记忆，您遇到过重定向问题
        )
    
    def _setup_logger(self) -> logging.Logger:
        """配置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # 控制台处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def fetch_page(self, start: int = 0) -> Optional[HTMLParser]:
        """
        获取单页HTML内容
        
        Args:
            start: 起始索引（0开始）
        
        Returns:
            解析后的HTML对象，失败返回None
        """
        url = f"{self.config.base_url}?start={start}"
        self.logger.info(f"正在请求: {url}")
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.get(url)
                
                # 检查状态码（根据记忆，您遇到过503问题）
                if response.status_code != 200:
                    self.logger.warning(
                        f"第{attempt + 1}次请求失败 - "
                        f"状态码: {response.status_code}"
                    )
                    time.sleep(self.config.retry_delay)
                    continue
                
                # 验证内容
                if "豆瓣电影 Top 250" not in response.text:
                    self.logger.warning("页面内容异常，可能被封禁或页面结构改变")
                    return None
                
                return HTMLParser(response.text)
                
            except Exception as e:
                self.logger.error(f"请求异常: {e}")
                time.sleep(self.config.retry_delay)
        
        self.logger.error(f"达到最大重试次数，放弃请求: {url}")
        return None
    
    def parse_page(self, html_parser: HTMLParser) -> List[Movie]:
        """
        解析单页电影数据
        
        Args:
            html_parser: HTML解析对象
        
        Returns:
            电影数据列表
        """
        movies = []
        
        # 根据记忆，您之前解析过豆瓣页面，这里使用更稳健的选择器
        movie_items = html_parser.css('div.item')
        
        if not movie_items:
            self.logger.warning("未找到电影条目，页面结构可能已改变")
            return movies
        
        for item in movie_items:
            try:
                movie = Movie()
                
                # 排名
                rank_elem = item.css_first('em')
                if rank_elem:
                    movie.rank = int(rank_elem.text())
                
                # 标题（主标题）
                title_elem = item.css_first('div.info div.hd a span.title')
                if title_elem:
                    movie.title = title_elem.text().strip()
                
                # 评分
                rating_elem = item.css_first('span.rating_num')
                if rating_elem:
                    movie.rating = float(rating_elem.text())
                
                # 评价人数
                star_elem = item.css_first('div.star')
                if star_elem:
                    # 评价人数在span文本中，如 "(123456人评价)"
                    rating_text = star_elem.text()
                    if "人评价" in rating_text:
                        # 提取数字部分
                        import re
                        match = re.search(r'(\d+)', rating_text)
                        if match:
                            movie.rating_count = int(match.group(1))
                
                # 简介
                quote_elem = item.css_first('p.quote span.inq')
                if quote_elem:
                    movie.quote = quote_elem.text().strip()
                
                # 其他信息（导演、年份等）
                info_elem = item.css_first('div.info div.bd p')
                if info_elem:
                    info_text = info_elem.text().strip()
                    # 按换行分割
                    lines = info_text.split('\n')
                    if len(lines) >= 2:
                        # 第一行：导演和演员
                        director_line = lines[0].strip()
                        if "导演:" in director_line:
                            parts = director_line.split("主演:")
                            movie.director = parts[0].replace("导演:", "").strip()
                            if len(parts) > 1:
                                movie.actors = parts[1].strip()
                        
                        # 第二行：年份、类型、时长
                        meta_line = lines[1].strip()
                        # 格式如："1994 / 美国 / 犯罪 剧情 / 142分钟"
                        meta_parts = meta_line.split(' / ')
                        if len(meta_parts) >= 3:
                            # 提取年份
                            try:
                                movie.year = int(meta_parts[0].strip())
                            except ValueError:
                                pass
                            
                            # 提取类型
                            movie.genres = meta_parts[2].strip()
                            
                            # 提取时长（如果有）
                            if len(meta_parts) > 3:
                                movie.duration = meta_parts[-1].strip()
                
                movies.append(movie)
                self.logger.debug(f"成功解析电影: {movie.rank} - {movie.title}")
                
            except Exception as e:
                self.logger.error(f"解析电影条目失败: {e}")
                continue
        
        self.logger.info(f"本页解析完成，共{len(movies)}部电影")
        return movies
    
    def fetch_all(self, max_pages: Optional[int] = None) -> List[Movie]:
        """
        爬取所有页面
        
        Args:
            max_pages: 最大页数,None则使用配置值
        
        Returns:
            所有电影数据
        """
        if max_pages is None:
            max_pages = self.config.max_pages
        
        all_movies = []
        
        self.logger.info(f"开始爬取，计划爬取{max_pages}页...")
        
        for page_num in range(max_pages):
            start = page_num * self.config.page_size
            self.logger.info(f"正在爬取第{page_num + 1}/{max_pages}页 (start={start})")
            
            html_parser = self.fetch_page(start)
            if not html_parser:
                self.logger.warning(f"第{page_num + 1}页获取失败，跳过")
                continue
            
            movies = self.parse_page(html_parser)
            all_movies.extend(movies)
            
            # 礼貌延迟，避免请求过快
            time.sleep(1.5)
        
        self.logger.info(f"爬取完成！共获取{len(all_movies)}部电影")
        return all_movies
    
    def save_to_csv(self, movies: List[Movie], filepath: Path):
        """
        保存为CSV文件
        """
        self.logger.info(f"正在保存数据到: {filepath}")
        
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            # 使用字典写入器
            fieldnames = [field for field in Movie.__dataclass_fields__.keys()]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for movie in movies:
                writer.writerow(asdict(movie))
        
        self.logger.info(f"数据保存完成！共{len(movies)}条记录")
    
    def close(self):
        """关闭HTTP客户端"""
        self.client.close()
        self.logger.info("HTTP客户端已关闭")


# ==================== 命令行接口 ====================

def main():
    """主入口函数"""
    # 配置日志级别
    logging.basicConfig(level = logging.INFO)
    
    # 创建爬虫实例
    fetcher = DoubanFetcher()
    fetcher.config.max_pages = 2
    
    try:
        # 爬取数据
        movies = fetcher.fetch_all()
        
        # 保存数据
        output_dir = Path("data/raw")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"movies_top250_{timestamp}.csv"
        
        fetcher.save_to_csv(movies, output_file)
        
        print(f"\n✅ 爬取完成！")
        print(f"数据文件: {output_file}")
        print(f"共爬取 {len(movies)} 部电影")
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
    finally:
        fetcher.close()


if __name__ == "__main__":
    main()