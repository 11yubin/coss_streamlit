# -*- coding: utf-8 -*-
"""개별프로젝트_2(송유빈).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y-UAYjt7WmE_9kGLvto2rcqYFnigeHXW

# 주제: 다양한 방법으로 숙박업소 데이터 분석하기

### 기획의도
- 최근 휴가철을 맞아 여행 계획을 알아보던 중, 국내 숙박업소 위치 비율/코로나19가 숙박업계에 미친 영향 등 다양한 방법으로 숙박업 데이터를 분석하고 싶다는 생각이 들어 해당 프로젝트를 선정하게 되었다.

### 이용 데이터
- 공공데이터 포털에 있는 '행정안전부_숙박업' 데이터 (csv)
- KOSIS 국가 통계 포털에 있는 '지역별 면적' 데이터 (csv)

## 모듈 임포트
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# %config InlineBackend.figure_format = 'retina'

plt.rc('font', family='NanumGothic')


df = pd.read_csv('fulldata_03_11_03_P_숙박업.csv', encoding='CP949')
df.head()

from pyproj import Proj, transform

proj_1 = Proj(init='epsg:2097')
proj_2 = Proj(init='epsg:4326')

converted = transform(proj_1, proj_2, df['좌표정보(x)'].values, df['좌표정보(y)'].values)
df['좌표정보(x)'], df['좌표정보(y)'] = converted[0], converted[1]
df.rename(columns={'좌표정보(x)':'경도', '좌표정보(y)':'위도'}, inplace=True)
df[['경도', '위도']]

df_new = df[['번호', '개방서비스명', '인허가일자', '폐업일자', '소재지면적', '소재지전체주소',
                 '도로명전체주소', '사업장명', '최종수정시점', '데이터갱신일자', '업태구분명',
                 '위도', '경도', '건물지상층수', '건물지하층수', '사용시작지상층',
                 '사용끝지상층', '사용시작지하층', '사용끝지하층', '한실수', '양실수']]

df_open = df_new.loc[df['영업상태명']!='폐업']
df_close = df_new.loc[df['영업상태명']=='폐업']

"""## 가설 설정 및 분석

### 가설 1. 영업중인 숙박업소는 부산/제주도 등 여행지에 가장 많이 분포할 것이다.
"""

location = df_open['소재지전체주소'].str.split().str[0]

sns.countplot(x=location)
plt.gcf().set_size_inches(15, 8)
plt.show()

"""- 지역별 면적 대비 개수로 분석"""

area = pd.read_csv('지역별_면적_20230628230940.csv', encoding='CP949')
area = area[['남북한별 ', '2021']][16:]
area.rename(columns={'남북한별 ':'위치', '2021':'면적'}, inplace=True)
area['면적'] = area['면적'].astype(int)

loc_cnt = location.value_counts().to_frame()
loc_cnt['위치'] = loc_cnt.index
loc_cnt_area = pd.merge(area, loc_cnt)
loc_cnt_area.rename(columns={'count':'개수'}, inplace=True)

loc_cnt_area['면적대비개수'] = loc_cnt_area['개수']/loc_cnt_area['면적']
loc_cnt_area.sort_values(by='면적대비개수', ascending=False, inplace=True)

sns.barplot(data=loc_cnt_area, x='위치', y='면적대비개수')

"""- 지도로 확인"""

df_open_loc = df_open[['위도', '경도']].dropna()

from folium.plugins import HeatMap

m = folium.Map(
  location=[35.8053542,127.7043419],
  zoom_start=7
)

heatmap = HeatMap(data=zip(df_open_loc['위도'], df_open_loc['경도']), min_opacity=0.2, max_val=7,
                radius=10, blur=1.5, max_zoom=5,color='red')
m.add_child(heatmap)

st_data = st_folium(m, width=725)

"""- 결론: 절대적인 값은 경기도에 가장 많으나, 면적 대비 개수의 비율을 구해보면 서울이 압도적으로 많다. 면적이 작은 광역시의 경우, 면적 대비 개수를 구했을 때 상대적으로 큰 값이 나오기 때문에 높은 순위에 위치해있다.

### 가설2. 코로나19 이후로 숙박업체의 연평균 폐업률이 늘어났을 것이다.
"""

df_close.head()

closed_year = df_close['폐업일자'].str[:4].value_counts()
closed_year = closed_year.sort_index()[10:-1]
closed_year.tail()

closed_year_df = closed_year.to_frame().reset_index()
closed_year_df.rename(columns={'폐업일자':'폐업수', 'index':'연도'}, inplace=True)
closed_year_df['연도'] = closed_year_df['연도'].astype(int)
closed_year_df.head()

px.line(closed_year_df, x='연도', y='폐업수').update_layout(title='연도별 폐업수')

px.scatter(closed_year_df, x='연도', y='폐업수')

after_covid = closed_year_df.loc[closed_year_df['연도']>=2020]
after_covid.head()

before_covid = closed_year_df.loc[closed_year_df['연도']<2020]
before_covid.head()

df_covid = pd.DataFrame()
df_covid['코로나'] = ['이전', '이후']
df_covid['연평균 폐업수'] = [before_covid['폐업수'].sum()/len(before_covid), after_covid['폐업수'].sum()/len(after_covid)]
px.histogram(df_covid, x='코로나', y='연평균 폐업수', color='코로나')

before_covid = closed_year_df.loc[closed_year_df['연도']<2020][-3:]
before_covid.head()

df_covid = pd.DataFrame()
df_covid['코로나'] = ['이전', '이후']
df_covid['연평균 폐업수'] = [before_covid['폐업수'].sum()/len(before_covid), after_covid['폐업수'].sum()/len(after_covid)]
px.histogram(df_covid, x='코로나', y='연평균 폐업수', color='코로나')

before_covid = closed_year_df.loc[closed_year_df['연도']<2020][-10:]
before_covid

df_covid = pd.DataFrame()
df_covid['코로나'] = ['이전', '이후']
df_covid['연평균 폐업수'] = [before_covid['폐업수'].sum()/len(before_covid), after_covid['폐업수'].sum()/len(after_covid)]
px.histogram(df_covid, x='코로나', y='연평균 폐업수', color='코로나')

"""- 결론: 전체적인 그래프를 볼 때는 특이점이 크게 나타나지 않았지만, 연평균 폐업률을 보았을 때는 코로나 이전에 비해 코로나 시기를 겪은 2020년부터 2022년까지 약 2배 높은 폐업률을 보였다. 이를 통해 코로나가 숙박업계의 폐업에 미친 영향이 있을 것이라고 판단했으나, 코로나 이전 3년/10년 간의 데이터를 분석해보니 현재 숙박업계의 폐업률이 증가하는 추세였다는 것을 알 수 있었다. 따라서 코로나19가 숙박업계 폐업에 큰 영향을 미쳤다는 유의미한 결과를 발견할 수는 없었다. 그리고, 2003년도에 유독 많은 숫자의 숙박업소가 폐업했는데, 당시의 사회적 상황에 따른 이유가 있을 것이라고 생각된다."""


