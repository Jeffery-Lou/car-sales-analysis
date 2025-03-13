import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="汽车销量分析",
    page_icon="🚗",
    layout="wide"
)

# 设置页面标题
st.title("🚗 汽车销量数据分析")

# 读取数据
@st.cache_data
def load_data():
    # 读取Excel文件
    df = pd.read_excel("汽车销量数据.xlsx")
    
    # 将宽表格转换为长表格，保留汽车品牌和车型列
    df_melted = df.melt(
        id_vars=['汽车品牌', '车型', '售价'],  # 保持不变的列
        var_name='日期',                    # 日期列名
        value_name='销量'                   # 销量列名
    )
    
    # 将日期列转换为datetime类型
    df_melted['日期'] = pd.to_datetime(df_melted['日期'].astype(str), format='%Y%m')
    
    # 重命名列以匹配之前的代码
    df_melted = df_melted.rename(columns={'汽车品牌': '品牌'})
    
    # 将销量中的空值替换为0
    df_melted['销量'] = df_melted['销量'].fillna(0)
    
    return df_melted[['日期', '品牌', '车型', '销量']]

# 加载数据
try:
    df = load_data()
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("按品牌和车型的销量趋势")
        
        # 选择品牌
        brands = sorted(df['品牌'].unique())
        selected_brand = st.selectbox('选择品牌', brands)
        
        # 过滤选定品牌的数据
        brand_data = df[df['品牌'] == selected_brand]
        
        # 创建车型销量趋势图
        fig_models = px.line(
            brand_data,
            x='日期',
            y='销量',
            color='车型',
            title=f'{selected_brand}各车型销量趋势',
            labels={'日期': '时间', '销量': '月度销量'}
        )
        st.plotly_chart(fig_models, use_container_width=True)
    
    with col2:
        st.subheader("品牌总销量趋势")
        
        # 计算每个品牌每月的总销量
        brand_monthly = df.groupby(['日期', '品牌'])['销量'].sum().reset_index()
        
        # 创建品牌总销量趋势图
        fig_brands = px.line(
            brand_monthly,
            x='日期',
            y='销量',
            color='品牌',
            title='各品牌总销量趋势',
            labels={'日期': '时间', '销量': '月度总销量'}
        )
        st.plotly_chart(fig_brands, use_container_width=True)
        
    # 显示选定品牌的销量统计
    selected_brands = st.multiselect(
        "选择品牌（可多选）",
        options=sorted(df['品牌'].unique()),
        default=[]
    )
    
    if selected_brands:
        st.subheader("选定品牌销量统计")
        # 计算选定品牌的总销量
        brand_stats = df[df['品牌'].isin(selected_brands)].groupby('品牌')['销量'].agg([
            ('总销量', 'sum'),
            ('平均月销量', 'mean')
        ]).round(0)
        
        # 格式化数字显示
        brand_stats['总销量'] = brand_stats['总销量'].apply(lambda x: f"{x:,.0f}")
        brand_stats['平均月销量'] = brand_stats['平均月销量'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            brand_stats,
            use_container_width=True
        )

    # 添加数据表格部分
    st.subheader("详细数据")
    
    # 添加日期范围选择
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("开始日期", df['日期'].min())
    with col_date2:
        end_date = st.date_input("结束日期", df['日期'].max())
    
    # 筛选数据
    mask = (df['日期'].dt.date >= start_date) & (df['日期'].dt.date <= end_date)
    if selected_brands:
        mask = mask & (df['品牌'].isin(selected_brands))
    
    filtered_df = df[mask].copy()
    
    # 计算月度同比增长率
    filtered_df['年份'] = filtered_df['日期'].dt.year
    filtered_df['月份'] = filtered_df['日期'].dt.month
    
    # 添加排序和搜索功能的数据表格
    st.dataframe(
        filtered_df.pivot_table(
            index=['品牌', '车型'],
            columns=['年份', '月份'],
            values='销量',
            aggfunc='sum'
        ).round(2),
        use_container_width=True,
        height=400
    )

except Exception as e:
    st.error(f"加载数据时出错: {str(e)}")
    st.info("请确保'汽车销量数据.xlsx'文件在正确的位置。") 