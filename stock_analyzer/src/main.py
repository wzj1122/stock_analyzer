"""
主程序入口
启动股票实时监测与AI分析系统
"""
import sys
import os
from loguru import logger

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import get_config


def setup_logging():
    """配置日志"""
    config = get_config()
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        config.LOG_FILE,
        rotation="10 MB",
        retention="7 days",
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info("Logging system initialized")


def main():
    """主函数"""
    setup_logging()
    logger.info("Starting Stock Analyzer System...")
    
    config = get_config()
    
    print("=" * 60)
    print("📈 股票实时监测与 AI 分析系统")
    print("=" * 60)
    print()
    print(f"配置环境：{os.getenv('FLASK_ENV', 'development')}")
    print(f"数据源：{config.STOCK_DATA_SOURCE}")
    print(f"关注股票数量：{len(config.WATCHLIST_STOCKS)}")
    print(f"刷新间隔：{config.REFRESH_INTERVAL}秒")
    print()
    print(config.RISK_WARNING)
    print()
    print("=" * 60)
    print("启动方式:")
    print("  1. Web 界面：streamlit run src/web_interface.py")
    print("  2. 命令行：python src/main.py --cli")
    print("=" * 60)
    
    # 检查必要的依赖
    try:
        import pandas as pd
        import numpy as np
        logger.info("Core dependencies loaded successfully")
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return
    
    # 尝试加载可选依赖
    try:
        import akshare as ak
        logger.info("akshare loaded successfully")
    except ImportError:
        logger.warning("akshare not available, will use yfinance only")
    
    try:
        import yfinance as yf
        logger.info("yfinance loaded successfully")
    except ImportError:
        logger.error("yfinance is required but not installed")
        return
    
    try:
        import streamlit as st
        logger.info("Streamlit available for web interface")
    except ImportError:
        logger.warning("Streamlit not available, web interface disabled")
    
    logger.info("System initialization completed")
    print("\n✅ 系统初始化完成!")
    print("\n请运行以下命令启动 Web 界面:")
    print("   streamlit run src/web_interface.py")
    print("\n或查看 README.md 获取详细使用说明。")


if __name__ == "__main__":
    main()
