import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from pykrx import stock
import plotly.express as px
import matplotlib.pyplot as plt
import warnings
import datetime as dt
import plotly.graph_objects as go
from pages import Sharpe
from pages import Correlation
from pages import Stock_Chatbot
import to_upward
from streamlit_extras.switch_page_button import switch_page
import scipy.optimize as sco
import plotly.subplots as sp
from streamlit_extras.colored_header import colored_header

if "page" not in st.session_state:
    st.session_state.page = "home"





DATA_PATH = "./"
SEED = 42

# 데이터 불러오는 함수(캐싱)
@st.cache_data(ttl=900)  # 캐싱 데코레이터
def load_csv(path):
    return pd.read_csv(path)

# 데이터 불러오기
data = load_csv(f"{DATA_PATH}labeled_data_final2.csv")

# 오류 방지를 위한 패딩 함수
str_list = data.Code.astype(str).to_list()
target_len = 6
padded_str_list = to_upward.pad_str(str_list, target_len)
data.Code = padded_str_list

# 마감일 및 시작일
end = dt.datetime.today().date().strftime("%Y%m%d")
start = (dt.datetime.today().date() - dt.timedelta(365)).strftime("%Y%m%d")


def reset_seeds(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)


if 'type_of_user' not in st.session_state:
    st.session_state.type_of_user = None

if 'selected_sectors' not in st.session_state:
    st.session_state.selected_sectors = []

if 'recommended_stocks' not in st.session_state:
    st.session_state.recommended_stocks = []


warnings.filterwarnings('ignore')


# Survey Part
colored_header(
    label='투자성향에 맞는 포트폴리오 추천',
    description="고객님의 투자 성향에 맞는 포트폴리오를 간편하게 추천해드립니다.",
    color_name="blue-70",
)


st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #F8FFD3;
        width=10px
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def init():
    if 'show_description' not in st.session_state:
        st.session_state.show_description = False

init()
if st.sidebar.checkbox('주식 섹터에 대한 설명 보기', help='클릭 시 설명을 확인할 수 있습니다.'):
    st.session_state.show_description = True
else:
    st.session_state.show_description = False




if st.session_state.show_description:
    st.write("#### 주식 섹터에 대한 설명")
    if st.button('dividend (배당)',key='dividend'):
        st.write("""
        **설명**: 주식회사가 주주에게 이익을 나눠주는 것을 의미합니다. 배당률이 높은 주식은 안정적인 수익을 기대할 수 있습니다.\n
        **예시**: 대한민국에서는 삼성전자, SK텔레콤 등이 배당률이 높은 주식으로 알려져 있습니다.
        """)
    if st.button('growth (성장)', key='growth'):
        st.write("""
        **설명**: 회사의 매출이나 이익이 지속적으로 증가하는지를 살펴보는 지표입니다. 성장률이 높은 주식은 높은 수익률을 기대할 수 있습니다.\n
        **예시**: NAVER, 카카오 등은 지속적인 성장을 보이는 주식입니다.
        """)    
    if st.button('value (가치)', key='value'):
        st.write("""
        **설명**: 주식의 현재 가격이 그 실제 가치에 비해 얼마나 저렴한지를 평가하는 지표입니다. P/E 비율, P/B 비율 등을 통해 측정합니다.\n
        **예시**: POSCO, 현대차 등은 가치 투자의 대상으로 여겨지는 경우가 많습니다.
        """)    
    if st.button('performance (실적)', key='performance'):
        st.write("""
        **설명**: 회사의 경영 실적을 평가하는 지표입니다. 매출, 이익, EBITDA 등을 통해 회사의 경영 성과를 측정합니다.\n
        **예시**: 삼성전자, SK하이닉스 등은 높은 매출과 이익을 보이는 회사입니다.
        """)
    if st.button('business (경영)', key='business'):
        st.write("""
        **설명**: 회사의 경영 성과를 평가하는 지표입니다. 영업이익률, 순이익률 등을 통해 회사의 경영 상태를 파악합니다.\n
        **예시**: 삼성바이오로직스, 셀트리온 등은 높은 영업이익률을 가진 회사입니다.
        """)    
    if st.button('finance (재무)', key='finance'):
        st.write("""
        **설명**: 회사의 재무 상태를 평가하는 지표입니다. 부채비율, 유동비율 등을 통해 회사의 재무 안정성을 측정합니다.\n
        **예시**: 삼성SDI, LG화학 등은 재무상태가 안정적인 회사로 알려져 있습니다.
        """)    
    if st.button('volitality (변동성)', key='volatility'):
        st.write("""
        **설명**: 주식 가격의 변동 폭을 의미합니다. 변동성이 높은 주식은 높은 수익, 높은 리스크를 가질 수 있습니다.\n
        **예시**: 바이오 관련 주식이나 새로운 기술을 개발한 스타트업 주식 등은 변동성이 높은 경우가 많습니다.
        """)







sectors = ["dividend", "growth", "value", "performance", "business", "finance", "volitality"]

# 필터링
def filter_by_grade(data, sector):
    if sector in ['finance']:
        return (data[sector] == 'A+') | (data[sector] == 'A') | (data[sector] == 'B') | (data[sector] == 'C') | (data[sector] == 'D') | (data[sector] == 'E')
    elif sector in ['volitality']:
        return (data[sector] == 'A+') | (data[sector] == 'A') | (data[sector] == 'B') | (data[sector] == 'C')
    elif sector in ['business']:
        return (data[sector] == 'A') | (data[sector] == 'B')
    elif sector in ['dividend']:
        return (data[sector] == 'A') | (data[sector] == 'B') | (data[sector] == 'C')
    elif sector in ['value']:
        return (data[sector] == 'A+') | (data[sector] == 'A') | (data[sector] == 'B') | (data[sector] == 'C')
    elif sector in ['growth']:
        return (data[sector] == 'A') | (data[sector] == 'A-') | (data[sector] == 'B') | (data[sector] == 'B-')
    elif sector in ['performance']:
        return (data[sector] == 'A+') | (data[sector] == 'A') | (data[sector] == 'B') | (data[sector] == 'C')



if 'selected_sectors' not in st.session_state:
    st.session_state.selected_sectors = st.multiselect("중요하게 여기는 가치 2가지~3가지를 선택하세요.", options=sectors,max_selections=3,help='주식 섹터에 관한 설명이 필요하다면, 왼쪽 사이드바에서 주식 섹터에 관한 설명보기를 클릭하세요.')
else:
    st.session_state.selected_sectors = st.multiselect("중요하게 여기는 가치 2가지~3가지를 선택하세요.", options=sectors, max_selections=3,default=st.session_state.selected_sectors,help='주식 섹터에 관한 설명이 필요하다면, 왼쪽 사이드바에서 주식 섹터에 관한 설명보기를 클릭하세요.')


if len(st.session_state.selected_sectors) ==2:
    st.success(f"선택하신 섹터는 {', '.join(st.session_state.selected_sectors)} 입니다.")


    stocks = []

    # 섹터 선택 확인
    if st.session_state.selected_sectors:
        conditions = [filter_by_grade(data, sector) for sector in st.session_state.selected_sectors]
        final_condition = np.logical_and.reduce(conditions)
        stocks = data[final_condition]["Name"].to_list()
        st.markdown(f""":blue[**추천 종목**]:chart_with_upwards_trend: *{stocks}*""")
        # 추천 종목을 표시
        # 추천 종목 계산 후
        st.session_state.recommended_stocks = stocks
        st.markdown(f"""
            <span style='font-size: 20px;'>
            <div style="text-align: center; color: #4655f2;">
                <strong>당신의 투자 성향을 선택해주세요.</strong>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            .stButton > button {
                background-color: #F8FFD3;
                width: 100%; /
                display: inline-block;
                margin: 0; /
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def page1():
            want_to_corr = st.button("안정형")
            if want_to_corr:
                st.session_state.type_of_user = "안정형"
                switch_page("Correlation")


        def page2():

            want_to_sharpe = st.button("수익형")
            if want_to_sharpe:
                st.session_state.type_of_user = "수익형"
                switch_page("Sharpe")


        col1, col2 = st.columns(2)
        with col1:
            page1()
        with col2:
            page2()

elif len(st.session_state.selected_sectors) == 3:
    st.success(f"선택하신 섹터는 {', '.join(st.session_state.selected_sectors)} 입니다.")


    stocks = []

    # 섹터 선택 확인
    if st.session_state.selected_sectors:
        conditions = [filter_by_grade(data, sector) for sector in st.session_state.selected_sectors]
        final_condition = np.logical_and.reduce(conditions)
        stocks = data[final_condition]["Name"].to_list()
        st.markdown(f""":blue[**추천 종목**]:chart_with_upwards_trend: *{stocks}*""")
        # 추천 종목을 표시
        # 추천 종목 계산 후
        st.session_state.recommended_stocks = stocks


        st.markdown(f"""
            <span style='font-size: 20px;'>
            <div style="text-align: center; color: #4655f2;">
                <strong>당신의 투자 성향을 선택해주세요.</strong>
            </div>
            """, unsafe_allow_html=True)


        st.markdown(
            """
            <style>
            .stButton > button {
                background-color: #F8FFD3;
                width: 100%; /
                display: inline-block;
                margin: 0; /
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def page1():
            want_to_corr = st.button("안정형")
            if want_to_corr:
                st.session_state.type_of_user = "안정형"
                switch_page("Correlation")


        def page2():

            want_to_sharpe = st.button("수익형")
            if want_to_sharpe:
                st.session_state.type_of_user = "수익형"
                switch_page("Sharpe")


        col1, col2 = st.columns(2)
        with col1:
            page1()
        with col2:
            page2()



        
else:
    st.warning('섹터를 2개 이상 선택해주세요.')



if st.sidebar.checkbox('주식 섹터 기준 info', help='클릭 시 설명을 확인할 수 있습니다.', key="sector_info2"):
    st.session_state.show_description = True
else:
    st.session_state.show_description = False

# "주식 섹터에 대한 설명"이 True면 내용을 표시
if st.session_state.show_description:
    st.write("### 주식 섹터 기준 설명")
    st.write("""
             좋은 포트폴리오를 제공하기 위해 저희는 평균 이상의 등급을 가진 종목들을 추천드립니다. \n 
             각 섹터에 포함된 등급은 다음과 같습니다.""")

    st.write("#### 배당 (Dividend): [A,B,C,D,E 中]")
    st.write("""
    A (최상위 배당주): 이 등급의 주식은 탁월한 배당 수익률을 자랑합니다. 안정적이고 높은 배당률은 장기 투자자들에게 이상적인 선택이 될 수 있으며, 주식 포트폴리오의 안정 요소로 작용할 수 있습니다. \n
    B (상위 배당주): 이 등급의 주식은 상당히 높은 배당률을 제공하여 안정적인 수익 기대가 가능합니다. 장기적인 투자 전략을 가진 투자자들에게 좋은 선택이 될 수 있습니다. \n
    C (보통 배당주): 이 등급은 미디엄 레벨의 배당률을 제공하는 주식을 나타냅니다. 성장 가능성과 배당 수익 사이에서 균형을 찾고자 하는 투자자에게 적합한 선택입니다. \n
    """)

    st.write("#### 성장 (Growth): [A,A-,B,B-,C+,C,D 中]")
    st.write("""
    A (높은 연별 성장): 이 그룹의 주식은 장기적인 관점에서 높은 성장률을 보여주는 특성이 있습니다. 분기별 매출 성장과 순익 성장률이 뛰어난 기업들이 포함되어 있습니다. \n
    A- (단기 손실폭 큰 그룹): 이 그룹은 연 성장률은 높지만 단기적으로 높은 손실폭을 보일 수 있는 주식을 나타냅니다. 장기적인 투자 전략을 가진 투자자들에게 유리한 선택이 될 수 있습니다. \n
    B (단기 성장성 큰 그룹): 이 그룹은 단기적인 시간 동안 높은 성장률을 보여주는 주식을 나타냅니다. 빠르게 변화하는 시장 환경에 유연하게 대응할 수 있는 기업들이 속해 있습니다. \n
    B- (중간 성장 그룹): 이 그룹은 일정한 성장률을 유지하면서 안정적인 성장을 보여주는 주식을 표시합니다. 안정적인 성장을 추구하는 투자자들에게 좋은 선택이 될 수 있습니다. \n
    """)    

    st.write("#### 가치 (Value): [A+,A,B,C,D,E,F 中]")
    st.write("""
    A+ (최상위 가치): 이 등급은 시장에서 상위 99% 이상의 가치를 가진 주식을 나타냅니다. 이러한 주식은 현재 시장 가치보다 높은 가치를 가지며, 투자자들에게 매우 높은 가치 투자 기회를 제공합니다. \n
    A (상위 가치): 이 등급은 현재 시장 가치보다 높은 가치를 가진 주식을 나타냅니다. 투자자들에게 높은 가치 투자 기회를 제공하며, 안정적인 수익률을 기대할 수 있습니다. \n
    B (중위 가치): 이 등급은 시장 평균 가치보다 약간 높은 가치를 가진 주식을 표시합니다. 이러한 주식은 안정적인 투자 기회와 더불어 잠재적인 성장 가능성을 제공합니다. \n
    C (평균 가치): 이 등급은 시장 평균 가치에 근접한 주식을 나타냅니다. 안정적인 투자 기회를 제공하면서도 일정한 성장 가능성이 있는 주식입니다. \n
    """)    

    st.write("#### 경영 (Business): [A,B,C,D 中]")
    st.write("""
    A (뛰어난 경영 성과): 이 등급은 영업이익률과 순이익률이 모두 뛰어난 기업을 나타냅니다. 경영 효율성과 높은 이익률이 특징입니다. \n
    B (평균 이상의 경영 성과): 이 등급은 평균 이상의 영업이익률과 순이익률을 보여주는 기업을 나타냅니다. 안정적인 경영과 성장 가능성을 겸비한 기업들이 속해 있습니다. \n
    """)    

    st.write("#### 재무 (Finance): [A+,A,B,C,D,E,F,G,H,I 中]")
    st.write("""
    A+ (최상위 등급): 이 등급의 기업들은 매우 높은 당좌비율과 유동비율을 보유하고 있어, 금융 안정성이 매우 뛰어납니다. 현금 흐름이 음수일지라도 빠르게 현금화가 가능하고 부채 상환 여력이 충분합니다. \n
    A (우수 등급): 이 등급의 기업들도 뛰어난 당좌비율과 유동비율을 자랑합니다. A+ 등급에 비해 당좌비율이 약간 낮지만, 여전히 금융 구조가 강력하고 안정적입니다. \n
    B (양호 등급): 이 등급의 기업들은 상위 11% 이상의 당좌비율과 유동비율을 보유하고 있으며, 현금 흐름도 평균 이상입니다. 재무 안정성이 높은 편입니다. \n
    C (보통 등급): 이 등급의 기업들은 B 등급과 유사한 당좌비율과 유동비율을 보유하고 있지만, 현금 흐름이 평균 이하입니다. 그러나 안정적인 재무 구조를 유지하고 있습니다. \n
    D (중하 등급): 이 등급의 기업들은 유동비율과 당좌비율이 낮은 편이며, 현금 흐름이 하위권에 속합니다. 그러나 부채 상환 여력은 아직 충분합니다. \n
    E (하위 등급): 이 등급의 기업들은 점차 부채 상환 능력이 낮아지고 금융 상태가 악화되는 특징이 있습니다. 하지만, 이러한 기업들도 특정 조건 하에 성장 가능성을 보여줄 수 있습니다. \n
    """)    

    st.write("#### 실적 (Performance): [A+,A,B,C,D,E 中]")
    st.write("""
    A+ (세계적 수준): 이 등급은 세계적인 수준의 기업을 나타내며, 국내에서는 삼성전자와 같은 기업이 해당됩니다. 이 기업들은 글로벌 시장에서도 높은 경쟁력을 보유하고 있습니다. \n
    A (우수 수준): 이 등급의 기업들은 매우 높은 매출과 이익률을 보유하고 있으며, 대부분의 영역에서 우수한 성과를 보여줍니다. \n
    B (평균 이상): 이 등급의 기업들은 주당 매출이 높으며, A 등급에 비해 EBITDA 마진이 약간 낮지만, 전반적으로 평균 이상의 성과를 보여줍니다. \n
    C (평균 수준): 이 등급의 기업들은 주당 매출이 낮으며, EBITDA 마진이 A 클래스보다 낮습니다. 그러나 일부 지표에서는 미흡하지 않은 성과를 보여줄 수 있습니다. \n
    """)    

    st.write("#### 변동성 (Volatility): [A+,A,B,C,D,E 中]")
    st.write("""
    A+ (압도적인 금양): 이 등급의 주식은 모든 지표에서 압도적인 성과를 보여줍니다. 안정된 수익률과 낮은 변동성이 특징입니다. \n
    A (장기적 우수성): 이 등급의 주식은 장기적으로 높은 수익률을 보여주며, 5년 평균 수익률이 상위 94% 이상입니다. \n
    B (단기적 우수성): 이 등급의 주식은 52주 변동률이 크며, 단기적으로 높은 수익률을 보여줍니다. 장기적인 수익률은 약간 낮을 수 있습니다. \n
    C (평균 이상의 수익률): 이 등급의 주식은 5년 평균 수익률이 평균 이상입니다. 안정적인 수익을 기대할 수 있습니다. \n
    """)

