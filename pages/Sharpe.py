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
from plotly.subplots import make_subplots
import sympy
import to_upward
from streamlit_extras.switch_page_button import switch_page
import io
import base64
import scipy.optimize as sco
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
import yfinance

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


# 마감일 및 시작일
end_03 = dt.datetime(2023,3,1).strftime("%Y%m%d")
start_03 = (dt.datetime(2023,3,1).date() - dt.timedelta(365)).strftime("%Y%m%d")
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


try:
    st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #F8FFD3;
        display: inline-block;
        margin: 0; /
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
    def page3():
        want_to_home = st.button("메인화면")
        if want_to_home:
            switch_page("Home")
    page3()

    st.markdown(f"""
            <span style='font-size: 15px;'>
            <div style=" color: #ff2a00;">
                <strong>투자 유형: [{st.session_state.type_of_user}]</strong>
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"""
            <span style='font-size: 15px;'>
            <div style=" color: #145aa6;">
                <strong>선택한 섹터: {st.session_state.selected_sectors}</strong>
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"""
            <span style='font-size: 15px;'>
            <div style=" color: #19a83b">
                <strong>추천 주식: {st.session_state.recommended_stocks}</strong>
            </div>
            """, unsafe_allow_html=True)

    st.divider()


    if len(st.session_state.recommended_stocks) >1:
            str_list = data.Code.astype(str).to_list()
            target_len = 6
            padded_str_list = to_upward.pad_str(str_list, target_len)
            data.Code = padded_str_list


            tmp=to_upward.get_close(data,st.session_state.recommended_stocks,start,end)
            before_data = to_upward.get_close(data,st.session_state.recommended_stocks,start_03,end_03)
            kospi200_2016 = yfinance.download('^KS200',start = dt.datetime(2016,1,1))["Close"]
            kospi200 = kospi200_2016[kospi200_2016.index>=start_03]
            now_data = to_upward.get_close(data,st.session_state.recommended_stocks,start,end) # tmp와 동일
            kospi200 = stock.get_index_ohlcv_by_date(start_03, end, "1028")['종가']
            daily_ret = tmp[st.session_state.recommended_stocks].pct_change()
            annual_ret = (1+daily_ret.mean())**tmp[st.session_state.recommended_stocks].shape[0]-1
            daily_cov = daily_ret.cov()
            annual_cov = daily_cov * tmp[st.session_state.recommended_stocks].shape[0]

            tmp2 = pd.DataFrame((annual_ret-0.02)/daily_ret.std()*np.sqrt(252),columns= ['sharpe']).sort_values(by='sharpe',ascending=False)

            if len(st.session_state.recommended_stocks) >=5:
                stocks = list(tmp2.iloc[0:5].index)
            elif len(st.session_state.recommended_stocks) <5:
                stocks= list(tmp2.iloc[0:].index)

            daily_ret = tmp[stocks].pct_change()
            annual_ret = (1+daily_ret.mean())**tmp[stocks].shape[0]-1
            daily_cov = daily_ret.cov()
            annual_cov = daily_cov * tmp[stocks].shape[0]

            
            if sum(annual_ret<0) == len(annual_ret<0):
                st.warning(f'연평균 수익률이 모두 음수인 업체이므로, 포트폴리오를 구성하기에 바람직하지 않습니다. 새롭게 sector를 선택해주세요.')

            else:
                col1, col2= st.columns(2)
                with col1:
                    tmp2
                with col2:
                    st.markdown(f"""
                        <span style='font-size: 16px;'>
                        <div style="color: #151617">
                            <strong>상관계수 상위 기업과 선택한 기준:<br>
                                {'<br>'.join(stocks)}
                        </div>
                        """, unsafe_allow_html=True)
                st.divider()

                col3, col4= st.columns(2)
                max_sharpe,min_risk,tmp2,df=to_upward.get_portfolio(stocks,annual_ret,annual_cov)
                with col3:
                    to_upward.show_CAPM(df, tmp2, max_sharpe, min_risk, rf=0.0325)
                with col4:
                    st.write('최대 샤프 비율')
                    st.dataframe(max_sharpe)
                    st.write('최소 리스크 비율')
                    st.dataframe(min_risk)

                min_value= (f"{4:.2f}")
                min_value= float(min_value)
                max_value= (f"{200:.2f}")
                max_value= float(max_value)
                max_return= (f"{100*max_sharpe['Returns'].iloc[0]:.2f}")
                max_return = float(max_return)
                
                
                exp_ret = st.slider("기대수익을 선택해주세요.", min_value, max_value, step=0.1,key="slider_sharpe") /100
                col5, col6= st.columns(2)
                with col5:
                    st.markdown(f'''위험 기피: :green[**기대수익 {min_value}% 이상 {max_return}% 미만입니다.**]''')
                    st.markdown(f'''중립: :orange[**기대수익 {max_return}% 입니다.**]''')
                    st.markdown(f'''위험 선호: :red[**기대수익 {max_return}% 초과 {max_value}% 이하입니다.**]''')

                with col6:
                    if exp_ret*100 >= min_value and exp_ret*100 < max_return:
                        st.image(f'Data analysis/위험기피.png', caption='당신은 수익형(위험기피형)입니다.', use_column_width=True)
                    elif exp_ret*100 == max_return:
                        st.image(f'Data analysis/중립.png', caption='당신은 수익형(중립형)입니다.', use_column_width=True)
                    elif exp_ret*100 > max_return and exp_ret*100 <= max_value:
                        st.image(f'Data analysis/위험선호.png', caption='당신은 수익형(위험선호형)입니다', use_column_width=True)


                st.divider()

                fig, solution= to_upward.show_portfolio(max_sharpe,exp_ret)
                st.plotly_chart(fig)
                st.success("위 그래프를 다운로드하려면, 그래프 우측 상단의 Download plot as a png 버튼을 클릭하세요.")
                st.divider()
                
                if exp_ret is not None:
                    tab1, tab2= st.tabs(['미래','과거'])

                    with tab1:
                        st.text(f'''
                        몬테카를로 시뮬레이션은 불확실한 상황에서 수치적 예측을 수행하는 데 사용되는 통계적 방법입니다.
                        이를 활용해 위의 포트폴리오로 투자했을 때 얼마의 수익을 얻을 수 있는 지, 
                        시뮬레이션 결과로 얻은 누적 수익률 분포를 분석하여, 다음의 백분위 수를 계산합니다. \n
                        호황장 (10% 백분위): 시뮬레이션 결과 중 최상위 10%에 해당하는 수익률 (최적 시나리오)
                        상승장 (25% 백분위): 시뮬레이션 결과 중 상위 25%에 해당하는 수익률 
                        평년 (50% 백분위): 시뮬레이션 결과의 중간값 (평균적 시나리오) 
                        하락장 (75% 백분위): 시뮬레이션 결과 중 하위 25%에 해당하는 수익률
                        불황장 (90% 백분위): 시뮬레이션 결과 중 하위 10%에 해당하는 수익률 (최악 시나리오) \n
                        몬테카를로 시뮬레이션을 사용하여 5달간의 포트폴리오 수익률을 예측합니다.
                        1000번의 시뮬레이션을 통해 다양한 시나리오(호황장, 상승장, 평년, 하락장, 불황장)의 수익률을 예측합니다.
                        시뮬레이션 결과를 실제 값과 비교하여, 포트폴리오 전략의 효과성을 평가합니다.
                        ''')

                        sim_num=1000
                        balance = 1000000
                        stock_money= max_sharpe[max_sharpe.columns[3:]]*balance
                        balance_df= to_upward.monte_sim(sim_num,tmp,stocks,stock_money)
                        
                        sim_data=to_upward.get_simret(balance_df,balance,before_data,stocks,max_sharpe,solution,None,None,rf=0.0325)
                        col7, col8= st.columns(2)
                        with col7:
                            st.write(sim_data)
                        with col8:                 
                            tmp4 = {'호황': [round((sim_data['호황'][4]/100)*balance)],
                                    '상승': [round((sim_data['상승'][4]/100)*balance)],
                                    '평년': [round((sim_data['평년'][4]/100)*balance)],
                                    '하락': [round((sim_data['하락'][4]/100)*balance)],
                                    '불황': [round((sim_data['불황'][4]/100)*balance)]}

                            df4 = pd.DataFrame(tmp4)
                            df4 = df4.applymap('{:,}'.format)
                            df4.index = ['수익(투자금:100만원)']
                            st.table(df4.T)

                        st.write(px.line(sim_data))
                        st.success("위 그래프를 다운로드하려면, 그래프 우측 상단의 Download plot as a png 버튼을 클릭하세요.")
                    
                        p_data =kospi200_2016.reset_index()
                        p_data.columns = ['ds','y']
                        m_prophet = Prophet(changepoint_range=1,)
                        m_prophet.fit(p_data)
                        np.random.seed(42)
                        future = m_prophet.make_future_dataframe(periods=0)
                        forecast = m_prophet.predict(future)
                        fig2 = m_prophet.plot(forecast)
                        a = add_changepoints_to_plot(fig2.gca(), m_prophet, forecast)
                        tmp3=pd.DataFrame()
                        tmp3['Date'] = fig2.gca().lines[2].get_xdata()
                        tmp3['Trend'] = fig2.gca().lines[2].get_ydata()

                        st.markdown(f"""
                                    아래 차트는 추세와 변곡 지점에 대한 차트입니다. 붉은 선은 추세, 붉은 점선은 변곡점을 나타냅니다.
                                    """)
                        st.pyplot(fig2)

                        now_trend_line = tmp3[tmp3['Date'] >= fig2.gca().lines[-1].get_xdata()[0]].reset_index(drop=True)
                        slope, intercept = np.polyfit(now_trend_line.index,now_trend_line['Trend'],1)
                        if (int((dt.datetime.now()- fig2.gca().lines[-1].get_xdata()[0]).days)>100) & (int((dt.datetime.now()- fig2.gca().lines[-1].get_xdata()[0]).days)<130):
                            if slope > 0:
                                st.markdown(f"현재 추세의 기울기는 {slope:0.4f}로 [상승추세]입니다.")
                            else:
                                st.markdown(f"현재 추세의 기울기는 {slope:0.4f}로 [하락추세]입니다.")
                        
                            st.markdown("변곡지점부터 100이상 지났습니다. 변곡지점이 가까우니 투자유의하시기바랍니다.")
                            st.markdown(f"""과거 기록을 기준으로 보았을 때, 추세의 변곡점은 주로 추세시작일 기준 100일,200일 부근에서 발생했습니다. 참고하여 투자하시기 바랍니다.""")
                        
                        elif (int((dt.datetime.now()- fig2.gca().lines[-1].get_xdata()[0]).days)>200) & (int((dt.datetime.now()- fig2.gca().lines[-1].get_xdata()[0]).days)<230):
                            if slope > 0:
                                st.markdown(f"현재 추세의 기울기는 {slope:0.4f}로 [상승추세]입니다.")
                            else:
                                st.markdown(f"현재 추세의 기울기는 {slope:0.4f}로 [하락추세]입니다.")
                            st.markdown("변곡지점부터 200일이상 지났습니다. 변곡지점이 가까우니 투자유의하시기바랍니다.")
                            st.markdown(f"""과거 기록을 기준으로 보았을 때, 추세의 변곡점은 주로 추세시작일 기준 100일,200일 부근에서 발생했습니다.\n참고하여 투자하시기 바랍니다.""")


                    with tab2:
                        st.text(f'''
                        몬테카를로 시뮬레이션은 불확실한 상황에서 수치적 예측을 수행하는 데 사용되는 통계적 방법입니다.
                        이를 활용해 위의 포트폴리오로 투자했을 때 얼마의 수익을 얻을 수 있는 지, 
                        시뮬레이션 결과로 얻은 누적 수익률 분포를 분석하여, 다음의 백분위 수를 계산합니다. \n
                        호황장 (10% 백분위): 시뮬레이션 결과 중 최상위 10%에 해당하는 수익률 (최적 시나리오)
                        상승장 (25% 백분위): 시뮬레이션 결과 중 상위 25%에 해당하는 수익률 
                        평년 (50% 백분위): 시뮬레이션 결과의 중간값 (평균적 시나리오) 
                        하락장 (75% 백분위): 시뮬레이션 결과 중 하위 25%에 해당하는 수익률
                        불황장 (90% 백분위): 시뮬레이션 결과 중 하위 10%에 해당하는 수익률 (최악 시나리오) \n
                        몬테카를로 시뮬레이션을 사용하여 5달간의 포트폴리오 수익률을 예측합니다.
                        1000번의 시뮬레이션을 통해 다양한 시나리오(호황장, 상승장, 평년, 하락장, 불황장)의 수익률을 예측합니다.
                        시뮬레이션 결과를 실제 값과 비교하여, 포트폴리오 전략의 효과성을 평가합니다.
                        ''')
                        daily_ret = before_data[st.session_state.recommended_stocks].pct_change()
                        annual_ret = (1+daily_ret.mean())**before_data[st.session_state.recommended_stocks].shape[0]-1
                        daily_cov = daily_ret.cov()
                        annual_cov = daily_cov * before_data[st.session_state.recommended_stocks].shape[0]
                        tmp2 = pd.DataFrame((annual_ret-0.02)/daily_ret.std()*np.sqrt(252),columns= ['sharpe']).sort_values(by='sharpe',ascending=False)
                        if len(st.session_state.recommended_stocks) >=5:
                            stocks = list(tmp2.iloc[0:5].index)
                        elif len(st.session_state.recommended_stocks) <5:
                            stocks= list(tmp2.iloc[0:].index)
                        daily_ret = before_data[stocks].pct_change()
                        annual_ret = (1+daily_ret.mean())**before_data[stocks].shape[0]-1
                        daily_cov = daily_ret.cov()
                        annual_cov = daily_cov * before_data[stocks].shape[0]
                        rf = 0.0325
                        max_sharpe,min_risk,tmp2,df = to_upward.get_portfolio(stocks,annual_ret,annual_cov)
                        sim_num=1000
                        balance = 1000000
                        stock_money= max_sharpe[max_sharpe.columns[3:]]*balance
                        balance_df= to_upward.monte_sim(sim_num,tmp,stocks,stock_money)
                        sim_data=to_upward.get_simret(balance_df,balance,before_data,stocks,max_sharpe,solution,now_data,kospi200,rf=0.0325)
                        col9, col10= st.columns(2)
                        with col9:
                            st.write(sim_data)
                        with col10:
                            tmp4 = {'호황': [round((sim_data['호황'][4]/100)*balance)],
                                    '상승': [round((sim_data['상승'][4]/100)*balance)],
                                    '평년': [round((sim_data['평년'][4]/100)*balance)],
                                    '하락': [round((sim_data['하락'][4]/100)*balance)],
                                    '불황': [round((sim_data['불황'][4]/100)*balance)]}

                            df4 = pd.DataFrame(tmp4)
                            df4 = df4.applymap('{:,}'.format)
                            df4.index = ['수익(투자금:100만원)']
                            st.table(df4.T)

                        st.write(px.line(sim_data))
                        st.success("위 그래프를 다운로드하려면, 그래프 우측 상단의 Download plot as a png 버튼을 클릭하세요.")

                        st.markdown(f"""
                                    아래 차트는 추세와 변곡 지점에 대한 차트입니다. 붉은 선은 추세, 붉은 점선은 변곡점을 나타냅니다.
                                    """)
                        st.pyplot(fig2)
                        before_trend_line = tmp3[tmp3['Date']>=before_data.index[-1]][:100].reset_index(drop=True)
                        slope, intercept = np.polyfit(before_trend_line.index,before_trend_line['Trend'],1)
                        if slope > 0:
                            st.markdown(f"과거 시뮬레이션 당시의 [상승추세] 기울기는 {slope:0.4}였습니다. 향후 투자에 참고하십시오.")
                        else:
                            st.markdown(f"과거 시뮬레이션 당시의 [하락추세] 기울기는 {slope:0.4}였습니다. 향후 투자에 참고하십시오.")


    else:
        st.warning("추천 주식의 개수가 1개 이하이므로, 포트폴리오를 구성하기에 바람직하지 않습니다. 새롭게 sector를 선택해주세요.")
        
except Exception as e:
    pass




    
        




