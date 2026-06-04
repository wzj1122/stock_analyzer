"""
Streamlit Web界面
提供实时股票监测和AI分析的用户界面
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import StockDataFetcher
from src.news_fetcher import NewsFetcher
from src.ai_analyzer import AIStockAnalyzer
from config.settings import get_config, Config


def initialize_session_state():
    """初始化session state"""
    if 'data_fetcher' not in st.session_state:
        st.session_state.data_fetcher = StockDataFetcher()
    if 'news_fetcher' not in st.session_state:
        st.session_state.news_fetcher = NewsFetcher()
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIStockAnalyzer()
    if 'config' not in st.session_state:
        st.session_state.config = get_config()
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}


def create_price_chart(stock_code: str, df: pd.DataFrame, indicators: dict) -> go.Figure:
    """
    创建价格图表
    
    Args:
        stock_code: 股票代码
        df: 价格数据
        indicators: 技术指标
        
    Returns:
        Plotly图表对象
    """
    # 创建子图
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{stock_code} 价格走势', '成交量', '技术指标')
    )
    
    # K线图
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='red',
            decreasing_line_color='green'
        ),
        row=1, col=1
    )
    
    # 添加均线
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='orange', width=1), name='MA5'), row=1, col=1)
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='purple', width=1), name='MA20'), row=1, col=1)
    
    # 布林带
    if 'BB_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='gray', width=1, dash='dash'), name='BB Upper'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='gray', width=1, dash='dash'), name='BB Lower', fill=None), row=1, col=1)
    
    # 成交量
    colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'green' for i in range(len(df))]
    fig.add_trace(
        go.Bar(x=df.index, y=df['volume'], marker_color=colors, name='Volume'),
        row=2, col=1
    )
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='blue', width=1), name='RSI'), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # 布局
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="日期", row=3, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="成交量", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    
    return fig


def render_stock_card(stock_result: dict):
    """渲染股票信息卡片"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="当前价格",
            value=f"{stock_result['current_price']:.2f}",
            delta=f"{stock_result['change_percent']:.2f}%"
        )
    
    with col2:
        rec = stock_result['recommendation']
        st.metric(
            label="AI建议",
            value=rec['action'],
            delta=f"置信度：{rec['confidence']*100:.0f}%"
        )
    
    with col3:
        tech = stock_result['technical_analysis']
        st.metric(
            label="技术信号",
            value=tech['signal'].upper(),
            delta=f"强度：{tech['strength']*100:.0f}%"
        )
    
    with col4:
        sentiment = stock_result['news_sentiment']
        polarity = sentiment.get('average_polarity', 0)
        if polarity > 0.2:
            delta = "正面"
        elif polarity < -0.2:
            delta = "负面"
        else:
            delta = "中性"
        st.metric(
            label="新闻情绪",
            value=delta,
            delta=f"极性：{polarity:.2f}"
        )


def render_analysis_details(stock_result: dict):
    """渲染详细分析结果"""
    # 技术面分析
    with st.expander("📊 技术面分析详情", expanded=True):
        tech = stock_result['technical_analysis']
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("技术指标")
            indicators = tech.get('indicators', {})
            for name, value in indicators.items():
                if value is not None:
                    st.write(f"**{name}**: {value:.2f}")
        
        with col2:
            st.subheader("检测到的形态")
            patterns = tech.get('patterns', [])
            if patterns:
                for pattern in patterns:
                    st.info(f"🔍 {pattern['name']} ({pattern['type']})")
            else:
                st.write("未检测到明显K线形态")
        
        st.subheader("信号原因")
        reasons = tech.get('reasons', [])
        if reasons:
            for reason in reasons:
                st.write(f"• {reason}")
        else:
            st.write("无明显信号")
    
    # 消息面分析
    with st.expander("📰 消息面分析详情"):
        sentiment = stock_result['news_sentiment']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("正面新闻", sentiment.get('positive_count', 0))
        with col2:
            st.metric("负面新闻", sentiment.get('negative_count', 0))
        with col3:
            st.metric("中性新闻", sentiment.get('neutral_count', 0))
        
        if stock_result.get('analyzed_news'):
            st.subheader("相关新闻")
            for news in stock_result['analyzed_news'][:5]:
                sent = news.get('sentiment', {})
                polarity = sent.get('polarity', 0)
                
                if polarity > 0.2:
                    emoji = "🟢"
                elif polarity < -0.2:
                    emoji = "🔴"
                else:
                    emoji = "⚪"
                
                st.write(f"{emoji} **{news.get('title', '无标题')}**")
                st.write(f"   来源：{news.get('source', '未知')} | 情绪极性：{polarity:.2f}")
                st.write("")
    
    # 综合建议
    with st.expander("💡 综合投资建议", expanded=True):
        rec = stock_result['recommendation']
        
        st.write(rec['summary'])
        
        if rec.get('risks'):
            st.warning("⚠️ 风险提示:")
            for risk in rec['risks']:
                st.write(f"• {risk}")
        
        st.info(f"🎯 综合评分：{rec['composite_score']:.2f} | 置信度：{rec['confidence']*100:.1f}%")


def main():
    """主函数"""
    st.set_page_config(
        page_title="股票实时监测与AI分析系统",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化
    initialize_session_state()
    config = st.session_state.config
    
    # 标题
    st.title("📈 股票实时监测与AI分析系统")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")
        
        # 刷新按钮
        if st.button("🔄 刷新数据", use_container_width=True):
            st.session_state.analysis_results = {}
            st.session_state.last_update = None
            st.rerun()
        
        # 自动刷新
        auto_refresh = st.checkbox("自动刷新 (每60秒)", value=False)
        
        st.divider()
        
        # 选择股票
        st.subheader("📋 关注列表")
        selected_stocks = st.multiselect(
            "选择要分析的股票",
            options=config.WATCHLIST_STOCKS,
            default=config.WATCHLIST_STOCKS[:5]
        )
        
        st.divider()
        
        # 显示最后更新时间
        if st.session_state.last_update:
            st.info(f"最后更新：{st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # 风险提示
        st.warning(config.RISK_WARNING)
    
    # 主内容区
    if not selected_stocks:
        st.warning("请至少选择一只股票进行分析")
        return
    
    # 获取和分析数据
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    data_fetcher = st.session_state.data_fetcher
    news_fetcher = st.session_state.news_fetcher
    ai_analyzer = st.session_state.ai_analyzer
    
    results = {}
    
    for i, stock_code in enumerate(selected_stocks):
        status_text.text(f"正在分析 {stock_code}... ({i+1}/{len(selected_stocks)})")
        
        try:
            # 获取股票信息
            stock_info = data_fetcher.get_stock_info(stock_code)
            
            # 获取历史数据
            price_data = data_fetcher.get_historical_data(stock_code, period="90d")
            
            # 计算技术指标
            if not price_data.empty:
                price_data = ai_analyzer.technical_analyzer.calculate_indicators(price_data)
            
            # 获取相关新闻
            stock_name = stock_info.get('name', '')
            news_list = news_fetcher.search_stock_news(
                stock_codes=[stock_code],
                stock_names=[stock_name] if stock_name else [],
                limit=20
            )
            
            # AI综合分析
            analysis_result = ai_analyzer.analyze_stock(
                stock_code=stock_code,
                stock_info=stock_info,
                price_data=price_data,
                news_list=news_list
            )
            
            results[stock_code] = analysis_result
            
            progress_bar.progress((i + 1) / len(selected_stocks))
            
        except Exception as e:
            st.error(f"分析 {stock_code} 时出错：{str(e)}")
            continue
    
    status_text.text("分析完成!")
    progress_bar.empty()
    
    # 更新最后时间
    st.session_state.last_update = datetime.now()
    st.session_state.analysis_results = results
    
    # 显示结果
    if results:
        # 选项卡
        tabs = st.tabs(["📊 总览", "📈 详细分析", "📉 对比分析"])
        
        with tabs[0]:
            st.subheader("投资组合总览")
            
            # 为每只股票创建卡片
            for stock_code, result in results.items():
                with st.container():
                    st.markdown(f"### {result['stock_name']} ({stock_code})")
                    render_stock_card(result)
                    st.divider()
        
        with tabs[1]:
            st.subheader("详细分析")
            
            # 选择要查看详情的股票
            detail_stock = st.selectbox(
                "选择股票查看详细分析",
                options=list(results.keys()),
                format_func=lambda x: f"{results[x]['stock_name']} ({x})"
            )
            
            if detail_stock and detail_stock in results:
                result = results[detail_stock]
                
                # 显示图表
                price_data = data_fetcher.get_historical_data(detail_stock, period="90d")
                if not price_data.empty:
                    chart = create_price_chart(
                        detail_stock,
                        price_data,
                        result['technical_analysis'].get('indicators', {})
                    )
                    st.plotly_chart(chart, use_container_width=True)
                
                # 显示详细分析
                render_analysis_details(result)
        
        with tabs[2]:
            st.subheader("股票对比分析")
            
            if len(results) > 1:
                # 创建对比表格
                comparison_data = []
                for code, result in results.items():
                    comparison_data.append({
                        "股票代码": code,
                        "股票名称": result['stock_name'],
                        "当前价格": f"{result['current_price']:.2f}",
                        "涨跌幅": f"{result['change_percent']:.2f}%",
                        "AI建议": result['recommendation']['action'],
                        "置信度": f"{result['recommendation']['confidence']*100:.0f}%",
                        "技术信号": result['technical_analysis']['signal'],
                        "情绪极性": f"{result['news_sentiment']['average_polarity']:.2f}",
                        "综合评分": f"{result['recommendation']['composite_score']:.2f}"
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # 对比图表
                fig = go.Figure()
                
                for code, result in results.items():
                    fig.add_trace(go.Bar(
                        name=result['stock_name'],
                        x=['技术评分', '情绪评分', '综合评分'],
                        y=[
                            result['technical_analysis']['strength'] * 2,
                            result['news_sentiment']['average_polarity'],
                            result['recommendation']['composite_score']
                        ]
                    ))
                
                fig.update_layout(
                    title="股票评分对比",
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("请选择多只股票进行对比分析")
    
    # 自动刷新
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()


if __name__ == "__main__":
    main()
