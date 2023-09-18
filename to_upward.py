import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import random
import os
from pykrx import stock
import matplotlib.pyplot as plt
import koreanize_matplotlib
import warnings
import datetime as dt
warnings.filterwarnings('ignore')
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sympy
import streamlit as st
from tqdm.auto import tqdm
from streamlit_extras.switch_page_button import switch_page
import io
import base64
import scipy.optimize as sco

@st.cache_data(ttl=900)
def pad_str(str_list, target_len):

  padded_str_list = []
  for str in str_list:
    if len(str) < target_len:
      padded_str = "0" * (target_len - len(str)) + str
    else:
      padded_str = str
    padded_str_list.append(padded_str)
  return padded_str_list

@st.cache_data(ttl=900)
def get_close(data,stocks,start,end):
    tmp = pd.DataFrame()
    for n in stocks:
        tmp[n] = stock.get_market_ohlcv(start, end, data[data['Name'] == n]['Code'])['종가']
    return tmp


@st.cache_data(ttl=900)
def stat(weights,annual_cov,annual_ret):
    returns = np.dot(weights, annual_ret)
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))
    return [risk,returns]


class Effective_frontier:
    def __init__(self,annual_cov,annual_ret):
        self.annual_cov = annual_cov
        self.annual_ret = annual_ret

    def ef(self,weight):
        return stat(weight,self.annual_cov,self.annual_ret)[0]**2
    
# def effective_frontier(weight):
#     return stat(weight,annual_cov,annual_ret)[0]**2

@st.cache_data(ttl=900)
def get_portfolio(stocks,annual_ret,annual_cov):
    port_ret = []
    port_risk = []
    port_weights = []
    sharpe_ratio = []
    np.random.seed(42)
    for i in range(5000):

        weights = np.random.random(len(stocks))
        weights /= np.sum(weights)


        returns = np.dot(weights, annual_ret)

        risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

        port_ret.append(returns)
        port_risk.append(risk)
        port_weights.append(weights)
        sharpe_ratio.append(returns/risk)

    portfolio = {'Returns' : port_ret, 'Risk' : port_risk, 'sharpe' : sharpe_ratio}
    for j, s in enumerate(stocks):
        portfolio[s] = [weight[j] for weight in port_weights]

    df = pd.DataFrame(portfolio)

    max_sharpe = df.loc[df['sharpe'] == df['sharpe'].max()]
    min_risk = df.loc[df['Risk'] == df['Risk'].min()]

    weight = np.random.random(len(stocks))
    weight = weight/np.sum(weight)
    #최적화 
    bnds = tuple((0,1) for x in range(len(stocks)))
    T_return = np.linspace(df['Returns'].min(),df['Returns'].max(),50) #수익률 구간 0~20%  
    T_vol = []           #목표 수익률별 최저분산 포트폴리오의 표준편차가 들어갈 벡터

    ef = Effective_frontier(annual_cov,annual_ret)
    for r in T_return :
        cons = ({'type' : 'eq', 'fun' : lambda x : np.sum(x) - 1},   #np.sum(x) = 비중의 총합   
                    {'type' : 'eq', 'fun' : lambda x : stat(x,annual_cov,annual_ret)[1] - r }) #Tr = 목표 수익률 
        opts = sco.minimize(ef.ef, weight, method = 'SLSQP', bounds = bnds, constraints = cons) #제한 수익률에서 분산 minimize
        T_vol.append(np.sqrt(opts['fun']))
        
        
    tmp2 = pd.DataFrame({'Returns': T_return, 'Risk':T_vol})
    return max_sharpe,min_risk,tmp2,df


def show_CAPM(df, tmp2, max_sharpe, min_risk, rf=0.0325):
    df.plot.scatter(x='Risk', y='Returns', c='sharpe', cmap='viridis', edgecolors='k', figsize=(10,8), grid=True)
    plt.plot(tmp2['Risk'], tmp2['Returns'], label='Efficient Frontier', linewidth=5,color='red')
    plt.scatter(max_sharpe['Risk'], max_sharpe['Returns'], label='Max_sharpe', marker='*',s=500)
    plt.scatter(min_risk['Risk'], min_risk['Returns'], label='Min_risk', marker='*', s=500)
    plt.plot([0, max_sharpe['Risk'].iloc[0], 0.5], [rf, max_sharpe['Returns'].iloc[0], (max_sharpe['Returns'].iloc[0] - rf) / max_sharpe['Risk'].iloc[0] * 0.5 + rf], label='New EF', linewidth=2,color='green')
    plt.xlabel('Risk')
    plt.ylabel('Expected Return')
    plt.title('Efficient Frontier Graph')
    plt.legend()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.download_button(
       label='efficient frontier graph 다운로드',
       data=buffer,
       file_name='efficient frontier graph.png',
       key='matplotlib-download-btn'
       )
    st.pyplot(plt)

def show_portfolio(max_sharpe,exp_ret):

    w = sympy.Symbol('w')

    equation = w*0.02 + (1-w)*max_sharpe['Returns'].values[0] - exp_ret

    solution = sympy.solve(equation, w)
    solution = float(solution[0])

        
    if solution >= 0:

        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],subplot_titles=("<b>포트폴리오", f"<b>기대수익을 위한 포트폴리오<br><sup>자기자본의 {solution*100:0.4}%만큼 채권투자</sup>"))

    else:
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],subplot_titles=("<b>포트폴리오", f"<b>투자금 비중</b><br><sup>자기자본의 {-solution*100:0.4}%만큼 차입</sup>"))
    if solution >= 0:
        fig.add_trace(go.Pie(
            values=list(max_sharpe.values[0][3:]),
            labels=list(max_sharpe.columns[3:]),
            domain=dict(x=[0, 0.5]),
            name="기존 포트폴리오"),
            row=1, col=1)

        fig.add_trace(go.Pie(
            values=list(max_sharpe.values[0][3:]* (1-float(solution)))+[float(solution)] ,
            labels=list(max_sharpe.columns[3:]) + ['채권'],
            domain=dict(x=[0.5, 1.0]),
            name="기대수익 포트폴리오"),
            row=1, col=2)
        
        
    else:
        fig.add_trace(go.Pie(
            values=list(max_sharpe.values[0][3:]),
            labels=list(max_sharpe.columns[3:]),
            domain=dict(x=[0, 0.5])),
            row=1, col=1)

        fig.add_trace(go.Pie(
            values=[1/(1-solution),1-(1/(1-solution))] ,
            labels=['자기자본','차입금'],
            domain=dict(x=[0.5, 1.0])),
            row=1, col=2)

    return fig, solution


def geometric_brownian_motion(tmp,S0, T=100, dt=1/100):
    """
    S0: 초기값
    mu: 평균
    sigma: 표준 편차
    T: 시뮬레이션 시간
    dt: 시간 간격
    """

    # Brownian motion
    W = np.random.normal(0, 1, (T, 1))

    daily_returns = tmp.pct_change().dropna()

    # 연간 수익률
    mean_return = daily_returns.mean()
    annual_return =((1 + mean_return) ** T) - 1

    # 변동성 계산
    mu = annual_return/T
    sigma = daily_returns.std()
    
    X = np.zeros((T, 1))
    X[0] = S0
    for t in range(1, T):
        X[t] = X[t - 1] * np.exp((mu - sigma ** 2 / 2) * dt + sigma * W[t])

    return X



def monte_sim(sim_num,tmp,stocks,stock_money,day=100):
    sim_num = sim_num
    balance_df = pd.DataFrame(np.zeros((sim_num,day)))
    for i in range(len(stocks)):
        X = []
        for k in range(sim_num):
            X.append(geometric_brownian_motion(tmp[stocks[i]],stock_money[stocks[i]].iloc[0]))
        balance_df += pd.DataFrame(np.array(X).reshape(sim_num,day))
    return balance_df.T


def get_simret(balance_df,balance,before_data,stocks,max_sharpe,solution,now_data=None,kospi200=None,rf=0.0325):
    port_weigth = max_sharpe[max_sharpe.columns[3:]].values
    tmp3 = pd.DataFrame()
    for i in [0.9,0.75,0.5,0.25,0.1]:
        lst = []
        idx = balance_df.T[balance_df.iloc[-1] >= balance_df.iloc[-1].quantile(i)][99].sort_values().index[0]
        for k in range(19,100,20):
            lst.append((balance_df.T.iloc[idx].iloc[k]-balance)/balance*100)
        tmp3[f'{100-i*100}%'] = lst

    tmp3.index=[f"{i}month" for i in range(1,6)]
    tmp3.columns =['호황','상승','평년','하락','불황']
    if now_data is not None:
        future_data = now_data[(now_data.index >before_data.index.max())&(now_data.index < dt.datetime(2023,8,2))]
        future_data = future_data[stocks].groupby(future_data.index.to_period('M')).first()
        future_data = (future_data/future_data.iloc[0]-1).drop(index=future_data.index[0])
        tmp3['real'] = ((future_data*port_weigth).sum(axis=1)*100).to_list()
    tmp3 = tmp3*(1-solution) + rf * solution*100
    if kospi200 is not None:
        f_kospi =kospi200[(kospi200.index >before_data.index.max())&(kospi200.index < dt.datetime(2023,8,2))]
        f_kospi = f_kospi.groupby(f_kospi.index.to_period('M')).first()
        f_kospi = (f_kospi/f_kospi.iloc[0]-1).drop(index=f_kospi.index[0])
        tmp3['KOSPI'] = (f_kospi*100).to_list()
    # 받아주는 인수가 많아짐. 
    return tmp3