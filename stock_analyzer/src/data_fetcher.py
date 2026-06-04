"""
股票数据获取模块
支持A股、港股、美股数据获取
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from typing import List, Dict, Optional

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    logger.warning("akshare not available, falling back to yfinance")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self, source: str = "akshare"):
        """
        初始化数据获取器
        
        Args:
            source: 数据源，可选 "akshare" 或 "yfinance"
        """
        self.source = source
        if source == "akshare" and not AKSHARE_AVAILABLE:
            logger.warning("akshare not available, switching to yfinance")
            self.source = "yfinance"
        
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance is required but not installed")
        
        logger.info(f"StockDataFetcher initialized with source: {self.source}")
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票信息字典
        """
        try:
            if self.source == "akshare":
                return self._get_info_akshare(stock_code)
            else:
                return self._get_info_yfinance(stock_code)
        except Exception as e:
            logger.error(f"Error fetching stock info for {stock_code}: {e}")
            return {}
    
    def _get_info_akshare(self, stock_code: str) -> Dict:
        """使用akshare获取股票信息"""
        # A股实时行情
        if ".SZ" in stock_code or ".SS" in stock_code:
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == stock_code.split('.')[0]]
            if not stock_data.empty:
                row = stock_data.iloc[0]
                return {
                    "code": stock_code,
                    "name": row.get('名称', ''),
                    "price": float(row.get('最新价', 0)),
                    "change": float(row.get('涨跌幅', 0)),
                    "change_amount": float(row.get('涨跌额', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "amount": float(row.get('成交额', 0)),
                    "high": float(row.get('最高', 0)),
                    "low": float(row.get('最低', 0)),
                    "open": float(row.get('今开', 0)),
                    "prev_close": float(row.get('昨收', 0)),
                    "market_cap": float(row.get('总市值', 0)) if '总市值' in row else 0,
                    "pe_ratio": float(row.get('市盈率-动态', 0)) if '市盈率 - 动态' in row else 0,
                    "timestamp": datetime.now()
                }
        
        # 港股
        elif ".HK" in stock_code:
            df = ak.stock_hk_spot_em()
            stock_data = df[df['代码'] == stock_code.split('.')[0]]
            if not stock_data.empty:
                row = stock_data.iloc[0]
                return {
                    "code": stock_code,
                    "name": row.get('名称', ''),
                    "price": float(row.get('最新价', 0)),
                    "change": float(row.get('涨跌幅', 0)),
                    "change_amount": float(row.get('涨跌额', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "high": float(row.get('最高', 0)),
                    "low": float(row.get('最低', 0)),
                    "open": float(row.get('今开', 0)),
                    "prev_close": float(row.get('昨收', 0)),
                    "market_cap": float(row.get('市值', 0)) if '市值' in row else 0,
                    "pe_ratio": float(row.get('市盈率', 0)) if '市盈率' in row else 0,
                    "timestamp": datetime.now()
                }
        
        return {}
    
    def _get_info_yfinance(self, stock_code: str) -> Dict:
        """使用yfinance获取股票信息"""
        try:
            ticker = yf.Ticker(stock_code)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Open'].iloc[0] if len(hist) > 0 else current_price
            change = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            
            return {
                "code": stock_code,
                "name": info.get('shortName', info.get('longName', '')),
                "price": float(current_price),
                "change": round(change, 2),
                "change_amount": round(current_price - prev_close, 2),
                "volume": int(hist['Volume'].iloc[-1]),
                "high": float(hist['High'].iloc[-1]),
                "low": float(hist['Low'].iloc[-1]),
                "open": float(hist['Open'].iloc[-1]),
                "prev_close": float(prev_close),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"yfinance error for {stock_code}: {e}")
            return {}
    
    def get_historical_data(self, stock_code: str, period: str = "60d") -> pd.DataFrame:
        """
        获取历史数据
        
        Args:
            stock_code: 股票代码
            period: 时间周期，如 "30d", "60d", "1y"
            
        Returns:
            DataFrame包含OHLCV数据
        """
        try:
            if self.source == "akshare":
                return self._get_history_akshare(stock_code, period)
            else:
                return self._get_history_yfinance(stock_code, period)
        except Exception as e:
            logger.error(f"Error fetching historical data for {stock_code}: {e}")
            return pd.DataFrame()
    
    def _get_history_akshare(self, stock_code: str, period: str = "60d") -> pd.DataFrame:
        """使用akshare获取历史数据"""
        try:
            # 解析周期
            days = int(period.replace("d", ""))
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # A股
            if ".SZ" in stock_code or ".SS" in stock_code:
                code = stock_code.split('.')[0]
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="qfq"  # 前复权
                )
                
                if not df.empty:
                    df = df.rename(columns={
                        "日期": "date",
                        "开盘": "open",
                        "收盘": "close",
                        "最高": "high",
                        "最低": "low",
                        "成交量": "volume",
                        "成交额": "amount"
                    })
                    df["date"] = pd.to_datetime(df["date"])
                    df.set_index("date", inplace=True)
                    return df
            
            # 港股
            elif ".HK" in stock_code:
                code = stock_code.split('.')[0]
                df = ak.stock_hk_daily(
                    symbol=code,
                    adjust="qfq"
                )
                
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"])
                    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
                    df.set_index("date", inplace=True)
                    return df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"akshare history error for {stock_code}: {e}")
            return pd.DataFrame()
    
    def _get_history_yfinance(self, stock_code: str, period: str = "60d") -> pd.DataFrame:
        """使用yfinance获取历史数据"""
        try:
            ticker = yf.Ticker(stock_code)
            df = ticker.history(period=period)
            
            if not df.empty:
                # 确保列名一致
                df = df.rename(columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume"
                })
                return df[["open", "high", "low", "close", "volume"]]
            
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"yfinance history error for {stock_code}: {e}")
            return pd.DataFrame()
    
    def get_multiple_stocks(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        批量获取多只股票信息
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            字典 {股票代码：股票信息}
        """
        results = {}
        for code in stock_codes:
            try:
                info = self.get_stock_info(code)
                if info:
                    results[code] = info
            except Exception as e:
                logger.error(f"Error fetching {code}: {e}")
                continue
        
        return results
    
    def get_real_time_quotes(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取实时报价
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            DataFrame包含实时报价数据
        """
        all_data = []
        
        for code in stock_codes:
            try:
                info = self.get_stock_info(code)
                if info:
                    all_data.append(info)
            except Exception as e:
                logger.error(f"Error fetching quote for {code}: {e}")
                continue
        
        if all_data:
            df = pd.DataFrame(all_data)
            return df
        
        return pd.DataFrame()
