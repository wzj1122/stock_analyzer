"""
AI分析模块
运用AI工具对股票走势和新闻进行科学客观分析
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from loguru import logger
from datetime import datetime

# 尝试导入AI相关库
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available, some AI features will be limited")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self, model_name: str = None, use_rule_based: bool = True):
        """
        初始化情感分析器
        
        Args:
            model_name: 模型名称 (如果为 None 则使用基于规则的方法)
            use_rule_based: 是否使用基于规则的方法（默认 True，节省资源）
        """
        self.model_name = model_name
        self.pipeline = None
        self.use_rule_based = use_rule_based
        
        # 只在明确需要且资源充足时加载模型
        if model_name and not use_rule_based and TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                # 加载中文情感分析模型
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info(f"Sentiment analyzer loaded with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load sentiment model: {e}, using rule-based fallback")
                self.use_rule_based = True
        else:
            logger.info("Using rule-based sentiment analysis (resource-efficient mode)")
            self.use_rule_based = True
    
    def analyze(self, text: str) -> Dict:
        """
        分析文本情感
        
        Args:
            text: 待分析的文本
            
        Returns:
            情感分析结果
        """
        if self.pipeline:
            try:
                result = self.pipeline(text[:512])  # 限制长度
                return {
                    "sentiment": result[0]["label"],
                    "confidence": float(result[0]["score"]),
                    "polarity": self._convert_to_polarity(result[0]["label"])
                }
            except Exception as e:
                logger.error(f"Sentiment analysis error: {e}")
        
        # 回退到基于规则的分析
        return self._rule_based_analysis(text)
    
    def _convert_to_polarity(self, label: str) -> float:
        """将标签转换为极性分数 (-1 到 1)"""
        positive_labels = ["positive", "POS", "积极", "正面"]
        negative_labels = ["negative", "NEG", "消极", "负面"]
        
        label_lower = label.lower()
        for pos in positive_labels:
            if pos.lower() in label_lower:
                return 1.0
        for neg in negative_labels:
            if neg.lower() in label_lower:
                return -1.0
        return 0.0
    
    def _rule_based_analysis(self, text: str) -> Dict:
        """基于规则的情感分析（回退方案）"""
        positive_words = [
            "上涨", "增长", "利好", "突破", "创新高", "盈利", "收益",
            "bullish", "rise", "gain", "profit", "surge", "soar"
        ]
        negative_words = [
            "下跌", "下降", "利空", "跌破", "亏损", "下滑", "暴跌",
            "bearish", "fall", "drop", "loss", "decline", "plunge"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            polarity = 0.0
            sentiment = "neutral"
            confidence = 0.5
        else:
            polarity = (pos_count - neg_count) / total
            if polarity > 0.2:
                sentiment = "positive"
                confidence = min(abs(polarity) + 0.3, 1.0)
            elif polarity < -0.2:
                sentiment = "negative"
                confidence = min(abs(polarity) + 0.3, 1.0)
            else:
                sentiment = "neutral"
                confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "polarity": polarity
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量分析文本情感"""
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        return results


class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        """初始化技术分析器"""
        logger.info("Technical analyzer initialized")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            添加了技术指标的DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 指数移动平均线
        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (std * 2)
        df['BB_lower'] = df['BB_middle'] - (std * 2)
        
        # 成交量均线
        df['VOL_MA5'] = df['volume'].rolling(window=5).mean()
        df['VOL_MA10'] = df['volume'].rolling(window=10).mean()
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        生成交易信号
        
        Args:
            df: 包含技术指标的DataFrame
            
        Returns:
            交易信号字典
        """
        if df.empty or len(df) < 60:
            return {"signal": "hold", "strength": 0, "reasons": []}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        signals = []
        bullish_count = 0
        bearish_count = 0
        
        # MA信号
        if latest['close'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
            signals.append("均线多头排列")
            bullish_count += 2
        elif latest['close'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
            signals.append("均线空头排列")
            bearish_count += 2
        
        # MACD信号
        if latest['MACD'] > latest['Signal_Line'] and prev['MACD'] <= prev['Signal_Line']:
            signals.append("MACD金叉")
            bullish_count += 2
        elif latest['MACD'] < latest['Signal_Line'] and prev['MACD'] >= prev['Signal_Line']:
            signals.append("MACD死叉")
            bearish_count += 2
        
        # RSI信号
        if latest['RSI'] < 30:
            signals.append("RSI超卖")
            bullish_count += 1
        elif latest['RSI'] > 70:
            signals.append("RSI超买")
            bearish_count += 1
        
        # 布林带信号
        if latest['close'] < latest['BB_lower']:
            signals.append("价格触及布林带下轨")
            bullish_count += 1
        elif latest['close'] > latest['BB_upper']:
            signals.append("价格触及布林带上轨")
            bearish_count += 1
        
        # 成交量信号
        if latest['volume'] > latest['VOL_MA5'] * 1.5:
            signals.append("成交量放大")
            if latest['close'] > latest['open']:
                bullish_count += 1
            else:
                bearish_count += 1
        
        # 综合判断
        if bullish_count > bearish_count + 2:
            signal = "buy"
            strength = min((bullish_count - bearish_count) / 10, 1.0)
        elif bearish_count > bullish_count + 2:
            signal = "sell"
            strength = min((bearish_count - bullish_count) / 10, 1.0)
        else:
            signal = "hold"
            strength = abs(bullish_count - bearish_count) / 10
        
        return {
            "signal": signal,
            "strength": round(strength, 2),
            "reasons": signals,
            "bullish_factors": bullish_count,
            "bearish_factors": bearish_count
        }
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        检测K线形态
        
        Args:
            df: OHLCV数据
            
        Returns:
            检测到的形态列表
        """
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3] if len(df) > 2 else prev
        
        # 检测十字星
        body_size = abs(latest['close'] - latest['open'])
        range_size = latest['high'] - latest['low']
        if range_size > 0 and body_size / range_size < 0.1:
            patterns.append({
                "name": "十字星",
                "type": "reversal",
                "significance": "medium"
            })
        
        # 检测大阳线
        if latest['close'] > latest['open'] * 1.03:
            patterns.append({
                "name": "大阳线",
                "type": "bullish",
                "significance": "high"
            })
        
        # 检测大阴线
        if latest['close'] < latest['open'] * 0.97:
            patterns.append({
                "name": "大阴线",
                "type": "bearish",
                "significance": "high"
            })
        
        # 检测早晨之星
        if (len(df) >= 3 and 
            prev2['close'] < prev2['open'] and  # 第一天阴线
            abs(prev['close'] - prev['open']) / (prev['high'] - prev['low']) < 0.1 and  # 第二天十字星
            prev['close'] < prev['open'] and
            latest['close'] > latest['open'] and  # 第三天阳线
            latest['close'] > (prev2['open'] + prev2['close']) / 2):
            patterns.append({
                "name": "早晨之星",
                "type": "bullish_reversal",
                "significance": "high"
            })
        
        # 检测黄昏之星
        if (len(df) >= 3 and
            prev2['close'] > prev2['open'] and  # 第一天阳线
            abs(prev['close'] - prev['open']) / (prev['high'] - prev['low']) < 0.1 and  # 第二天十字星
            prev['close'] > prev['open'] and
            latest['close'] < latest['open'] and  # 第三天阴线
            latest['close'] < (prev2['open'] + prev2['close']) / 2):
            patterns.append({
                "name": "黄昏之星",
                "type": "bearish_reversal",
                "significance": "high"
            })
        
        return patterns


class AIStockAnalyzer:
    """AI股票综合分析器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化AI股票分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        logger.info("AI Stock Analyzer initialized")
    
    def analyze_stock(self, stock_code: str, stock_info: Dict, 
                     price_data: pd.DataFrame, news_list: List[Dict]) -> Dict:
        """
        综合分析股票
        
        Args:
            stock_code: 股票代码
            stock_info: 股票基本信息
            price_data: 价格数据
            news_list: 相关新闻列表
            
        Returns:
            综合分析结果
        """
        result = {
            "stock_code": stock_code,
            "stock_name": stock_info.get("name", ""),
            "analysis_time": datetime.now().isoformat(),
            "current_price": stock_info.get("price", 0),
            "change_percent": stock_info.get("change", 0),
        }
        
        # 技术分析
        if not price_data.empty:
            price_with_indicators = self.technical_analyzer.calculate_indicators(price_data)
            technical_signals = self.technical_analyzer.generate_signals(price_with_indicators)
            patterns = self.technical_analyzer.detect_patterns(price_with_indicators)
            
            result["technical_analysis"] = {
                "signal": technical_signals["signal"],
                "strength": technical_signals["strength"],
                "reasons": technical_signals["reasons"],
                "patterns": patterns,
                "indicators": {
                    "RSI": float(price_with_indicators['RSI'].iloc[-1]) if 'RSI' in price_with_indicators.columns else None,
                    "MACD": float(price_with_indicators['MACD'].iloc[-1]) if 'MACD' in price_with_indicators.columns else None,
                    "MA5": float(price_with_indicators['MA5'].iloc[-1]) if 'MA5' in price_with_indicators.columns else None,
                    "MA20": float(price_with_indicators['MA20'].iloc[-1]) if 'MA20' in price_with_indicators.columns else None,
                }
            }
        else:
            result["technical_analysis"] = {
                "signal": "hold",
                "strength": 0,
                "reasons": ["数据不足"],
                "patterns": [],
                "indicators": {}
            }
        
        # 新闻情感分析
        if news_list:
            sentiments = []
            for news in news_list[:10]:  # 分析前10条新闻
                title = news.get("title", "")
                summary = news.get("summary", "")
                text = title + " " + summary
                
                if text.strip():
                    sentiment_result = self.sentiment_analyzer.analyze(text)
                    news["sentiment"] = sentiment_result
                    sentiments.append(sentiment_result["polarity"])
            
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                result["news_sentiment"] = {
                    "average_polarity": round(avg_sentiment, 3),
                    "news_count": len(sentiments),
                    "positive_count": sum(1 for s in sentiments if s > 0.2),
                    "negative_count": sum(1 for s in sentiments if s < -0.2),
                    "neutral_count": len(sentiments) - sum(1 for s in sentiments if abs(s) > 0.2)
                }
            else:
                result["news_sentiment"] = {
                    "average_polarity": 0,
                    "news_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                }
            
            result["analyzed_news"] = news_list[:10]
        else:
            result["news_sentiment"] = {
                "average_polarity": 0,
                "news_count": 0
            }
            result["analyzed_news"] = []
        
        # 综合建议
        result["recommendation"] = self._generate_recommendation(result)
        
        return result
    
    def _generate_recommendation(self, analysis_result: Dict) -> Dict:
        """
        生成投资建议
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            投资建议
        """
        tech_signal = analysis_result["technical_analysis"]["signal"]
        tech_strength = analysis_result["technical_analysis"]["strength"]
        
        news_polarity = analysis_result["news_sentiment"]["average_polarity"]
        
        # 综合评分
        score = 0
        
        # 技术面评分 (-2 到 2)
        if tech_signal == "buy":
            score += tech_strength * 2
        elif tech_signal == "sell":
            score -= tech_strength * 2
        
        # 消息面评分 (-1 到 1)
        score += news_polarity
        
        # 生成建议
        if score >= 1.5:
            action = "强烈建议买入"
            confidence = min(score / 3, 1.0)
        elif score >= 0.5:
            action = "建议买入"
            confidence = min(score / 2, 1.0)
        elif score <= -1.5:
            action = "强烈建议卖出"
            confidence = min(abs(score) / 3, 1.0)
        elif score <= -0.5:
            action = "建议卖出"
            confidence = min(abs(score) / 2, 1.0)
        else:
            action = "持有观望"
            confidence = max(0, 1 - abs(score))
        
        # 风险提示
        risks = []
        if news_polarity < -0.3:
            risks.append("负面新闻较多，注意风险")
        if analysis_result["technical_analysis"].get("patterns"):
            risks.append("检测到重要K线形态，需密切关注")
        if abs(analysis_result["change_percent"]) > 5:
            risks.append("今日波动较大，注意风险控制")
        
        return {
            "action": action,
            "confidence": round(confidence, 2),
            "composite_score": round(score, 2),
            "risks": risks,
            "summary": self._generate_summary(analysis_result, action)
        }
    
    def _generate_summary(self, analysis_result: Dict, action: str) -> str:
        """生成分析摘要"""
        stock_name = analysis_result["stock_name"]
        price = analysis_result["current_price"]
        change = analysis_result["change_percent"]
        
        tech_reasons = analysis_result["technical_analysis"]["reasons"]
        sentiment = analysis_result["news_sentiment"]["average_polarity"]
        
        summary = f"{stock_name}当前价格{price}，涨跌幅{change}%。\n"
        
        if tech_reasons:
            summary += f"技术面：{', '.join(tech_reasons[:3])}。\n"
        
        if sentiment > 0.2:
            summary += "消息面偏正面，市场情绪乐观。\n"
        elif sentiment < -0.2:
            summary += "消息面偏负面，市场情绪谨慎。\n"
        else:
            summary += "消息面中性。\n"
        
        summary += f"综合建议：{action}。"
        
        return summary
    
    def analyze_portfolio(self, portfolio: List[Dict]) -> Dict:
        """
        分析投资组合
        
        Args:
            portfolio: 投资组合列表，每项包含stock_code, stock_info, price_data, news_list
            
        Returns:
            组合分析结果
        """
        results = []
        for item in portfolio:
            result = self.analyze_stock(
                item["stock_code"],
                item["stock_info"],
                item["price_data"],
                item["news_list"]
            )
            results.append(result)
        
        # 组合整体分析
        total_score = sum(r["recommendation"]["composite_score"] for r in results)
        avg_score = total_score / len(results) if results else 0
        
        return {
            "stocks": results,
            "portfolio_score": round(avg_score, 2),
            "recommendation": "分散投资，注意风险控制" if abs(avg_score) < 1 else ("整体偏多" if avg_score > 0 else "整体偏空"),
            "analysis_time": datetime.now().isoformat()
        }
