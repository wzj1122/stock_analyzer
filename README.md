# 📈 股票实时监测与 AI 分析系统

一个功能完整的股票实时监测、新闻检索和 AI 智能分析系统，为用户提供科学客观的投资建议。

## ✨ 主要功能

### 1. 实时股票监测
- 🔄 支持 A 股、港股、美股实时行情
- 📊 自动刷新股价数据（可配置间隔）
- 📈 多维度技术指标计算（MA、MACD、RSI、布林带等）

### 2. 新闻智能检索
- 🌐 聚合全球权威财经媒体（新浪财经、东方财富、Reuters、Bloomberg 等）
- 🔍 基于关键词的智能新闻过滤
- 📰 实时推送与关注股票相关的重大新闻

### 3. AI 智能分析
- 🤖 NLP 情感分析（支持中英文）
- 📉 K 线形态自动识别
- 🎯 多因子综合评分系统
- 💡 生成买卖建议和风险提示

### 4. 可视化界面
- 🖥️ Streamlit 交互式 Web 界面
- 📊 Plotly 动态图表（K 线图、指标图、对比图）
- 📱 响应式设计，支持多设备访问

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Redis（可选，用于缓存）

### 安装步骤

```bash
# 1. 进入项目目录
cd stock_analyzer

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑.env 文件，填入你的 API Keys

# 5. 启动 Web 界面
streamlit run src/web_interface.py
```

### 配置说明

在 `config/settings.py` 中可以配置：

```python
# 关注的股票代码
WATCHLIST_STOCKS = [
    "000001.SZ",  # 平安银行
    "600519.SS",  # 贵州茅台
    "AAPL",       # 苹果
    "TSLA",       # 特斯拉
]

# 数据刷新间隔（秒）
REFRESH_INTERVAL = 60

# 技术指标
TECHNICAL_INDICATORS = ["MA", "MACD", "RSI", "BOLL"]
```

## 📁 项目结构

```
stock_analyzer/
├── config/                 # 配置文件
│   └── settings.py        # 系统配置
├── src/                    # 源代码
│   ├── main.py            # 主程序入口
│   ├── data_fetcher.py    # 股票数据获取
│   ├── news_fetcher.py    # 新闻检索
│   ├── ai_analyzer.py     # AI 分析引擎
│   └── web_interface.py   # Web 界面
├── tests/                  # 测试文件
├── logs/                   # 日志目录
├── data/                   # 数据缓存
├── requirements.txt        # 依赖列表
└── README.md              # 说明文档
```

## 🛠️ 核心模块

### 1. 数据获取模块 (`data_fetcher.py`)
- 支持多个数据源（akshare、yfinance）
- 自动故障转移
- 批量数据获取

### 2. 新闻检索模块 (`news_fetcher.py`)
- RSS Feed 解析
- 网页爬虫
- 相关性评分

### 3. AI 分析模块 (`ai_analyzer.py`)
- **SentimentAnalyzer**: 新闻情感分析
- **TechnicalAnalyzer**: 技术指标计算和信号生成
- **AIStockAnalyzer**: 综合分析和投资建议

### 4. Web 界面模块 (`web_interface.py`)
- 实时数据展示
- 交互式图表
- 投资组合管理

## 📊 技术指标

系统支持以下技术分析指标：

| 指标 | 说明 | 用途 |
|------|------|------|
| MA5/10/20/60 | 移动平均线 | 趋势判断 |
| EMA12/26 | 指数移动平均线 | MACD 计算 |
| MACD | 异同移动平均线 | 买卖信号 |
| RSI | 相对强弱指标 | 超买超卖 |
| BOLL | 布林带 | 波动区间 |
| VOL_MA | 成交量均线 | 量能分析 |

## 🎯 分析流程

```
1. 获取股票实时行情
       ↓
2. 计算技术指标
       ↓
3. 检索相关新闻
       ↓
4. 情感分析 (NLP)
       ↓
5. 技术面 + 消息面综合评分
       ↓
6. 生成投资建议
       ↓
7. 可视化展示
```

## ⚠️ 风险提示

**重要声明：**
1. 本系统提供的分析仅供参考，不构成投资建议
2. 股市有风险，投资需谨慎
3. AI 分析存在局限性，请结合个人判断
4. 过往表现不代表未来收益
5. 用户应自行承担投资风险

## 🔧 高级配置

### 使用 OpenAI API 增强分析

在 `.env` 文件中配置：

```bash
OPENAI_API_KEY=your_api_key_here
```

### 自定义新闻源

编辑 `config/settings.py`：

```python
NEWS_SOURCES = [
    {
        "name": "自定义新闻源",
        "url": "https://example.com/rss",
        "enabled": True
    }
]
```

### 添加更多股票

```python
WATCHLIST_STOCKS.extend([
    "00700.HK",  # 腾讯控股
    "NVDA",      # 英伟达
])
```

## 🧪 测试

```bash
# 运行单元测试
pytest tests/

# 运行单个模块测试
python -m pytest tests/test_data_fetcher.py -v
```

## 📝 更新日志

### v1.0.0 (2024)
- ✨ 初始版本发布
- 📈 支持 A 股、港股、美股
- 🤖 AI 情感分析
- 📊 技术指标分析
- 🌐 多新闻源聚合

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请通过 GitHub Issues 联系。

---

**🎉 祝您投资顺利！**

*记住：理性投资，风险控制第一。*
