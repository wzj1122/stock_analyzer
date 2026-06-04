"""
测试模块示例
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestDataFetcher:
    """数据获取器测试"""
    
    def test_import_data_fetcher(self):
        """测试能否导入数据获取器"""
        from src.data_fetcher import StockDataFetcher
        assert StockDataFetcher is not None
    
    def test_create_fetcher(self):
        """测试创建数据获取器实例"""
        from src.data_fetcher import StockDataFetcher
        fetcher = StockDataFetcher(source="yfinance")
        assert fetcher is not None
        assert fetcher.source == "yfinance"


class TestNewsFetcher:
    """新闻获取器测试"""
    
    def test_import_news_fetcher(self):
        """测试能否导入新闻获取器"""
        from src.news_fetcher import NewsFetcher
        assert NewsFetcher is not None
    
    def test_create_fetcher(self):
        """测试创建新闻获取器实例"""
        from src.news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        assert fetcher is not None


class TestAIAnalyzer:
    """AI 分析器测试"""
    
    def test_import_analyzer(self):
        """测试能否导入 AI 分析器"""
        from src.ai_analyzer import AIStockAnalyzer
        assert AIStockAnalyzer is not None
    
    def test_create_analyzer(self):
        """测试创建 AI 分析器实例"""
        from src.ai_analyzer import AIStockAnalyzer
        analyzer = AIStockAnalyzer()
        assert analyzer is not None
    
    def test_sentiment_analysis(self):
        """测试情感分析"""
        from src.ai_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        # 测试正面文本
        result = analyzer.analyze("股票大涨，业绩利好")
        assert "sentiment" in result
        assert "polarity" in result
        
        # 测试负面文本
        result = analyzer.analyze("股价暴跌，亏损严重")
        assert "sentiment" in result
        assert "polarity" in result
    
    def test_technical_indicators(self):
        """测试技术指标计算"""
        from src.ai_analyzer import TechnicalAnalyzer
        
        # 创建模拟数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 115, 100),
            'low': np.random.uniform(95, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        analyzer = TechnicalAnalyzer()
        result_df = analyzer.calculate_indicators(df)
        
        # 检查是否添加了指标列
        assert 'MA5' in result_df.columns
        assert 'MA20' in result_df.columns
        assert 'RSI' in result_df.columns
        assert 'MACD' in result_df.columns


class TestConfig:
    """配置测试"""
    
    def test_import_config(self):
        """测试能否导入配置"""
        from config.settings import get_config
        config = get_config()
        assert config is not None
    
    def test_watchlist(self):
        """测试关注列表"""
        from config.settings import get_config
        config = get_config()
        assert len(config.WATCHLIST_STOCKS) > 0
        assert isinstance(config.WATCHLIST_STOCKS, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
