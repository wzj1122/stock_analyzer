"""
股票实时监测与AI分析系统配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """系统配置类"""
    
    # API Keys (从环境变量获取)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY", "")  # 可选，用于中文新闻分析
    
    # 股票数据源配置
    STOCK_DATA_SOURCE = "akshare"  # 可选：akshare, yfinance
    REFRESH_INTERVAL = 60  # 数据刷新间隔（秒）
    
    # 关注的股票代码列表
    WATCHLIST_STOCKS = [
        # A股
        "000001.SZ",  # 平安银行
        "600519.SS",  # 贵州茅台
        "000858.SZ",  # 五粮液
        "300750.SZ",  # 宁德时代
        # 港股
        "0700.HK",    # 腾讯控股
        "9988.HK",    # 阿里巴巴
        # 美股
        "AAPL",       # 苹果
        "GOOGL",      # 谷歌
        "TSLA",       # 特斯拉
        "NVDA",       # 英伟达
    ]
    
    # 新闻源配置
    NEWS_SOURCES = [
        {
            "name": "新浪财经",
            "url": "http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletin.php",
            "enabled": True
        },
        {
            "name": "东方财富",
            "url": "http://news.eastmoney.com/",
            "enabled": True
        },
        {
            "name": "财新网",
            "url": "https://www.caixin.com/",
            "enabled": True
        },
        {
            "name": "Reuters",
            "url": "https://www.reuters.com/markets/",
            "enabled": True
        },
        {
            "name": "Bloomberg",
            "url": "https://www.bloomberg.com/markets",
            "enabled": True
        }
    ]
    
    # AI模型配置
    AI_MODEL_CONFIG = {
        "sentiment_model": "bert-base-chinese",  # 情感分析模型
        "summary_model": "facebook/bart-large-cnn",  # 摘要模型
        "prediction_model": "openai/gpt-4",  # 预测模型
        "max_news_count": 50,  # 每次分析的最大新闻数量
    }
    
    # 技术指标配置
    TECHNICAL_INDICATORS = [
        "MA",      # 移动平均线
        "EMA",     # 指数移动平均线
        "MACD",    # 异同移动平均线
        "RSI",     # 相对强弱指标
        "KDJ",     # 随机指标
        "BOLL",    # 布林带
        "VOL",     # 成交量
    ]
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/stock_analyzer.log"
    
    # Redis配置（用于缓存和任务队列）
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # Web界面配置
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 8501
    
    # 风险提示配置
    RISK_WARNING = """
    ⚠️ 风险提示：
    1. 本系统提供的分析仅供参考，不构成投资建议
    2. 股市有风险，投资需谨慎
    3. AI分析存在局限性，请结合个人判断
    4. 过往表现不代表未来收益
    """


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


# 配置映射
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config(env=None):
    """获取配置对象"""
    if env is None:
        env = os.getenv("FLASK_ENV", "default")
    return config_map.get(env, config_map["default"])()
