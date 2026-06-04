"""
新闻检索与分析模块
实时检索各大权威媒体新闻报道
"""
import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import json


class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self):
        """初始化新闻获取器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("NewsFetcher initialized")
    
    def fetch_news_from_sources(self, sources: List[Dict], keywords: List[str] = None) -> List[Dict]:
        """
        从多个新闻源获取新闻
        
        Args:
            sources: 新闻源配置列表
            keywords: 关键词列表，用于过滤新闻
            
        Returns:
            新闻列表
        """
        all_news = []
        
        for source in sources:
            if not source.get("enabled", True):
                continue
            
            try:
                news_list = self._fetch_from_source(source, keywords)
                all_news.extend(news_list)
                logger.info(f"Fetched {len(news_list)} news from {source['name']}")
            except Exception as e:
                logger.error(f"Error fetching news from {source['name']}: {e}")
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('published', datetime.min), reverse=True)
        
        return all_news
    
    def _fetch_from_source(self, source: Dict, keywords: List[str] = None) -> List[Dict]:
        """
        从单个新闻源获取新闻
        
        Args:
            source: 新闻源配置
            keywords: 关键词列表
            
        Returns:
            新闻列表
        """
        news_list = []
        url = source.get("url", "")
        
        # 尝试RSS feed
        if "rss" in url.lower() or "feed" in url.lower():
            news_list = self._fetch_rss(url, source["name"], keywords)
        else:
            # 尝试网页爬取
            news_list = self._fetch_web(url, source["name"], keywords)
        
        return news_list
    
    def _fetch_rss(self, url: str, source_name: str, keywords: List[str] = None) -> List[Dict]:
        """从RSS feed获取新闻"""
        news_list = []
        
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:20]:  # 限制每个源最多20条
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                published = entry.get('published_parsed')
                
                # 关键词过滤
                if keywords and not self._match_keywords(title + ' ' + summary, keywords):
                    continue
                
                news_item = {
                    "title": title,
                    "summary": summary,
                    "source": source_name,
                    "url": entry.get('link', ''),
                    "published": datetime(*published[:6]) if published else datetime.now(),
                    "sentiment": None,  # 后续由AI分析
                    "relevance_score": 0.0
                }
                
                news_list.append(news_item)
        
        except Exception as e:
            logger.error(f"RSS fetch error for {url}: {e}")
        
        return news_list
    
    def _fetch_web(self, url: str, source_name: str, keywords: List[str] = None) -> List[Dict]:
        """从网页获取新闻"""
        news_list = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 根据不同网站结构调整选择器
            if "sina" in url:
                news_list = self._parse_sina(soup, source_name, keywords)
            elif "eastmoney" in url:
                news_list = self._parse_eastmoney(soup, source_name, keywords)
            elif "caixin" in url:
                news_list = self._parse_caixin(soup, source_name, keywords)
            elif "reuters" in url:
                news_list = self._parse_reuters(soup, source_name, keywords)
            elif "bloomberg" in url:
                news_list = self._parse_bloomberg(soup, source_name, keywords)
            else:
                # 通用解析
                news_list = self._parse_generic(soup, source_name, keywords)
        
        except Exception as e:
            logger.error(f"Web fetch error for {url}: {e}")
        
        return news_list
    
    def _parse_sina(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """解析新浪财经"""
        news_list = []
        # 简化版，实际需要根据网站结构调整
        return news_list
    
    def _parse_eastmoney(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """解析东方财富"""
        news_list = []
        return news_list
    
    def _parse_caixin(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """解析财新网"""
        news_list = []
        return news_list
    
    def _parse_reuters(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """解析Reuters"""
        news_list = []
        return news_list
    
    def _parse_bloomberg(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """解析Bloomberg"""
        news_list = []
        return news_list
    
    def _parse_generic(self, soup: BeautifulSoup, source_name: str, keywords: List[str]) -> List[Dict]:
        """通用网页解析"""
        news_list = []
        
        # 查找可能的新闻标题
        headlines = soup.find_all(['h1', 'h2', 'h3'], class_=re.compile(r'news|title|headline', re.I))
        
        for item in headlines[:10]:
            title = item.get_text(strip=True)
            if keywords and not self._match_keywords(title, keywords):
                continue
            
            news_item = {
                "title": title,
                "summary": "",
                "source": source_name,
                "url": "",
                "published": datetime.now(),
                "sentiment": None,
                "relevance_score": 0.0
            }
            news_list.append(news_item)
        
        return news_list
    
    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        """检查文本是否匹配关键词"""
        if not keywords:
            return True
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def search_stock_news(self, stock_codes: List[str], stock_names: List[str] = None, 
                         limit: int = 50) -> List[Dict]:
        """
        搜索与股票相关的新闻
        
        Args:
            stock_codes: 股票代码列表
            stock_names: 股票名称列表
            limit: 返回新闻数量限制
            
        Returns:
            相关新闻列表
        """
        # 构建关键词
        keywords = stock_codes.copy()
        if stock_names:
            keywords.extend(stock_names)
        
        # 添加通用金融关键词
        general_keywords = [
            "stock", "market", "trading", "investor", "earnings",
            "股票", "股市", "行情", "涨停", "跌停", "财报"
        ]
        keywords.extend(general_keywords)
        
        # 定义新闻源
        sources = [
            {"name": "新浪财经", "url": "http://feeds.finance.sina.com.cn/stock/rss.xml", "enabled": True},
            {"name": "东方财富", "url": "http://app.eastmoney.com/rss/feed.aspx", "enabled": True},
            {"name": "Reuters Business", "url": "https://www.reuters.com/rssFeed/businessNews", "enabled": True},
            {"name": "Bloomberg Markets", "url": "https://www.bloomberg.com/feed/markets", "enabled": True},
        ]
        
        news = self.fetch_news_from_sources(sources, keywords)
        
        # 计算相关性分数
        for news_item in news:
            score = self._calculate_relevance(news_item, keywords)
            news_item["relevance_score"] = score
        
        # 按相关性排序并限制数量
        news.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return news[:limit]
    
    def _calculate_relevance(self, news_item: Dict, keywords: List[str]) -> float:
        """计算新闻与关键词的相关性分数"""
        text = news_item["title"] + " " + news_item["summary"]
        text_lower = text.lower()
        
        match_count = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                match_count += 1
        
        # 归一化到0-1之间
        if len(keywords) > 0:
            score = min(match_count / len(keywords), 1.0)
        else:
            score = 0.0
        
        return score
    
    def get_market_overview_news(self, limit: int = 20) -> List[Dict]:
        """
        获取市场概览新闻
        
        Args:
            limit: 返回新闻数量限制
            
        Returns:
            市场新闻列表
        """
        keywords = [
            "market overview", "market analysis", "market trend",
            "市场综述", "市场分析", "大盘走势", "宏观经济"
        ]
        
        sources = [
            {"name": "Reuters Markets", "url": "https://www.reuters.com/rssFeed/marketsNews", "enabled": True},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/feed/markets", "enabled": True},
        ]
        
        news = self.fetch_news_from_sources(sources, keywords)
        return news[:limit]
