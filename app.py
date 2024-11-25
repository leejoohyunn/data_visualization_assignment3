import streamlit as st
import folium
from folium import plugins
import pandas as pd
import geopandas as gpd
import plotly.express as px
from streamlit_folium import folium_static
import plotly.graph_objects as go
from datetime import datetime
import os

# 페이지 기본 설정
st.set_page_config(
    page_title="서울시 인구 통계 대시보드",
    page_icon="🏙️",
    layout="wide"
)

# CSS 스타일 적용
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background-color: #f5f5f5;
    }
    .stat-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 제목 및 설명
st.title("🏙️ 서울시 인구 통계 대시보드")
st.markdown("---")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 상대 경로로 변경
    df = pd.read_csv("data/df_seoul_pop_cleaned.csv")
    gdf = gpd.read_file('data/refined_korea.json')
    return df, gdf

# 데이터 로드
df_seoul_pop_cleaned, gdf = load_data()

# 나머지 코드는 동일...

# 사이드바
st.sidebar.header("📊 데이터 필터")
selected_year = st.sidebar.selectbox(
    "연도 선택",
    ["2024"]  # 실제 데이터에 맞게 연도 리스트 수정
)

# 메인 컨텐츠를 3개 컬럼으로 분할
col1, col2, col3 = st.columns(3)

# 주요 통계 표시
with col1:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.metric(
        label="총 인구수",
        value=f"{df_seoul_pop_cleaned['인구수'].sum():,.0f}명",
        delta="2.5% vs 전년"  # 실제 데이터에 맞게 수정
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.metric(
        label="평균 출생률",
        value=f"{df_seoul_pop_cleaned['인구수'].mean():,.1f}명",
        delta="-1.2% vs 전년"  # 실제 데이터에 맞게 수정
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.metric(
        label="가장 높은 인구 구역",
        value=df_seoul_pop_cleaned.loc[df_seoul_pop_cleaned['인구수'].idxmax(), '행정구'],
        delta="변동없음"  # 실제 데이터에 맞게 수정
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# 지도와 차트를 나란히 배치
col_map, col_chart = st.columns([3, 2])

with col_map:
    st.subheader("🗺️ 서울시 구별 인구 현황")
    
    # Folium 지도 생성
    city_hall = [37.566345, 126.977893]
    m = folium.Map(
        location=city_hall,
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Choropleth 레이어 추가
    choropleth = folium.Choropleth(
        geo_data=gdf,
        data=df_seoul_pop_cleaned,
        columns=('행정구', '인구수'),
        key_on='feature.properties.행정구',
        fill_color='RdYlBu',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='인구수',
        smooth_factor=0
    ).add_to(m)
    
    # 툴팁 추가
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['행정구'],
            aliases=['구역: '],
            style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
        )
    )
    
    # 미니맵 추가
    plugins.MiniMap().add_to(m)
    
    # 전체화면 버튼 추가
    plugins.Fullscreen().add_to(m)
    
    # 지도 표시
    folium_static(m)

with col_chart:
    st.subheader("📊 구별 인구 분포")
    
    # 막대 차트
    fig_bar = px.bar(
        df_seoul_pop_cleaned.sort_values('인구수', ascending=True).tail(10),
        x='인구수',
        y='행정구',
        orientation='h',
        title='상위 10개 구 인구 현황',
        color='인구수',
        color_continuous_scale='RdYlBu'
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title=None,
        xaxis_title="인구수",
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 파이 차트
    fig_pie = px.pie(
        df_seoul_pop_cleaned,
        values='인구수',
        names='행정구',
        title='구별 인구 비율'
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 하단에 상세 데이터 테이블 추가
st.markdown("---")
st.subheader("📋 상세 데이터")
st.dataframe(
    df_seoul_pop_cleaned.style.highlight_max(subset=['인구수'], color='lightgreen'),
    use_container_width=True
)

# 페이지 하단 정보
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """,
    unsafe_allow_html=True
)
