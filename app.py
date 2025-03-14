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

    # 1. 单品牌车型销量分析
    st.header("1️⃣ 单品牌车型销量分析")
    
    # 选择品牌
    brands = sorted(df['品牌'].unique())
    selected_brand = st.selectbox('选择品牌', brands)
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
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
        
        # 添加数据标签
        fig_models.update_traces(
            mode='lines+markers+text',
            textposition='top center'
        )
        
        st.plotly_chart(fig_models, use_container_width=True)
    
    with col2:
        # 创建车型月度销量表格
        model_monthly = brand_data.pivot_table(
            index='车型',
            columns='日期',
            values='销量',
            aggfunc='sum'
        ).round(0)
        
        # 添加合计行
        model_monthly.loc['合计'] = model_monthly.sum()
        
        # 格式化数字显示
        formatted_model_monthly = model_monthly.map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        
        st.dataframe(
            formatted_model_monthly,
            use_container_width=True,
            height=400
        )

    # 2. 品牌总销量分析
    st.header("2️⃣ 品牌总销量分析")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 计算所有品牌的月度总销量
        brand_total = df.groupby(['日期', '品牌'])['销量'].sum().reset_index()
        
        # 计算每个月的总销量和去年同期销量
        monthly_sum = brand_total.groupby('日期')['销量'].sum().reset_index()
        monthly_sum['去年同期'] = monthly_sum['销量'].shift(12)
        monthly_sum['同比增长率'] = (monthly_sum['销量'] - monthly_sum['去年同期']) / monthly_sum['去年同期'] * 100
        
        # 创建堆叠柱状图和增长率折线图
        fig_brand_total = go.Figure()
        
        # 添加每个品牌的堆叠柱状图
        for brand in brands:
            brand_data = brand_total[brand_total['品牌'] == brand]
            fig_brand_total.add_trace(
                go.Bar(
                    name=brand,
                    x=brand_data['日期'],
                    y=brand_data['销量'],
                    text=brand_data['销量'].round(0),
                    textposition='inside',
                )
            )
        
        # 添加同比增长率折线图
        fig_brand_total.add_trace(
            go.Scatter(
                name='同比增长率',
                x=monthly_sum['日期'],
                y=monthly_sum['同比增长率'],
                yaxis='y2',
                line=dict(color='red', width=2),
                mode='lines+markers'
            )
        )
        
        # 更新布局
        fig_brand_total.update_layout(
            title='品牌月度总销量及同比增长率',
            barmode='stack',
            yaxis=dict(
                title='销量',
                side='left'
            ),
            yaxis2=dict(
                title='同比增长率 (%)',
                side='right',
                overlaying='y',
                tickformat='.1f'
            ),
            xaxis_title='时间',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        # 设置y轴从0开始
        fig_brand_total.update_yaxes(rangemode="tozero")
        
        st.plotly_chart(fig_brand_total, use_container_width=True)
    
    with col4:
        # 创建品牌月度销量表格
        brand_monthly_table = brand_total.pivot_table(
            index='品牌',
            columns='日期',
            values='销量',
            aggfunc='sum'
        ).round(0)
        
        # 添加合计行
        brand_monthly_table.loc['合计'] = brand_monthly_table.sum()
        
        # 格式化数字显示
        formatted_brand_monthly = brand_monthly_table.map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        
        st.dataframe(
            formatted_brand_monthly,
            use_container_width=True,
            height=400
        )

    # 3. 品牌对比分析
    st.header("3️⃣ 品牌对比分析")
    
    # 使用多选框选择要对比的品牌
    selected_brands = st.multiselect(
        '选择要对比的品牌（建议选择2-5个品牌）',
        options=brands,
        default=brands[:2]  # 默认选择前两个品牌
    )
    
    if len(selected_brands) < 2:
        st.warning('请至少选择两个品牌进行对比')
    else:
        # 获取所有选中品牌的数据
        compare_data = []
        for brand in selected_brands:
            brand_data = df[df['品牌'] == brand].groupby('日期')['销量'].sum().reset_index()
            brand_data['品牌'] = brand
            brand_data['去年同期'] = brand_data['销量'].shift(12)
            brand_data['同比增长率'] = (brand_data['销量'] - brand_data['去年同期']) / brand_data['去年同期'] * 100
            compare_data.append(brand_data)
        
        # 合并所有品牌数据
        all_compare_data = pd.concat(compare_data)
        
        col7, col8 = st.columns(2)
        
        with col7:
            # 创建销量对比图
            fig_compare = go.Figure()
            
            # 为每个品牌添加柱状图
            for i, brand in enumerate(selected_brands):
                brand_data = all_compare_data[all_compare_data['品牌'] == brand]
                fig_compare.add_trace(
                    go.Bar(
                        name=brand,
                        x=brand_data['日期'],
                        y=brand_data['销量'],
                        text=brand_data['销量'].round(0),
                        textposition='auto',
                        offsetgroup=i
                    )
                )
            
            # 更新布局
            fig_compare.update_layout(
                title='品牌销量对比',
                barmode='group',
                yaxis_title='销量',
                xaxis_title='时间',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)
        
        with col8:
            # 创建增长率对比图
            fig_growth = go.Figure()
            
            # 添加0%基准线
            fig_growth.add_hline(
                y=0, 
                line_dash="dash", 
                line_color="gray",
                annotation_text="0%",
                annotation_position="left"
            )
            
            # 为每个品牌添加增长率折线
            for brand in selected_brands:
                brand_data = all_compare_data[all_compare_data['品牌'] == brand]
                fig_growth.add_trace(
                    go.Scatter(
                        name=brand,
                        x=brand_data['日期'],
                        y=brand_data['同比增长率'],
                        mode='lines+markers',
                        line=dict(width=2),
                        marker=dict(size=8)
                    )
                )
            
            # 更新布局
            fig_growth.update_layout(
                title='品牌同比增长率对比',
                yaxis_title='同比增长率 (%)',
                xaxis_title='时间',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified'
            )
            
            # 设置y轴格式
            fig_growth.update_yaxes(tickformat='.1f')
            
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # 创建详细数据表格
        st.subheader("详细对比数据")
        
        # 数据透视表
        compare_table = all_compare_data.pivot_table(
            index=['日期'],
            columns=['品牌'],
            values=['销量', '同比增长率'],
            aggfunc={'销量': 'sum', '同比增长率': 'first'}
        ).round(1)
        
        # 重新排序列以使销量和增长率交替显示
        new_columns = []
        for brand in selected_brands:
            new_columns.extend([('销量', brand), ('同比增长率', brand)])
        compare_table = compare_table[new_columns]
        
        # 格式化数据显示
        formatted_compare_table = compare_table.copy()
        for brand in selected_brands:
            formatted_compare_table[('销量', brand)] = formatted_compare_table[('销量', brand)].map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
            formatted_compare_table[('同比增长率', brand)] = formatted_compare_table[('同比增长率', brand)].map(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
        
        st.dataframe(
            formatted_compare_table.sort_index(ascending=False),
            use_container_width=True,
            height=400
        )

except Exception as e:
    st.error(f"加载数据时出错: {str(e)}")
    st.info("请确保'汽车销量数据.xlsx'文件在正确的位置。") 