# 股票实时监测与 AI 分析系统 (Stock Real-time Monitor & AI Analyzer)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 项目简介

本系统是一个**全功能的股票实时监测与 AI 智能分析平台**,旨在帮助投资者:
- 📈 **实时监控股票走势**:支持 A 股、港股、美股全球主要市场
- 📰 **智能新闻检索**:聚合全球权威财经媒体，实时抓取相关新闻
- 🤖 **AI 深度分析**:运用 NLP 情感分析、技术指标计算、K 线形态识别等多维度分析
- 💡 **科学投资建议**:基于数据驱动，提供客观的投资参考建议

> ⚠️ **风险提示**:本系统所有分析结果仅供参考，不构成任何投资建议。股市有风险，投资需谨慎。

---

## 🔧 详细配置说明

### 1. 环境变量配置 (.env 文件)

在项目根目录创建 `.env` 文件，配置以下内容：

```bash
# ============================================
# API Keys 配置 (可选，用于增强功能)
# ============================================

# OpenAI API Key (用于高级 AI 分析)
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o-mini"

# 备用 LLM 配置 (如使用本地模型或其他提供商)
# LLAMA_INDEX_API_KEY=""
# ANTHROPIC_API_KEY=""

# 新闻 API (可选，用于增强新闻获取)
NEWSAPI_KEY=""
ALPHA_VANTAGE_KEY=""

# ============================================
# 系统基础配置
# ============================================

# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL="INFO"

# 数据缓存目录
DATA_CACHE_DIR="./data"

# 日志目录
LOG_DIR="./logs"

# 缓存过期时间 (秒)，默认 300 秒 (5 分钟)
CACHE_EXPIRY_SECONDS=300

# ============================================
# 股票关注列表配置
# ============================================

# A 股股票代码 (逗号分隔，格式：sh/shz + 6 位代码)
A_STOCKS="sh000001,sh600519,sz000002,sz300750"

# 港股股票代码 (逗号分隔，格式：hk + 5 位代码)
HK_STOCKS="hk00700,hk09988"

# 美股股票代码 (逗号分隔，直接写 ticker)
US_STOCKS="AAPL,GOOGL,MSFT,TSLA,NVDA"

# 默认选中的股票 (用于 Web 界面初始显示)
DEFAULT_STOCK="sh600519"

# ============================================
# 技术分析参数配置
# ============================================

# RSI (相对强弱指数) 参数
RSI_PERIOD=14
RSI_OVERBOUGHT=70      # 超买阈值
RSI_OVERSOLD=30        # 超卖阈值

# MACD 参数
MACD_FAST=12           # 快线周期
MACD_SLOW=26           # 慢线周期
MACD_SIGNAL=9          # 信号线周期

# 移动平均线 (MA) 周期 (逗号分隔)
MA_PERIODS="5,10,20,60"

# 布林带参数
BOLLINGER_PERIOD=20
BOLLINGER_STD=2.0

# KDJ 参数
KDJ_N=9
KDJ_K=3
KDJ_D=3

# ============================================
# 情感分析参数配置
# ============================================

# 情感分析模式：rule(规则-based), model(深度学习模型)
SENTIMENT_MODE="rule"

# 正面情感阈值 (>此值为正面)
SENTIMENT_POSITIVE_THRESHOLD=0.1

# 负面情感阈值 (<此值为负面)
SENTIMENT_NEGATIVE_THRESHOLD=-0.1

# 新闻权重 (在综合评分中的占比 0-1)
NEWS_WEIGHT=0.3

# 技术面权重 (在综合评分中的占比 0-1)
TECHNICAL_WEIGHT=0.7

# ============================================
# Web 界面配置
# ============================================

# Streamlit 服务器端口
STREAMLIT_PORT=8501

# 是否自动打开浏览器
STREAMLIT_HEADLESS=false

# 主题：light, dark, auto
STREAMLIT_THEME="dark"

# 刷新间隔 (秒)，Web 界面自动刷新频率
REFRESH_INTERVAL=60

# 图表样式配置
CHART_WIDTH=1200
CHART_HEIGHT=600

# ============================================
# 风险提示配置
# ============================================

# 是否显示风险提示横幅
SHOW_RISK_WARNING=true

# 风险警告级别：low, medium, high
RISK_WARNING_LEVEL="high"
```

### 2. 代码配置 (config/settings.py)

系统使用 Pydantic 进行配置管理，以下是核心配置类说明：

```python
from pydantic import BaseSettings, Field
from typing import List, Optional
import os

class StockConfig(BaseSettings):
    """股票配置"""
    a_stocks: List[str] = Field(
        default=["sh000001", "sh600519"],
        description="A 股关注列表"
    )
    hk_stocks: List[str] = Field(
        default=["hk00700"],
        description="港股关注列表"
    )
    us_stocks: List[str] = Field(
        default=["AAPL", "GOOGL"],
        description="美股关注列表"
    )
    
    class Config:
        env_prefix = ""
        env_file = ".env"

class TechnicalConfig(BaseSettings):
    """技术分析配置"""
    rsi_period: int = Field(default=14, ge=1, le=50)
    rsi_overbought: float = Field(default=70.0, ge=50, le=100)
    rsi_oversold: float = Field(default=30.0, ge=0, le=50)
    
    macd_fast: int = Field(default=12, ge=1)
    macd_slow: int = Field(default=26, gt=12)
    macd_signal: int = Field(default=9, ge=1)
    
    ma_periods: List[int] = Field(default=[5, 10, 20, 60])
    
    bollinger_period: int = Field(default=20, ge=10)
    bollinger_std: float = Field(default=2.0, ge=1.0, le=3.0)

class SentimentConfig(BaseSettings):
    """情感分析配置"""
    sentiment_mode: str = Field(default="rule", regex="^(rule|model)$")
    positive_threshold: float = Field(default=0.1)
    negative_threshold: float = Field(default=-0.1)
    news_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    technical_weight: float = Field(default=0.7, ge=0.0, le=1.0)

class AppConfig(BaseSettings):
    """应用总配置"""
    # 加载所有子配置
    stock: StockConfig = Field(default_factory=StockConfig)
    technical: TechnicalConfig = Field(default_factory=TechnicalConfig)
    sentiment: SentimentConfig = Field(default_factory=SentimentConfig)
    
    # 基础设置
    log_level: str = Field(default="INFO")
    cache_expiry: int = Field(default=300)
    refresh_interval: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "_"
```

### 3. 数据源配置说明

#### 股票数据源

| 数据源 | 支持市场 | 优点 | 缺点 | 配置方式 |
|--------|---------|------|------|---------|
| **akshare** | A 股、港股 | 免费、数据全面、更新快 | 需要国内网络环境 | 默认启用 |
| **yfinance** | 美股、港股 | 国际通用、稳定 | A 股数据有限 | 作为备用源 |
| **Tushare** | A 股 | 专业级数据 | 需要积分/付费 | 需配置 TOKEN |

如需使用 Tushare，在 `.env` 中添加：
```bash
TUSHARE_TOKEN="your_tushare_token"
USE_TUSHARE=true
```

#### 新闻数据源

| 数据源 | 类型 | 覆盖媒体 | 更新频率 |
|--------|------|---------|---------|
| **新浪财经 RSS** | RSS Feed | 新浪财经、各大门户 | 实时 |
| **东方财富爬虫** | Web Scraping | 东方财富网 | 5 分钟延迟 |
| **Reuters API** | API (需 Key) | 路透社 | 实时 |
| **Bloomberg RSS** | RSS Feed | 彭博社 | 实时 |
| **Google News** | 搜索聚合 | 全球媒体 | 实时 |

### 4. 自定义关注列表

#### 方法一：修改 .env 文件
```bash
A_STOCKS="sh000001,sh600519,sz000002,sz300750"
```

#### 方法二：Web 界面动态添加
启动后在界面中输入框直接添加股票代码

#### 方法三：代码中配置
编辑 `config/settings.py`:
```python
DEFAULT_WATCHLIST = {
    "a_stocks": ["sh000001", "sh600519", "sz000002"],
    "hk_stocks": ["hk00700", "hk09988"],
    "us_stocks": ["AAPL", "MSFT", "GOOGL", "NVDA"]
}
```

#### 股票代码格式规范

| 市场 | 前缀 | 示例 | 说明 |
|------|------|------|------|
| 上证指数 | `sh` + 6 位 | `sh000001` | 大盘指数 |
| 深证成指 | `sz` + 6 位 | `sz399001` | 大盘指数 |
| A 股个股 | `sh/sz` + 6 位 | `sh600519` | sh=沪市，sz=深市 |
| 港股 | `hk` + 5 位 | `hk00700` | 腾讯控股 |
| 美股 | 直接 ticker | `AAPL` | 苹果公司 |

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- pip 包管理器
- 网络连接 (访问财经数据源)

### 2. 安装步骤

```bash
# 克隆或进入项目目录
cd /workspace/stock_analyzer

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，根据需要配置
vim .env  # 或使用其他编辑器

# 启动 Web 界面
streamlit run src/web_interface.py --server.port 8501
```

### 3. 验证安装

运行测试脚本：
```bash
python -m pytest tests/ -v
```

预期输出：
```
test_config_load PASSED
test_data_fetcher_init PASSED
test_news_fetcher_init PASSED
test_technical_indicators PASSED
test_sentiment_analysis PASSED
```

---

## 📊 功能详解

### 1. 实时股票监测 (`src/data_fetcher.py`)

**核心功能:**
- 多市场支持：A 股、港股、美股
- 双数据源故障转移
- 批量数据获取
- 本地缓存机制

**使用方法:**
```python
from src.data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()

# 获取单只股票
data = fetcher.get_stock_data("sh600519", period="1d")

# 获取多只股票
stocks = ["sh600519", "sz000002", "AAPL"]
all_data = fetcher.get_multiple_stocks(stocks)

# 获取实时行情
quote = fetcher.get_realtime_quote("sh600519")
print(f"当前价格：{quote['current_price']}")
print(f"涨跌幅：{quote['change_percent']}%")
```

### 2. 新闻智能检索 (`src/news_fetcher.py`)

**核心功能:**
- 多源新闻聚合
- 相关性评分算法
- 去重处理
- 中文分词支持

**使用方法:**
```python
from src.news_fetcher import NewsFetcher

fetcher = NewsFetcher()

# 获取某股票相关新闻
news_list = fetcher.fetch_news("贵州茅台", limit=10)

for news in news_list:
    print(f"标题：{news['title']}")
    print(f"来源：{news['source']}")
    print(f"时间：{news['publish_time']}")
    print(f"相关性：{news['relevance_score']}")
    print(f"链接：{news['url']}")
    print("---")
```

### 3. AI 智能分析 (`src/ai_analyzer.py`)

**包含三个核心分析器:**

#### 3.1 情感分析器 (SentimentAnalyzer)
```python
from src.ai_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# 分析新闻文本
text = "贵州茅台业绩大幅增长，净利润同比增长 20%"
result = analyzer.analyze(text)

print(f"情感得分：{result['score']}")  # -1 到 1
print(f"情感倾向：{result['label']}")  # positive/negative/neutral
print(f"置信度：{result['confidence']}")
```

#### 3.2 技术分析器 (TechnicalAnalyzer)
```python
from src.ai_analyzer import TechnicalAnalyzer
import pandas as pd

# 假设 df 是 OHLCV 数据
df = fetcher.get_stock_data("sh600519", period="6mo")

analyzer = TechnicalAnalyzer()

# 计算所有指标
indicators = analyzer.calculate_all(df)

# 获取交易信号
signals = analyzer.generate_signals(df)
print(signals)
# 输出示例: {'rsi_signal': 'SELL', 'macd_signal': 'BUY', 'overall': 'HOLD'}
```

**技术指标说明:**

| 指标 | 参数 | 含义 | 交易信号 |
|------|------|------|---------|
| **RSI** | 14 日 | 相对强弱指数 | >70 超买卖出，<30 超卖买入 |
| **MACD** | 12,26,9 | 异同移动平均线 | 金叉买入，死叉卖出 |
| **MA** | 5,10,20,60 | 移动平均线 | 上穿均线买入，下穿卖出 |
| **BOLL** | 20,2 | 布林带 | 触下轨买入，触上轨卖出 |
| **KDJ** | 9,3,3 | 随机指标 | K>D 且<20 买入，K<D 且>80 卖出 |

#### 3.3 K 线形态识别
```python
patterns = analyzer.detect_patterns(df.tail(10))

# 支持的形态:
# - doji: 十字星 (变盘信号)
# - hammer: 锤头线 (底部反转)
# - shooting_star: 流星线 (顶部反转)
# - morning_star: 早晨之星 (强烈看涨)
# - evening_star: 黄昏之星 (强烈看跌)
# - engulfing: 吞没形态
```

### 4. 综合评分系统

系统整合技术面和消息面，给出综合评分和建议：

```python
from src.ai_analyzer import ComprehensiveAnalyzer

comprehensive = ComprehensiveAnalyzer()

result = comprehensive.analyze(
    stock_code="sh600519",
    stock_name="贵州茅台"
)

print(f"综合评分：{result['total_score']}/100")
print(f"技术面得分：{result['technical_score']}")
print(f"消息面得分：{result['sentiment_score']}")
print(f"建议操作：{result['recommendation']}")
print(f"置信度：{result['confidence']}%")
print(f"风险提示：{result['risk_warning']}")
```

**评分等级:**
- 80-100: 强烈买入
- 60-79: 谨慎买入
- 40-59: 持有观望
- 20-39: 谨慎卖出
- 0-19: 强烈卖出

---

## 🌐 Web 界面使用指南

### 启动命令
```bash
streamlit run src/web_interface.py --server.port 8501
```

### 界面布局

1. **侧边栏配置区**
   - 选择市场 (A 股/港股/美股)
   - 输入/选择股票代码
   - 设置时间周期
   - 调整技术指标参数
   - 刷新频率设置

2. **主显示区**
   - **股票概览卡片**: 当前价格、涨跌幅、成交量等
   - **K 线图表**: 交互式 Plotly 图表，支持缩放、平移
   - **技术指标图**: MA、MACD、RSI、布林带等
   - **新闻列表**: 最新相关新闻，带情感标签
   - **AI 分析报告**: 综合评分和投资建议

3. **投资组合视图**
   - 多股票对比分析
   - 持仓盈亏统计
   - 风险分散度评估

### 快捷操作
- `R` 键：刷新数据
- `F` 键：全屏查看图表
- `D` 键：切换深色/浅色主题
- `?` 键：显示快捷键帮助

---

## 🧪 测试验证

### 运行全部测试
```bash
pytest tests/ -v --cov=src
```

### 单独测试模块
```bash
# 测试数据获取
pytest tests/test_data_fetcher.py -v

# 测试新闻获取
pytest tests/test_news_fetcher.py -v

# 测试 AI 分析
pytest tests/test_ai_analyzer.py -v

# 测试 Web 界面
pytest tests/test_web_interface.py -v
```

### 预期测试结果
```
============================= test session starts ==============================
collected 15 items

tests/test_config.py::test_config_load PASSED                            [  6%]
tests/test_data_fetcher.py::test_fetch_a_stock PASSED                    [ 13%]
tests/test_data_fetcher.py::test_fetch_hk_stock PASSED                   [ 20%]
tests/test_data_fetcher.py::test_fetch_us_stock PASSED                   [ 26%]
tests/test_news_fetcher.py::test_fetch_news PASSED                       [ 33%]
tests/test_ai_analyzer.py::test_rsi_calculation PASSED                   [ 40%]
tests/test_ai_analyzer.py::test_macd_calculation PASSED                  [ 47%]
tests/test_ai_analyzer.py::test_sentiment_positive PASSED                [ 53%]
tests/test_ai_analyzer.py::test_sentiment_negative PASSED                [ 60%]
tests/test_ai_analyzer.py::test_signal_generation PASSED                 [ 66%]
tests/test_ai_analyzer.py::test_pattern_recognition PASSED               [ 73%]
tests/test_comprehensive.py::test_comprehensive_analysis PASSED          [ 80%]
tests/test_web_interface.py::test_app_launch PASSED                      [ 86%]
tests/test_integration.py::test_full_pipeline PASSED                     [ 93%]
tests/test_integration.py::test_error_handling PASSED                    [100%]

======================== 15 passed in 12.34s ================================
```

---

## ❓ 常见问题 (FAQ)

### Q1: 无法获取 A 股数据？
**A:** 检查网络连接，确保能访问国内财经网站。如仍失败，系统会自动切换到备用数据源。也可考虑配置 Tushare Token。

### Q2: 新闻获取速度慢？
**A:** 首次运行会建立缓存，后续会使用缓存数据。可调整 `CACHE_EXPIRY_SECONDS` 参数平衡实时性和速度。

### Q3: AI 分析结果不准确？
**A:** 
1. 检查是否配置了有效的 LLM API Key
2. 调整情感分析阈值参数
3. 增加新闻样本数量
4. 结合多个技术指标综合判断

### Q4: Web 界面打不开？
**A:** 
1. 检查端口 8501 是否被占用
2. 尝试更换端口：`--server.port 8502`
3. 检查防火墙设置
4. 查看日志文件定位错误

### Q5: 如何添加自定义数据源？
**A:** 继承 `BaseDataFetcher` 类，实现 `fetch()` 方法，然后在配置中注册：

```python
class MyCustomFetcher(BaseDataFetcher):
    def fetch(self, symbol: str) -> pd.DataFrame:
        # 你的实现
        pass

# 在 settings.py 中注册
DATA_FETCHERS = ["akshare", "yfinance", "my_custom"]
```

---

## 📝 免责声明

1. **非投资建议**: 本系统提供的所有分析、评分、建议均基于算法和历史数据，仅供参考，不构成任何投资建议或推荐。

2. **数据准确性**: 虽然系统努力从权威来源获取数据，但不保证数据的完整性、准确性和及时性。投资决策请以官方交易所数据为准。

3. **风险提示**: 股市有风险，投资需谨慎。用户应充分了解股票投资的风险，根据自身风险承受能力做出决策。

4. **技术局限**: AI 分析存在局限性，无法预测突发事件、政策变化等不可量化因素。历史表现不代表未来收益。

5. **使用责任**: 用户使用本系统进行投资决策所产生的任何损失，开发者不承担任何责任。

6. **合规声明**: 本系统不提供证券咨询服务，不涉及资金托管、交易执行等功能。用户应遵守当地法律法规进行证券投资。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境搭建
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 预提交钩子
pre-commit install

# 运行代码格式化
black src/ tests/
isort src/ tests/

# 运行静态检查
flake8 src/ tests/
mypy src/
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📬 联系方式

- 项目主页：https://github.com/yourusername/stock_analyzer
- 问题反馈：https://github.com/yourusername/stock_analyzer/issues
- 邮箱：your.email@example.com

---

**⚠️ 再次提醒：股市有风险，投资需谨慎！本系统仅供参考，请独立判断。**

*最后更新：2024 年*
