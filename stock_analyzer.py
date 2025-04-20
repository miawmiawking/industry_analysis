import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import akshare as ak
import numpy as np
from collections import Counter
import time
import plotly.express as px
import plotly.graph_objects as go
import json
from streamlit.components.v1 import html
import streamlit.components.v1 as components
import io

# 设置页面配置
st.set_page_config(
    page_title="股票行业概念分析",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0277BD;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E3F2FD;
        font-weight: 500;
    }
    .card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .analyze-button {
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        border-top: 1px solid #E0E0E0;
        padding-top: 20px;
        color: #757575;
    }
    .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
        color: #0277BD;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .stock-input {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        background-color: #F5F7FA;
    }
    .plot-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        background-color: white;
        padding: 10px;
        margin-top: 15px;
    }
    /* 加载动画样式 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 10px;
        border: 3px solid rgba(0, 123, 255, 0.3);
        border-radius: 50%;
        border-top-color: #0277BD;
        animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    /* 提示卡片样式 */
    .tip-card {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    /* 标签样式 */
    .tag {
        display: inline-block;
        background-color: #E3F2FD;
        color: #0277BD;
        padding: 2px 8px;
        border-radius: 12px;
        margin-right: 5px;
        font-size: 0.8rem;
    }
    /* 示例代码样式 */
    .code-example {
        background-color: #F5F7FA;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .code-example:hover {
        background-color: #E3F2FD;
        border-color: #90CAF9;
    }
</style>
""", unsafe_allow_html=True)

# 设置页面标题
st.markdown('<h1 class="main-header">📊 股票行业概念分析器</h1>', unsafe_allow_html=True)

# 添加应用说明
st.markdown("""
<div class="card">
    <h3 style="color: #0277BD; margin-top: 0;">应用说明</h3>
    <p>该应用用于分析一组股票的行业和概念分布情况，帮助您快速了解投资组合的行业集中度和相关主题。</p>
    <div class="tip-card">
        <p><strong>使用方法：</strong></p>
        <ul>
            <li>请输入1-500个股票代码，用空格、顿号(、)或逗号(,，)分隔</li>
            <li>点击"自动分析"按钮后系统将展示股票的基本信息表格</li>
            <li>分析结果包括行业和概念的分布饼图，点击可查看详情</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# 创建缓存函数获取股票基本信息
@st.cache_data(ttl=3600)  # 缓存1小时
def get_stock_basic_info():
    """获取A股所有股票的基本信息"""
    try:
        return ak.stock_info_a_code_name()
    except Exception as e:
        st.error(f"获取股票基本信息时出错: {e}")
        return pd.DataFrame(columns=['code', 'name'])

# 创建缓存函数获取行业板块信息
@st.cache_data(ttl=3600)  # 缓存1小时
def get_industry_list():
    """获取东方财富-行业板块列表"""
    try:
        return ak.stock_board_industry_name_em()
    except Exception as e:
        st.error(f"获取行业板块列表时出错: {e}")
        return pd.DataFrame(columns=['板块名称', '板块代码'])

# 创建缓存函数获取概念板块信息
@st.cache_data(ttl=3600)  # 缓存1小时
def get_concept_list():
    """获取东方财富-概念板块列表"""
    try:
        return ak.stock_board_concept_name_em()
    except Exception as e:
        st.error(f"获取概念板块列表时出错: {e}")
        return pd.DataFrame(columns=['板块名称', '板块代码'])

# 创建缓存函数获取行业成分股
@st.cache_data(ttl=3600)  # 缓存1小时
def get_industry_stocks(industry_name):
    """获取特定行业的成分股"""
    try:
        df = ak.stock_board_industry_cons_em(symbol=industry_name)
        return df
    except Exception as e:
        st.warning(f"获取行业 '{industry_name}' 成分股时出错: {e}")
        return pd.DataFrame(columns=['代码', '名称'])

# 创建缓存函数获取概念成分股
@st.cache_data(ttl=3600)  # 缓存1小时
def get_concept_stocks(concept_name):
    """获取特定概念的成分股"""
    try:
        df = ak.stock_board_concept_cons_em(symbol=concept_name)
        return df
    except Exception as e:
        st.warning(f"获取概念 '{concept_name}' 成分股时出错: {e}")
        return pd.DataFrame(columns=['代码', '名称'])

# 股票代码输入区域
stock_codes_input = st.text_area(
    "请输入股票代码（1-500个，用空格、顿号或逗号分隔）:", 
    height=120, 
    help="例如: 600519 000858、002594,601398，300750",
    key="stock_input",
    placeholder="在此输入股票代码，如：600519、000858、002594，601398..."
)

# 解析股票代码函数
def parse_stock_codes(input_text):
    """
    解析输入的股票代码文本，支持空格、顿号(、)或中英文逗号(,，)分隔，并验证股票代码格式
    
    参数:
        input_text: 输入的股票代码文本
        
    返回:
        解析后的股票代码列表和无效代码列表
    """
    if not input_text:
        return [], []
    
    # 替换顿号和逗号（包括中英文）为空格，然后按空格分割
    codes = re.split(r'[、,，\s]+', input_text.strip())
    # 移除空字符串
    codes = [code for code in codes if code]
    
    # 标准化股票代码格式并验证
    formatted_codes = []
    invalid_codes = []
    
    for code in codes:
        # 移除可能的前缀
        if code.upper().startswith(('SH', 'SZ')):
            code = code[2:]
        
        # 验证股票代码格式：必须是6位数字
        if re.match(r'^\d{6}$', code):
            formatted_codes.append(code)
        else:
            invalid_codes.append(code)
    
    return formatted_codes, invalid_codes

# 获取股票信息的函数
def get_stock_info(stock_codes):
    """
    获取股票的基本信息、所属行业和概念
    
    参数:
        stock_codes: 股票代码列表
        
    返回:
        包含股票信息的DataFrame
    """
    # 初始化结果DataFrame
    result_df = pd.DataFrame(columns=["序号", "股票代码", "股票名称", "所属行业", "相关概念"])
    
    # 获取股票基本信息
    stock_info = get_stock_basic_info()
    
    # 创建股票代码到名称的映射
    code_to_name = dict(zip(stock_info['code'], stock_info['name']))
    
    # 获取行业分类数据
    industry_data = get_industry_list()
    
    # 获取概念分类数据
    concept_data = get_concept_list()
    
    # 创建进度条容器
    progress_container = st.empty()
    status_container = st.empty()
    
    # 提前缓存所有行业的成分股数据
    industry_stocks_cache = {}
    with progress_container.container():
        st.markdown("<p><div class='loading-spinner'></div> <b>正在加载所有行业数据...</b></p>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        
        total_industries = len(industry_data)
        for i, (_, row) in enumerate(industry_data.iterrows()):
            industry_name = row['板块名称']
            industry_stocks_cache[industry_name] = get_industry_stocks(industry_name)
            
            # 更新进度和状态
            progress = (i + 1) / total_industries
            progress_bar.progress(progress)
            status_container.markdown(f"正在加载: {industry_name} ({i+1}/{total_industries})")
            
            # 每加载10个行业更新一次界面
            if (i + 1) % 10 == 0 or i == total_industries - 1:
                status_container.markdown(f"已加载 {i+1}/{total_industries} 个行业")
    
    # 提前缓存所有概念的成分股数据
    concept_stocks_cache = {}
    with progress_container.container():
        st.markdown("<p><div class='loading-spinner'></div> <b>正在加载所有概念数据 (这可能需要几分钟时间)...</b></p>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        
        total_concepts = len(concept_data)
        for i, (_, row) in enumerate(concept_data.iterrows()):
            concept_name = row['板块名称']
            concept_stocks_cache[concept_name] = get_concept_stocks(concept_name)
            
            # 更新进度和状态
            progress = (i + 1) / total_concepts
            progress_bar.progress(progress)
            status_container.markdown(f"正在加载: {concept_name} ({i+1}/{total_concepts})")
            
            # 每加载20个概念更新一次界面
            if (i + 1) % 20 == 0 or i == total_concepts - 1:
                status_container.markdown(f"已加载 {i+1}/{total_concepts} 个概念")
    
    # 分析股票数据
    with progress_container.container():
        st.markdown("<p><div class='loading-spinner'></div> <b>正在分析股票数据...</b></p>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        
        total_stocks = len(stock_codes)
        processed_stocks = 0
        not_found_stocks = []
        
        for idx, code in enumerate(stock_codes, 1):
            # 查找股票名称
            stock_name = code_to_name.get(code, None)
            
            if stock_name is None:
                not_found_stocks.append(code)
                stock_name = "未知股票"
            
            # 获取行业信息
            industry = get_stock_industry(code, industry_data, industry_stocks_cache)
            
            # 获取概念信息
            concepts = get_stock_concepts(code, concept_data, concept_stocks_cache)
            
            # 添加到结果DataFrame
            result_df = pd.concat([result_df, pd.DataFrame({
                "序号": [idx],
                "股票代码": [code],
                "股票名称": [stock_name],
                "所属行业": [industry],
                "相关概念": [concepts]
            })], ignore_index=True)
            
            # 更新进度
            processed_stocks += 1
            progress_bar.progress(processed_stocks / total_stocks)
            
            # 每处理5个股票更新一次状态
            if idx % 5 == 0 or idx == len(stock_codes):
                status_container.markdown(f"已分析 {idx}/{total_stocks} 只股票")
        
        # 清除进度容器
        progress_container.empty()
        status_container.empty()
        
        # 如果有未找到的股票，显示警告
        if not_found_stocks:
            st.warning(f"以下股票代码未找到: {', '.join(not_found_stocks)}")
    
    return result_df

def get_stock_industry(stock_code, industry_data, industry_stocks_cache):
    """
    获取股票所属行业，尝试多种方式确保结果准确性
    
    参数:
        stock_code: 股票代码
        industry_data: 行业分类数据
        industry_stocks_cache: 行业成分股缓存
        
    返回:
        行业名称字符串
    """
    # 首先尝试从缓存中查找
    for industry_name, industry_stocks in industry_stocks_cache.items():
        # 检查股票代码是否在此行业的成分股中
        if not industry_stocks.empty and '代码' in industry_stocks.columns:
            if stock_code in industry_stocks['代码'].values:
                return industry_name
    
    # 如果在缓存中没找到，尝试实时查询（可能是新股或缓存不完整）
    try:
        # 尝试通过股票信息接口获取行业
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if not stock_info.empty and '行业' in stock_info.columns:
            industry_from_info = stock_info.loc[stock_info['item'] == '行业', 'value'].values
            if len(industry_from_info) > 0:
                return industry_from_info[0]
    except Exception:
        pass
    
    return "未知行业"

def get_stock_concepts(stock_code, concept_data, concept_stocks_cache):
    """
    获取股票相关概念，使用改进的相关性算法
    
    参数:
        stock_code: 股票代码
        concept_data: 概念分类数据
        concept_stocks_cache: 概念成分股缓存
        
    返回:
        概念名称字符串，多个概念以逗号分隔，最多返回5个最相关的概念
    """
    matched_concepts = []
    
    # 建立概念板块权重表 (基于concept_data的排序)
    concept_weights = {}
    for i, (_, row) in enumerate(concept_data.iterrows()):
        # 越靠前的概念板块权重越高
        concept_weights[row['板块名称']] = len(concept_data) - i
    
    # 从缓存中查找所有概念
    for concept_name, concept_stocks in concept_stocks_cache.items():
        if not concept_stocks.empty and '代码' in concept_stocks.columns:
            if stock_code in concept_stocks['代码'].values:
                # 计算相关性得分 (考虑多个因素)
                relevance_score = 0
                
                # 因素1: 概念的热度/权重 (基于原始排序)
                weight = concept_weights.get(concept_name, 0)
                relevance_score += weight * 0.5  # 权重因素占50%
                
                # 因素2: 概念的精确度 (成分股数量越少越精确)
                stock_count = len(concept_stocks)
                # 成分股在30-100之间的概念最合适，太少可能太小众，太多可能太宽泛
                if 30 <= stock_count <= 100:
                    precision_score = 100
                elif stock_count < 30:
                    precision_score = stock_count
                else:  # stock_count > 100
                    precision_score = max(1, 200 - stock_count)  # 数量越多分数越低
                
                relevance_score += precision_score * 0.5  # 精确度因素占50%
                
                # 因素3: 考虑概念的热度/关注度 (如果有该数据)
                try:
                    concept_detail = concept_data[concept_data['板块名称'] == concept_name]
                    if not concept_detail.empty and '涨跌幅' in concept_detail.columns:
                        # 涨跌幅的绝对值可以作为热度的一个指标
                        change_rate = abs(float(concept_detail['涨跌幅'].values[0].replace('%', '')))
                        heat_score = min(change_rate * 5, 100)  # 最高100分
                        relevance_score += heat_score * 0.2  # 热度因素加成20%
                except Exception:
                    pass
                
                matched_concepts.append((concept_name, relevance_score))
    
    if matched_concepts:
        # 按照相关性得分排序 (得分越高越相关)
        sorted_concepts = sorted(matched_concepts, key=lambda x: x[1], reverse=True)
        # 只取前5个最相关的概念
        top_concepts = [concept[0] for concept in sorted_concepts[:5]]
        return ", ".join(top_concepts)
    else:
        return "暂无相关概念"

# 分析行业分布的函数
def analyze_industry_distribution(stocks_df):
    """
    分析股票的行业分布
    
    参数:
        stocks_df: 包含股票信息的DataFrame
        
    返回:
        行业分布的Counter对象和行业-股票映射字典
    """
    industries = stocks_df["所属行业"].tolist()
    # 过滤掉"未知行业"
    industries = [ind for ind in industries if ind != "未知行业"]
    
    # 创建行业-股票映射字典
    industry_stocks = {}
    for _, row in stocks_df.iterrows():
        industry = row["所属行业"]
        if industry != "未知行业":
            if industry not in industry_stocks:
                industry_stocks[industry] = []
            industry_stocks[industry].append({"代码": row["股票代码"], "名称": row["股票名称"]})
    
    return Counter(industries), industry_stocks

# 分析概念分布的函数
def analyze_concept_distribution(stocks_df):
    """
    分析股票的概念分布
    
    参数:
        stocks_df: 包含股票信息的DataFrame
        
    返回:
        概念分布的Counter对象和概念-股票映射字典
    """
    # 收集所有概念
    all_concepts = []
    concept_stocks = {}
    
    for _, row in stocks_df.iterrows():
        concepts_str = row["相关概念"]
        if concepts_str != "暂无相关概念":
            concepts = [c.strip() for c in concepts_str.split(",")]
            all_concepts.extend(concepts)
            
            # 建立概念-股票映射
            for concept in concepts:
                if concept not in concept_stocks:
                    concept_stocks[concept] = []
                concept_stocks[concept].append({"代码": row["股票代码"], "名称": row["股票名称"]})
    
    # 统计概念出现次数
    concept_counter = Counter(all_concepts)
    return concept_counter, concept_stocks

# 使用Plotly绘制饼图
def plot_distribution_plotly(counter, stocks_map, title, color_scheme='blues'):
    """
    使用Plotly绘制分布饼图
    
    参数:
        counter: 分布计数器
        stocks_map: 类别-股票映射字典
        title: 图表标题
        color_scheme: 颜色方案
        
    返回:
        Plotly图表对象
    """
    if not counter:
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            showarrow=False,
            font=dict(size=20, family="Microsoft YaHei, Arial")
        )
        fig.update_layout(
            title=title,
            title_font=dict(size=20, family="Microsoft YaHei, Arial"),
            height=500
        )
        return fig
    
    # 只展示前10个类别，其余归为"其他"
    if len(counter) > 10:
        top_items = counter.most_common(9)
        other_sum = sum(count for item, count in counter.most_common()[9:])
        if other_sum > 0:
            top_items.append(("其他", other_sum))
            
            # 合并"其他"类别中的股票
            other_stocks = []
            for item, _ in counter.most_common()[9:]:
                if item in stocks_map:
                    other_stocks.extend(stocks_map[item])
            stocks_map["其他"] = other_stocks
            
        labels = [item[0] for item in top_items]
        values = [item[1] for item in top_items]
    else:
        labels = list(counter.keys())
        values = list(counter.values())
    
    # 计算百分比
    total = sum(values)
    percentages = [100.0 * value / total for value in values]
    
    # 创建自定义hover文本
    hover_texts = []
    for label, value, percentage in zip(labels, values, percentages):
        stocks_in_category = len(stocks_map.get(label, []))
        hover_texts.append(
            f"<b>{label}</b><br>"
            f"包含: <b>{stocks_in_category}</b>只股票<br>"
            f"占比: <b>{percentage:.1f}%</b><br>"
            f"点击查看详情"
        )
    
    # 准备股票信息用于点击交互
    custom_data = []
    for label in labels:
        if label in stocks_map:
            # 传递所有股票信息
            stock_list = stocks_map[label]
            custom_data.append(stock_list)
        else:
            custom_data.append([])
    
    # 创建拉出效果的数组
    pulls = [0.02] * len(labels)
    # 找出最大值的索引，将其拉出更多
    max_idx = values.index(max(values))
    pulls[max_idx] = 0.1
    
    # 设置颜色
    if color_scheme == 'blues':
        color_sequence = px.colors.sequential.Blues_r[1:] + px.colors.sequential.PuBu_r[1:]
        bgcolor = "rgba(227, 242, 253, 0.6)"  # 浅蓝色背景
        pull_color = "#1E88E5"  # 拉出部分的颜色
    elif color_scheme == 'oranges':
        color_sequence = px.colors.sequential.Oranges_r[1:] + px.colors.sequential.OrRd_r[1:]
        bgcolor = "rgba(255, 243, 224, 0.6)"  # 浅橙色背景
        pull_color = "#F57C00"  # 拉出部分的颜色
    
    # 为最大值设置特殊颜色
    colors = color_sequence[:len(labels)]
    colors[max_idx] = pull_color
    
    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='percent+value',  # 同时显示百分比和数量
        hoverinfo='text',
        hovertext=hover_texts,
        marker=dict(
            colors=colors,
            line=dict(color='#FFFFFF', width=2),
            pattern=dict(
                shape=["", "", "", "x", "", "", "", ".", "", ""]  # 添加纹理效果
            )
        ),
        textfont=dict(size=14, family="Microsoft YaHei, Arial"),  # 设置中文字体
        textposition='inside',  # 文本放在饼图内部
        hole=.4,  # 中心孔
        customdata=custom_data,  # 用于点击交互
        pull=pulls,  # 拉出效果
        rotation=45,  # 旋转角度增加动感
        direction='clockwise',  # 顺时针方向
        sort=False,  # 不排序，保持原始顺序
        insidetextorientation='radial',  # 文本径向排列
    )])
    
    # 将最大的扇区拉出
    fig.update_traces(pull=pulls)
    
    # 添加中心文本
    total_items = sum(values)
    fig.add_annotation(
        text=f"<b>共{total_items}只</b><br>股票",
        x=0.5, y=0.5,
        font=dict(size=16, color="#0D47A1", family="Microsoft YaHei, Arial"),
        showarrow=False,
        xanchor="center",
        yanchor="middle"
    )
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, family="Microsoft YaHei, Arial"),
            x=0.5
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family="Microsoft YaHei, Arial")
        ),
        height=550,  # 增加高度以容纳更多内容
        margin=dict(t=60, b=100, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Microsoft YaHei, Arial"),
        uniformtext=dict(minsize=12, mode='hide'),
        showlegend=True,
        # 添加水印
        annotations=[
            dict(
                text="点击扇形查看详情",
                x=0.5, y=0.5,
                xshift=0, yshift=60,
                font=dict(size=11, color="#555555"),
                showarrow=False,
                xanchor="center",
                yanchor="middle"
            )
        ],
        # 添加悬停效果设置
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Microsoft YaHei, Arial"
        ),
    )
    
    # 添加动态效果的帧
    frames = []
    for i in range(1, 36):
        frames.append(
            go.Frame(
                data=[go.Pie(
                    labels=labels,
                    values=values,
                    rotation=45 + i*10,  # 旋转角度
                    pull=pulls
                )]
            )
        )
    fig.frames = frames
    
    return fig

# 自定义按钮样式
analyze_button_html = """
<style>
div.stButton > button:first-child {
    background-color: #1E88E5;
    background-image: linear-gradient(135deg, #1976D2, #42A5F5);
    color: white;
    font-size: 16px;
    font-weight: bold;
    border: none;
    padding: 8px 20px 8px 15px;
    border-radius: 30px;
    width: auto;
    height: auto;
    transition: all 0.3s;
    margin-left: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-transform: none;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}

div.stButton > button:first-child:before {
    content: '⚙️';
    margin-right: 8px;
    font-size: 18px;
    animation: spin 5s linear infinite;
    display: inline-block;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

div.stButton > button:first-child:hover {
    background-image: linear-gradient(135deg, #0D47A1, #1976D2);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

div.stButton > button:first-child:active {
    transform: translateY(1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
"""
st.markdown(analyze_button_html, unsafe_allow_html=True)

# 添加重置按钮功能
def reset_analysis():
    """重置分析结果，清空会话状态"""
    for key in ['stocks_df', 'industry_distribution', 'industry_stocks_map', 
                'concept_distribution', 'concept_stocks_map', 'analysis_done',
                'selected_industry', 'selected_concept']:
        if key in st.session_state:
            del st.session_state[key]

# 添加重置按钮
if st.session_state.get('analysis_done', False):
    if st.button("重置分析", key="reset_button"):
        reset_analysis()
        st.experimental_rerun()

# 主程序
if st.button("自动分析", key="analyze_button"):
    # 检查输入是否为空
    if not stock_codes_input:
        st.error("⚠️ 请输入股票代码")
    else:
        # 解析股票代码
        stock_codes, invalid_codes = parse_stock_codes(stock_codes_input)
        
        # 显示无效代码警告
        if invalid_codes:
            st.warning(f"⚠️ 检测到以下无效的股票代码: {', '.join(invalid_codes)}")
        
        # 检查股票代码数量
        if len(stock_codes) < 1:
            st.error("⚠️ 请至少输入1个有效的股票代码")
        elif len(stock_codes) > 500:
            st.error("⚠️ 输入的股票代码不应超过500个")
        else:
            try:
                # 设置更长的超时时间
                st.warning(f"正在分析 {len(stock_codes)} 只股票，请耐心等待...")
                
                # 获取股票信息
                stocks_df = get_stock_info(stock_codes)
                
                # 将数据保存到session_state中以便于在选择框交互时不丢失
                st.session_state.stocks_df = stocks_df
                
                # 分析行业和概念分布
                industry_distribution, industry_stocks_map = analyze_industry_distribution(stocks_df)
                concept_distribution, concept_stocks_map = analyze_concept_distribution(stocks_df)
                
                # 保存分布数据到session_state
                st.session_state.industry_distribution = industry_distribution
                st.session_state.industry_stocks_map = industry_stocks_map
                st.session_state.concept_distribution = concept_distribution
                st.session_state.concept_stocks_map = concept_stocks_map
                
                # 设置标志表示分析已完成
                st.session_state.analysis_done = True
                
                # 显示分析完成提示
                st.success("✅ 分析完成！")
                
                # 自动滚动到结果部分
                js = '''
                <script>
                    function scroll_to_results() {
                        var results = document.querySelector('h2:contains("股票信息表格")');
                        if (results) {
                            results.scrollIntoView({behavior: 'smooth'});
                        }
                    }
                    setTimeout(scroll_to_results, 500);
                </script>
                '''
                components.html(js, height=0)
                
            except Exception as e:
                st.error(f"分析过程中发生错误: {str(e)}")
                st.info("请尝试重新输入股票代码或稍后再试")

# 检查是否已有分析结果
if st.session_state.get('analysis_done', False):
    # 从session_state获取数据
    stocks_df = st.session_state.stocks_df
    industry_distribution = st.session_state.industry_distribution
    industry_stocks_map = st.session_state.industry_stocks_map
    concept_distribution = st.session_state.concept_distribution
    concept_stocks_map = st.session_state.concept_stocks_map
    
    # 添加分析摘要
    st.markdown("""
    <div class="card" style="margin-top: 30px;">
        <h3 style="color: #0277BD; margin-top: 0;">分析摘要</h3>
        <p>已完成对 <b>{}</b> 只股票的行业和概念分布分析。</p>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; padding: 15px; min-width: 140px;">
                <div style="font-size: 2rem; font-weight: bold; color: #1E88E5;">{}</div>
                <div>有效股票数</div>
            </div>
            <div style="text-align: center; padding: 15px; min-width: 140px;">
                <div style="font-size: 2rem; font-weight: bold; color: #1E88E5;">{}</div>
                <div>行业数量</div>
            </div>
            <div style="text-align: center; padding: 15px; min-width: 140px;">
                <div style="font-size: 2rem; font-weight: bold; color: #1E88E5;">{}</div>
                <div>概念数量</div>
            </div>
        </div>
    </div>
    """.format(
        len(stocks_df),
        len(stocks_df),
        len(industry_distribution),
        len(concept_distribution)
    ), unsafe_allow_html=True)
    
    # 显示股票信息表格
    st.markdown('<h2 class="sub-header">股票信息表格</h2>', unsafe_allow_html=True)
    
    # 使用自定义CSS样式美化表格
    table_css = """
    <style>
        .stock-table {
            margin-top: 20px;
            margin-bottom: 40px;
        }
        .stock-table th {
            background-color: #E3F2FD !important;
            color: #0D47A1 !important;
            font-weight: bold !important;
        }
        .stock-table tr:nth-child(even) {
            background-color: #F5F7FA !important;
        }
        .stock-table td {
            text-align: left !important;
        }
    </style>
    """
    st.markdown(table_css, unsafe_allow_html=True)
    
    # 添加表格筛选功能
    st.markdown('<div class="stock-table">', unsafe_allow_html=True)
    
    # 添加搜索框
    search_term = st.text_input("🔍 搜索股票代码或名称", key="stock_search")
    
    # 筛选数据
    if search_term:
        filtered_df = stocks_df[
            stocks_df['股票代码'].str.contains(search_term) | 
            stocks_df['股票名称'].str.contains(search_term)
        ]
    else:
        filtered_df = stocks_df
    
    # 显示表格
    st.dataframe(
        filtered_df, 
        use_container_width=True,
        column_config={
            "序号": st.column_config.NumberColumn(width="small"),
            "股票代码": st.column_config.TextColumn(width="medium"),
            "股票名称": st.column_config.TextColumn(width="medium"),
            "所属行业": st.column_config.TextColumn(width="large"),
            "相关概念": st.column_config.TextColumn(width="large"),
        },
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 创建两列布局
    st.markdown('<h2 class="sub-header">分布分析图表</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    # 显示行业分布图
    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("行业分布")
        if industry_distribution:
            # 使用Plotly绘制行业分布图
            fig_industry = plot_distribution_plotly(industry_distribution, industry_stocks_map, "行业分布", "blues")
            
            # 显示饼图
            st.plotly_chart(fig_industry, use_container_width=True)
            
            # 添加关于"其他"类别的说明
            if len(industry_distribution) > 10:
                st.markdown("""
                <div style="font-size: 0.8rem; color: #666; margin-top: 5px; margin-bottom: 15px; font-style: italic;">
                    注：当行业数量超过10个时，仅显示数量最多的前9个行业，其余行业归为"其他"类别。
                </div>
                """, unsafe_allow_html=True)
            
            # 创建一个选择器，让用户选择行业查看股票详情
            st.markdown("<h4 style='margin-top:15px;'>选择行业查看股票详情</h4>", unsafe_allow_html=True)
            industry_names = list(industry_stocks_map.keys())
            if industry_names:
                # 按照包含的股票数量从大到小排序行业
                industry_names = sorted(industry_names, key=lambda x: len(industry_stocks_map[x]), reverse=True)
                
                # 将"其他"类别移动到最后面
                if "其他" in industry_names:
                    industry_names.remove("其他")
                    industry_names.append("其他")
                
                # 使用session_state存储选择的行业，避免刷新问题
                if 'selected_industry' not in st.session_state:
                    st.session_state.selected_industry = industry_names[0]
                
                selected_industry = st.selectbox(
                    "选择行业", 
                    industry_names, 
                    key="industry_select",
                    format_func=lambda x: f"{x} ({len(industry_stocks_map[x])}只股票)",
                    index=industry_names.index(st.session_state.selected_industry) if st.session_state.selected_industry in industry_names else 0,
                    on_change=lambda: setattr(st.session_state, 'selected_industry', st.session_state.industry_select)
                )
                
                if selected_industry:
                    # 显示所选行业的股票
                    st.markdown(f"<h5>行业「{selected_industry}」包含的股票：</h5>", unsafe_allow_html=True)
                    stocks_in_industry = industry_stocks_map[selected_industry]
                    
                    # 创建DataFrame来显示股票
                    if stocks_in_industry:
                        industry_stocks_df = pd.DataFrame(stocks_in_industry)
                        st.dataframe(
                            industry_stocks_df, 
                            column_config={
                                "代码": st.column_config.TextColumn("股票代码", width="medium"),
                                "名称": st.column_config.TextColumn("股票名称", width="medium")
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.info("此行业无股票数据")
            
        else:
            st.info("未找到行业分布数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示概念分布图
    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("概念分布")
        if concept_distribution:
            # 使用Plotly绘制概念分布图
            fig_concept = plot_distribution_plotly(concept_distribution, concept_stocks_map, "概念分布", "oranges")
            
            # 显示饼图
            st.plotly_chart(fig_concept, use_container_width=True)
            
            # 添加关于"其他"类别的说明
            if len(concept_distribution) > 10:
                st.markdown("""
                <div style="font-size: 0.8rem; color: #666; margin-top: 5px; margin-bottom: 15px; font-style: italic;">
                    注：当概念数量超过10个时，仅显示数量最多的前9个概念，其余概念归为"其他"类别。
                </div>
                """, unsafe_allow_html=True)
            
            # 创建一个选择器，让用户选择概念查看股票详情
            st.markdown("<h4 style='margin-top:15px;'>选择概念查看股票详情</h4>", unsafe_allow_html=True)
            concept_names = list(concept_stocks_map.keys())
            if concept_names:
                # 按照包含的股票数量从大到小排序概念
                concept_names = sorted(concept_names, key=lambda x: len(concept_stocks_map[x]), reverse=True)
                
                # 将"其他"类别移动到最后面
                if "其他" in concept_names:
                    concept_names.remove("其他")
                    concept_names.append("其他")
                
                # 使用session_state存储选择的概念，避免刷新问题
                if 'selected_concept' not in st.session_state:
                    st.session_state.selected_concept = concept_names[0]
                
                selected_concept = st.selectbox(
                    "选择概念", 
                    concept_names, 
                    key="concept_select",
                    format_func=lambda x: f"{x} ({len(concept_stocks_map[x])}只股票)",
                    index=concept_names.index(st.session_state.selected_concept) if st.session_state.selected_concept in concept_names else 0,
                    on_change=lambda: setattr(st.session_state, 'selected_concept', st.session_state.concept_select)
                )
                
                if selected_concept:
                    # 显示所选概念的股票
                    st.markdown(f"<h5>概念「{selected_concept}」包含的股票：</h5>", unsafe_allow_html=True)
                    stocks_in_concept = concept_stocks_map[selected_concept]
                    
                    # 创建DataFrame来显示股票
                    if stocks_in_concept:
                        concept_stocks_df = pd.DataFrame(stocks_in_concept)
                        st.dataframe(
                            concept_stocks_df, 
                            column_config={
                                "代码": st.column_config.TextColumn("股票代码", width="medium"),
                                "名称": st.column_config.TextColumn("股票名称", width="medium")
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.info("此概念无股票数据")
            
        else:
            st.info("未找到概念分布数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 添加点击事件说明
    st.markdown("""
    <div style="background-color:#f0f9ff; padding:10px; border-radius:5px; margin:20px 0; text-align:center;">
        <p style="margin:0; color:#0277BD;">
            <strong>提示：</strong> 请使用上方选择框查看每个行业/概念包含的股票详情
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加下载功能
    st.markdown('<h2 class="sub-header">数据导出</h2>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # 添加下载选项
    col1, col2 = st.columns(2)
    
    with col1:
        @st.cache_data
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 将股票信息表格写入第一个Sheet
                df.to_excel(writer, index=False, sheet_name='股票信息表格')
                
                # 如果存在行业分布数据，写入第二个Sheet
                if 'industry_distribution' in st.session_state and st.session_state['industry_distribution']:
                    industry_df = pd.DataFrame(list(st.session_state['industry_distribution'].items()), 
                                             columns=['行业', '股票数量'])
                    industry_df = industry_df.sort_values('股票数量', ascending=False)
                    industry_df.to_excel(writer, index=False, sheet_name='行业分布')
                
                # 如果存在概念分布数据，写入第三个Sheet
                if 'concept_distribution' in st.session_state and st.session_state['concept_distribution']:
                    concept_df = pd.DataFrame(list(st.session_state['concept_distribution'].items()), 
                                            columns=['概念', '股票数量'])
                    concept_df = concept_df.sort_values('股票数量', ascending=False)
                    concept_df.to_excel(writer, index=False, sheet_name='概念分布')
                    
            return output.getvalue()
        
        excel = convert_df_to_excel(stocks_df)
        st.download_button(
            label="📥 下载Excel文件",
            data=excel,
            file_name="股票分析结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_button"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.markdown('<div style="border-top: 1px solid #1E88E5; margin-top: 30px; padding-top: 20px; text-align: center; color: #757575;">数据来源：东方财富、<a href="https://github.com/akfamily/akshare" target="_blank" style="color: #1E88E5; text-decoration: none;">AKShare</a></div>', unsafe_allow_html=True) 
