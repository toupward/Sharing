import streamlit as st
from streamlit_chat import message
from bardapi import Bard
import os
import requests
from streamlit_extras.colored_header import colored_header
import pandas as pd
import to_upward

from pages import Sharpe
from pages import Correlation
from pages import Stock_Chatbot


if "page" not in st.session_state:
    st.session_state.page = "home"



DATA_PATH = "/"

# 데이터 불러오는 함수(캐싱)
@st.cache_data(ttl=900)  # 캐싱 데코레이터
def load_csv(path):
    return pd.read_csv(path)

# 데이터 불러오기
data = load_csv(f"{DATA_PATH}labeled_data_final2.csv")

str_list = data.Code.astype(str).to_list()
target_len = 6
padded_str_list = to_upward.pad_str(str_list, target_len)

data.Code = padded_str_list

info = ['목표주가','recommendationKey','추정EPS','추정PER','동종업계ROE','동종업계enterpriseToEbitda','동종업계dividendYield','동종업계trailingEps','동종업계trailingPE']
volitality = ['Name','volitality','marketCap','fiftyDayAverage','twoHundredDayAverage','52WeekChange','ytdReturn','fiveYearAverageReturn','beta']
performance = ['Name','performance','totalRevenue','grossProfits','revenuePerShare','ebitdaMargins','EBITDAPS']
finance = ['Name','finance','debtToEquity','operatingCashflow','freeCashflow','totalCashPerShare','currentRatio','quickRatio','totalCash','totalDebt','BPS']
business = ['Name','business','returnOnAssets','returnOnEquity','grossMargins','operatingMargins','profitMargins']
value = ["Name",'동종업계trailingPE','동종업계enterpriseToEbitda','동종업계trailingEps','value','priceToBook','enterpriseValue','enterpriseToRevenue','enterpriseToEbitda','trailingEps','priceToSalesTrailing12Months','trailingPE']
dividend = ['Name','dividend','dividendYield','dividendRate','5년평균dividendYield']
growth = ['Name','revenueGrowth','earningsGrowth','earningsQuarterlyGrowth','revenueQuarterlyGrowth','heldPercentInsiders','목표주가','recommendationKey','growth']


value_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[동종업계 대비 PER를 기준으로 등급을 매김
	A+(class5) : 상위 99% 이상 (샘플수 1개)
	A(class6) : 상위 97~ 99%
	B(class1) : 상위 87~95
	C(class4)
	D(class2)
	E(class0) : 하위 4~14%
	F(class3) : 하위 4% 미만
]

data설명:[Name : 기업명
동종업계trailingPE : 동종업계trailingPE
동종업계enterpriseToEbitda : 동종업계enterpriseToEbitda
동종업계trailingEps : 동종업계trailingEps
value : class에 따른 등급
priceToBook : priceToBook
enterpriseValue : enterpriseValue
enterpriseToRevenue : enterpriseToRevenue
enterpriseToEbitda : enterpriseToEbitda
trailingEps : trailingEps
priceToSalesTrailing12Months :priceToSalesTrailing12Months
trailingPE : trailingPE]

data:[Name : LG에너지솔루션
동종업계trailingPE : 9.59
동종업계enterpriseToEbitda : 5.49
동종업계trailingEps : 27936.99
value : A
priceToBook : 5.44
enterpriseValue : 135256086675456.0
enterpriseToRevenue : 4.508
enterpriseToEbitda : 34.66
trailingEps : 3306
priceToSalesTrailing12Months : 4.440976
trailingPE : 167.27]

contents:[LG에너지솔루션, 동종업계 대비 높은 PER로 투자매력 돋보여.
LG에너지솔루션은 2023년 6월 30일 기준으로 동종업계 대비 높은 PER(주가수익비율)을 기록하며 투자매력을 돋보이고 있다.
LG에너지솔루션의 동종업계 대비 PER은 167.27으로, 이는 동종업계 평균 PER인 9.59의 17.6배에 달한다. 이는 LG에너지솔루션이 글로벌 전기차 배터리 시장에서 경쟁력을 갖추고 있으며, 향후 성장세가 기대된다는 것을 의미한다.
LG에너지솔루션은 2022년 기준으로 세계 전기차 배터리 시장 점유율 2위(23.5%)를 차지하고 있다. 또한, 중국 CATL(24%)에 이어 세계 2위의 생산능력을 보유하고 있다.
LG에너지솔루션은 최근 미국, 유럽 등 글로벌 시장에서 주요 완성차 업체들과 배터리 공급 계약을 체결하며 성장세를 이어가고 있다. 또한, 차세대 전기차 배터리 개발에도 적극 투자하고 있다.
이러한 성장세를 감안할 때, LG에너지솔루션의 높은 PER은 투자매력을 높이는 요인으로 작용할 것으로 전망된다.
다만, 고성장 기업의 경우 실적 변동에 따른 리스크가 존재한다는 점은 유의해야 한다.
LG에너지솔루션은 최근 원자재 가격 상승과 중국 정부의 전기차 보조금 축소 등 악재가 발생하며 주가가 하락한 바 있다. 향후 이러한 악재가 지속될 경우 기업의 실적과 주가에 부정적인 영향을 미칠 수 있다.

따라서 LG에너지솔루션에 투자하기 위해서는 기업의 실적과 재무 상황을 면밀히 분석하고, 투자 위험을 충분히 고려해야 한다.
]

data:[Name : SK하이닉스
동종업계trailingPE : 9.59
동종업계enterpriseToEbitda : 5.49
동종업계trailingEps : 27936.99
value : B
priceToBook : 0.83
enterpriseValue : 106149797953536.0
enterpriseToRevenue : 2.827
enterpriseToEbitda : 3.48
trailingEps : 3242
priceToSalesTrailing12Months : 2.2426567
trailingPE : 36.55]

contents:[SK하이닉스, 동종업계 대비 적절한 PER로 투자 매력 유지.
SK하이닉스는 2023년 6월 30일 기준으로 동종업계 대비 적절한 PER(주가수익비율)을 기록하며 투자 매력을 유지하고 있다.
SK하이닉스의 동종업계 대비 PER은 36.55로, 이는 동종업계 평균 PER인 9.59의 3.8배에 달한다. 이는 SK하이닉스가 글로벌 반도체 시장에서 경쟁력을 갖추고 있으며, 안정적인 실적을 거두고 있다는 것을 의미한다.
SK하이닉스는 2022년 기준으로 세계 D램 시장 점유율 1위(43.3%)를 차지하고 있다. 또한, 세계 낸드 플래시 시장 점유율 2위(17.3%)를 차지하고 있다.
SK하이닉스는 최근 미국, 중국 등 글로벌 시장에서 주요 반도체 고객사들과 공급 계약을 체결하며 성장세를 이어가고 있다. 또한, 차세대 반도체 개발에도 적극 투자하고 있다.
이러한 성장세와 안정적인 실적을 감안할 때, SK하이닉스의 적절한 PER은 투자 매력을 높이는 요인으로 작용할 것으로 전망된다.
다만, 경기 침체 우려와 원자재 가격 상승 등 악재가 지속될 경우 기업의 실적에 부정적인 영향을 미칠 수 있다는 점은 유의해야 한다.

따라서 SK하이닉스에 투자하기 위해서는 기업의 실적과 재무 상황을 면밀히 분석하고, 투자 위험을 충분히 고려해야 한다.
]
"""
volitality_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[
	A+(class1) : 모든 지표에서 압도적인 금양
	A(class3) : 1년평균수익률이 상위권이며, 5년 평균수익률이 상위 94% 이상인 그룹. 장기수익률이 우수한 그룹
	B(class2) : 52weekchange가 크며, 1년 평균수익률이 class3과 비슷하거나 조금 높지만, 5년평균수익률이 class3대비 많이 떨어지는 그룹. 즉, 단기 수익률은 좋지만 장기수익률은 좋지못한그룹.
	C(class5) : 0 class 중 5년 평균수익률이 평균 이상인 그룹
	D(class0) : 모든 면에서 중간수준의 그룹. 1년 평균수익률이 class2와 비슷하거나 부족하며, 5년 평균수익률이 class2보다 낮은 그룹.
	E(class4) : 1년 수익률 면에서 class2보다 다소 떨어지며, 5년 평균수익률은 하위 42%로 class0과 class2 대비해서 장기수익률이 좋지 못한 그룹
]

data설명:[Name : 기업명
volitality : class에 따른 등급
marketCap : marketCap
fiftyDayAverage : 50일 평균가격
twoHundredDayAverage : 200일 평균가격
52WeekChange : 52WeekChange
ytdReturn : ytdReturn
fiveYearAverageReturn : fiveYearAverageReturn
beta : beta]

data:[Name : 삼성전자
volitality : C
marketCap : 452548859265024.0
fiftyDayAverage : 71160.0
twoHundredDayAverage : 64285.0
52WeekChange : 15.025042999999998
ytdReturn : 24.59
fiveYearAverageReturn : 16.247999999999998
beta : 0.95]

contents:[삼성전자

삼성전자는 5년 평균 수익률이 16.24%로 5년 평균 수익률이 평균 이상인 그룹(Class5)에 속한다. 이는 삼성전자가 최근 5년 동안 안정적인 성장을 이어오고 있음을 나타낸다.
삼성전자의 52주간 수익률은 15.02%로, 단기 수익률도 우수한 편이다. 또한, 시가총액은 452조 원대로, 국내 상장 기업 중 가장 크다.
삼성전자는 글로벌 반도체 시장에서 독보적인 위치를 차지하고 있으며, 최근에는 인공지능(AI), 5G, 사물인터넷(IoT) 등 신성장 분야에서도 두각을 나타내고 있다. 이러한 성장 잠재력은 삼성전자의 장기적인 수익 창출력을 뒷받침할 것으로 기대된다.
다만, 삼성전자의 주가는 최근 상승세를 보이고 있어 단기적인 조정 가능성도 있다. 또한, 글로벌 경기 침체 우려가 커지고 있어 투자에 신중을 기할 필요가 있다.

종합 평가
삼성전자는 안정적인 성장과 성장 잠재력을 갖춘 기업으로, 장기적인 투자 관점에서 매력적인 종목으로 평가된다.]

data:[Name : SK하이닉스
동종업계trailingPE : 9.59
동종업계enterpriseToEbitda : 5.49
동종업계trailingEps : 27936.99
value : B
priceToBook : 0.83
enterpriseValue : 106149797953536.0
enterpriseToRevenue : 2.827
enterpriseToEbitda : 3.48
trailingEps : 3242
priceToSalesTrailing12Months : 2.2426567
trailingPE : 36.55]

contents:[SK하이닉스

SK하이닉스는 5년 평균 수익률이 19.69%로 5년 평균 수익률이 가장 높은 그룹(Class1)에 속한다. 이는 SK하이닉스가 최근 5년 동안 매우 우수한 성장을 이어오고 있음을 나타낸다.
SK하이닉스의 52주간 수익률은 40.58%로, 단기 수익률도 매우 우수한 편이다. 또한, 시가총액은 106조 원대로, 국내 상장 기업 중 4번째로 크다.
SK하이닉스는 글로벌 반도체 시장에서 삼성전자에 이어 2위의 점유율을 차지하고 있다. 또한, 최근에는 메모리 반도체 뿐만 아니라 낸드 플래시 반도체, 파운드리 사업 등에서도 두각을 나타내고 있다. 이러한 성장 잠재력은 SK하이닉스의 장기적인 수익 창출력을 뒷받침할 것으로 기대된다.
다만, SK하이닉스의 주가는 최근 상승세를 보이고 있어 단기적인 조정 가능성도 있다. 또한, 글로벌 경기 침체 우려가 커지고 있어 투자에 신중을 기할 필요가 있다.

종합 평가
SK하이닉스는 우수한 성장성과 성장 잠재력을 갖춘 기업으로, 장기적인 투자 관점에서 매우 매력적인 종목으로 평가된다.

추가 분석
SK하이닉스의 현재 주가는 동종업계 대비 할인된 수준이다. 이는 SK하이닉스의 성장 잠재력이 동종업계 평균보다 높다는 것을 의미한다. 또한, SK하이닉스의 PER은 36.55로 동종업계 평균(9.59)보다 높은 수준이다. 이는 SK하이닉스의 성장성에 대한 시장의 기대가 높다는 것을 의미한다.
따라서, SK하이닉스는 단기적인 조정 가능성을 감안하더라도, 장기적인 투자 관점에서 매우 매력적인 종목으로 평가된다.
]
"""
performance_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[
	A+(class1) : 삼성전자. Performance부분에서 세계적인 수준의 기업으로 국내에 동일한 그룹으로 묶일 기업이 없음.
	A(class3) : grossprofit 백분위 91%이상 그룹의 평균치는 백분위 96%그룹. A클래스에는 미치지 못하지만, 대부분의 영역에서 우수한 그룹
	B(class4) : 주당매출이 백분위89%, 그 외 EBITDA Margin이 A클래스보다 낮은 편이며, 전반적인 수치가 A클래스 대비 낮지만, 평균이상인 그룹
	C(class5) : 태광산업. 주당매출이 백분위89%, 그 외 EBITDA Margin이 A클래스보다 낮은 편이며, EBITA나 총이익이 다소 불량한 기업
	D(class0) : 주당매출, 총이익, EBITDA Margin 등 전반의 지표가 불량한 기업.
	F(class2) : 한국전력. 총이익이 백분위 1%미만, 그 외 매출, EBITDA 등 전반의 지표에 대해서 최하위인 기업.
]

data설명:[Name : 기업명
performance : class에 따른 등급
totalRevenue : totalRevenue
grossProfits : grossProfits
revenuePerShare : revenuePerShare
ebitdaMargins : ebitdaMargins
EBITDAPS : EBITDAPS]

data:[Name : SK하이닉스
performance : A
totalRevenue : 446216.0
grossProfits : 68094.0
revenuePerShare : 54607.414
ebitdaMargins : 0.38006002
EBITDAPS : 28792.0]

contents:[SK하이닉스, 메모리 반도체 시장의 선두주자

SK하이닉스는 대한민국의 메모리 반도체 설계, 제조 기업으로, 종합 세계 2위의 RAM과 낸드플래시 제조 기업이다. 2023년 기준, SK하이닉스의 Performance 등급은 A로, gross profit 백분위 91% 이상 그룹의 평균치는 백분위 96% 그룹에 해당한다.
SK하이닉스의 total revenue는 2023년 기준 446216억 원, gross profits는 68094억 원, revenue per share는 54607.414원, ebitda margins는 0.38006002, EBITDAPS는 28792원이다.
이러한 수치를 바탕으로 볼 때, SK하이닉스는 메모리 반도체 시장에서 세계적인 수준의 기업으로 평가할 수 있다. 특히, gross profits는 91% 이상의 백분위를 기록하여, 메모리 반도체 시장에서 뛰어난 수익성을 보이고 있음을 알 수 있다. 또한, revenue per share와 ebitda margins도 각각 54607.414원과 0.38006002로, 우수한 실적을 기록하고 있다.
SK하이닉스는 최근 차량용 메모리 솔루션 개발 품질 국제 인증을 획득하는 등, 차세대 메모리 시장 공략에 박차를 가하고 있다. 또한, 청주에 M15X 신규 공장을 건설하는 등, 생산능력 확대에도 적극적으로 나서고 있다.
이러한 노력을 바탕으로, SK하이닉스는 메모리 반도체 시장의 선두주자로서, 더욱 성장하고 발전해 나갈 것으로 기대된다.]

data:[Name : 삼성전자
performance : A+
totalRevenue : 3022314.0
grossProfits : 433766.0
revenuePerShare : 39878.17
ebitdaMargins : 0.19594999
EBITDAPS : 12143.0]

contents:[삼성전자, 글로벌 IT 리더십 강화

삼성전자는 대한민국을 대표하는 글로벌 IT 기업으로, 스마트폰, 반도체, 디스플레이, 가전 등 다양한 분야에서 세계적인 경쟁력을 갖추고 있다. 2023년 기준, 삼성전자의 Performance 등급은 A+로, 국내에 동일한 그룹으로 묶일 기업이 없다.
삼성전자의 total revenue는 2023년 기준 3022314억 원, gross profits는 433766억 원, revenue per share는 39878.17원, ebitda margins는 0.19594999, EBITDAPS는 12143원이다.
이러한 수치를 바탕으로 볼 때, 삼성전자는 글로벌 IT 산업을 선도하는 기업으로 평가할 수 있다. 특히, gross profits는 99.9% 이상의 백분위를 기록하여, 글로벌 IT 산업에서 압도적인 수익성을 보이고 있음을 알 수 있다. 또한, revenue per share와 ebitda margins도 각각 39878.17원과 0.19594999로, 세계 최고 수준의 실적을 기록하고 있다.
삼성전자는 최근 갤럭시 S23 시리즈를 출시하는 등, 스마트폰 시장에서 경쟁력을 강화하고 있다. 또한, 메모리 반도체 시장에서 세계 1위를 유지하고 있으며, 디스플레이 시장에서도 프리미엄 제품을 중심으로 경쟁력을 확대하고 있다. 가전 부문에서도 비스포크 가전을 통해 소비자 선택권을 확대하고 있다.
이러한 노력을 바탕으로, 삼성전자는 글로벌 IT 산업을 선도하는 기업으로서, 더욱 성장하고 발전해 나갈 것으로 기대된다.]
"""
finance_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[
	A+(class2) : 당좌비율,유동비율 모두 상위 1% 수준, 현금흐름이 음수이지만 부채상환 여력이 충분하고, 빠르게 현금화가 가능한 당좌비율이 매우 크기에 가장 높은 그룹으로 선정함.
	A(class6) : 당좌비율,유동비율이 모두 상위 1%이나 당좌비율이 A+보다는 낮은 그룹.
	B(class1) : 당좌비율 상위 11%이상 유동비율 상위 7% 이상이며 현금흐름도 평균이상인 그룹.
	C(class4) : B와 비슷한 당좌비율, 유동비율을 가졌지만, 현금흐름이 평균이하(48%이하)인 그룹
	D(class3): B,C와 유사한 비율을 가졌지만, 현금흐름이 하위인 그룹. 상환여력은 충분하지만, 상황이 악화되고 있는 그룹
	E(class5): 유동비율 상위 11%이상, 당좌비율 상위 31~6%
	F(class8): 유동비율 상위 11%이하, 당좌비율 상위 31%이상
	G(class0): 당좌비율 46~69%이며, E,F그룹보다 유동비율이 낮은 그룹
	H(class7): 당좌비율 46%이하,I클래스보다는 양호한 유동비율, 현금흐름 등을 가진 그룹.
	I(class9): 유동비율 백분위 10% 미만, 유동비율 백분위 6%미만, 현금흐름 백분위 3% 이하. 유동비율,당좌비율 모두 1이하, 현금흐름이 음수인 그룹으로, 현재 상환능력도 부족하며, 현금흐름도 좋지 못한 그룹. 위기가 발생하면 부도가능성이 높음.
]

data설명:[Name : 기업명
finance : class에 따른 등급
debtToEquity : debtToEquity
operatingCashflow : operatingCashflow
freeCashflow : freeCashflow
totalCashPerShare : totalCashPerShare
currentRatio : currentRatio
quickRatio : quickRatio
totalCash : totalCash
totalDebt : totalDebt
BPS : BPS]

data:[Name : 카카오
finance : G
debtToEquity : 69.6990075303542
operatingCashflow : 6784.0
freeCashflow : -4505.0
totalCashPerShare : 10867.605982833396
currentRatio : 1.453
quickRatio : 1.368
totalCash : 48359.0
totalDebt : 94316.0
BPS : 22893]

contents:[
카카오 재무분석

카카오는 2023년 6월 기준으로 재무상태 등급 G를 받았습니다. 이는 당좌비율이 46~69%이며, 유동비율이 11% 이상이지만 E, F 그룹보다 낮은 그룹에 해당합니다.
구체적으로 살펴보면, 카카오의 당좌비율은 1.453으로 2022년 말 1.368에서 소폭 상승했습니다. 유동비율은 1.368로 2022년 말과 동일합니다. 부채비율은 69.699%로 2022년 말 68.57%에서 소폭 상승했습니다.
카카오의 재무상태는 전체적으로 양호한 편이지만, 부채비율이 다소 높다는 점은 우려할 만합니다. 부채비율이 높을수록 회사가 적자를 기록하거나 자금이 부족해질 경우 부채 상환에 어려움을 겪을 수 있습니다.
카카오는 최근 몇 년간 공격적인 투자를 통해 핀테크, 콘텐츠, 커머스 등 다양한 분야로 사업을 확장해왔습니다. 이러한 투자는 긍정적인 측면이 있지만, 재무 부담으로 이어질 수 있다는 점은 유의해야 합니다.
카카오가 재무건전성을 강화하기 위해서는 부채비율을 낮추기 위한 노력이 필요합니다. 이를 위해 유휴자산을 처분하거나 자본금을 증액하는 등의 방법을 검토할 수 있습니다. 또한, 수익성 개선을 통해 부채 상환 능력을 강화하는 것도 중요합니다.
카카오는 국내 대표적인 IT 기업으로서 향후 성장 가능성이 높은 기업입니다. 다만, 재무건전성을 꾸준히 관리해 나간다면 더욱 안정적인 성장을 이어갈 수 있을 것으로 기대됩니다.]

data:[Name : 하이브
finance : F
debtToEquity : 66.3024550141701
operatingCashflow : 3471.0
freeCashflow : 406295281664.0
totalCashPerShare : 12763.781210158202
currentRatio : 3.202
quickRatio : 2.997
totalCash : 5316.0
totalDebt : 19418.0
BPS : 66995]

contents:[

하이브 재무분석

하이브는 2023년 6월 기준으로 재무상태 등급 F를 받았습니다. 이는 유동비율 상위 11% 이상, 당좌비율 상위 31 이상 그룹에 해당합니다.
구체적으로 살펴보면, 하이브의 당좌비율은 3.202로 2022년 말 3.134에서 소폭 상승했습니다. 유동비율은 2.997로 2022년 말과 동일합니다. 부채비율은 66.302%로 2022년 말 68.57%에서 소폭 하락했습니다.
하이브의 재무상태는 전체적으로 양호한 편입니다. 당좌비율과 유동비율이 모두 높아서 단기적인 지급 능력이 충분합니다. 또한, 현금흐름이 매우 양호하여 부채 상환 능력도 우수합니다.
다만, 부채비율이 다소 높은 편이라는 점은 우려할 만합니다. 부채비율이 높을수록 회사가 적자를 기록하거나 자금이 부족해질 경우 부채 상환에 어려움을 겪을 수 있습니다.
하이브는 최근 몇 년간 BTS의 인기에 힘입어 빠르게 성장해왔습니다. 이러한 성장 과정에서 많은 자금을 투자해왔기 때문에 부채비율이 높아졌습니다. 하이브가 재무건전성을 강화하기 위해서는 부채비율을 낮추기 위한 노력이 필요합니다. 이를 위해 유휴자산을 처분하거나 자본금을 증액하는 등의 방법을 검토할 수 있습니다.
하이브는 K-POP 대표 기업으로서 향후 성장 가능성이 높은 기업입니다. 다만, 재무건전성을 꾸준히 관리해 나간다면 더욱 안정적인 성장을 이어갈 수 있을 것으로 기대됩니다.]
"""
business_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[
	A(class1) : 영업이익률 상위 83% 이상 순이익률도 높은 편
	B(class3) : class0 중 순이익률이 그룹 내 평균이상인 그룹
	C(class0) : 영업이익 17%이하 순이익률 1.3%이상인 그룹
	D(class2) : 그 외 영업이익 및 순이익률이 저조한 그룹
]

data설명:[Name : 기업명
business : class에 따른 등급
returnOnAssets : returnOnAssets
returnOnEquity : returnOnEquity
grossMargins : grossMargins
operatingMargins : operatingMargins
profitMargins : profitMargins]

data:[Name : 삼성SDI
business : B
returnOnAssets : 7.27
returnOnEquity : 12.52
grossMargins : 0.20143
operatingMargins : 0.08685
profitMargins : 0.09495]

contents:[삼성SDI, 업계 최고 ROE로 주주 이익 극대화

삼성SDI는 2022년 기준 자기자본 수익률(ROE) 12.52%를 기록하며, 업계 최고 수준을 달성했다. 이는 전년 대비 1.2%p 상승한 수치다. 삼성SDI의 ROE는 업계 평균인 7.27%를 크게 웃돌며, 국내 기업 중에서도 상위권에 속한다.
삼성SDI의 높은 ROE는 견고한 사업구조와 경쟁력 있는 제품 포트폴리오에 기인한다. 삼성SDI는 전기차 배터리, 디스플레이, 전자재료 등 다양한 분야에서 경쟁력을 갖추고 있다. 특히 전기차 배터리 분야에서는 세계 1위 기업으로 자리매김하고 있으며, 디스플레이 분야에서도 OLED 시장에서 독보적인 지위를 차지하고 있다.
삼성SDI는 이러한 견고한 사업구조를 기반으로 향후 성장세를 이어갈 것으로 기대된다. 특히 전기차 배터리 시장의 성장세가 지속되면서 삼성SDI의 ROE는 더욱 상승할 것으로 예상된다.
한편, 삼성SDI는 ROE가 높은 기업을 의미하는 class B에 속한다. class B에 속하는 기업은 영업이익률이 17% 이하이면서 순이익률이 1.3% 이상인 기업으로, 삼성SDI는 순이익률이 9.495%로 그룹 내 평균 이상을 기록하고 있다.
이러한 분석을 통해 삼성SDI는 높은 ROE를 바탕으로 주주 이익을 극대화하고 있으며, 향후 성장세도 기대된다는 것을 알 수 있다.]

data:[Name : SK하이닉스
business : C
returnOnAssets : 2.24
returnOnEquity : 3.56
grossMargins : 0.22850999
operatingMargins : 0.01446
profitMargins : -0.06215]

contents:[SK하이닉스, 영업이익률 저조로 투자 매력↓

SK하이닉스는 2022년 기준 영업이익률 1.3%를 기록하며, 업계 평균인 6.7%를 크게 밑돌았다. 이는 전년 대비 1.2%p 하락한 수치다. SK하이닉스의 영업이익률은 국내 기업 중에서도 하위권에 속하며, class C에 속한다.
class C는 영업이익률이 17% 이하이면서 순이익률이 1.3% 이상인 기업을 의미한다. SK하이닉스는 순이익률 0.64%로 그룹 내 평균 이상을 기록하고 있지만, 영업이익률이 저조해 투자 매력이 낮은 것으로 평가된다.
SK하이닉스의 저조한 영업이익률은 메모리 반도체 시장의 수요 감소와 가격 하락으로 인한 것으로 분석된다. 지난해 하반기부터 지속되고 있는 전세계적인 IT제품 수요감소에 따른 재고 축적과 메모리 가격 하락 여파로 SK하이닉스는 2분기 연속 영업적자를 기록하기도 했다.
SK하이닉스는 올해도 메모리 반도체 시장의 부진이 지속될 것으로 예상됨에 따라 영업이익률 개선이 어려울 것으로 전망된다. 또한, SK하이닉스는 지속적인 시설투자와 연구개발 비용 확대에 따른 비용 증가로 영업이익률 개선에 어려움을 겪을 것으로 예상된다.
이러한 분석을 통해 SK하이닉스는 저조한 영업이익률로 인해 투자 매력이 낮아질 것으로 예상된다.]
"""
dividend_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[
	A (class2) : 최상위 배당주, 5년 평균 배당률이 5.41% 이상 (백분위 약 94% 초과)
	B (class4) : 상위 배당주, 5.41이하3.674 이상 (백분위 약 81-94%)
	C (class0) : 보통 배당주, 3.674 이하 (백분위 약 57-81%)
	D (class3) : 하위 배당주, 2.261 이하 (백분위 32-57%)
	E (class1) : 최하위배당주,0.982 이하 (백분위 약 32% 이하)
]

data설명:[Name : 기업명
dividend : class에 따른 등급
dividendYield : 1년 평균배당수익률
dividendRate : 주방배당금
5년평균dividendYield : 5년 평균배당수익률]

data:[Name : 포스코퓨처엠
dividend : E
dividendYield : 0.07
dividendRate : 300
5년평균dividendYield : 0.408]

contents:[포스코퓨처엠은 최하위 배당주로 분류됩니다.
1년 평균 배당수익률은 0.07%로, 이는 5년 평균 배당수익률인 0.408%에 비해 크게 낮습니다. 포스코퓨처엠은 포스코그룹의 화학소재 계열사로, 전기차 배터리, 반도체, 디스플레이 등 첨단산업 소재를 생산합니다. 최근 에너지 부문의 성장이 두드러지고 있지만, 여전히 배당 성향은 낮은 수준입니다.

포스코퓨처엠의 배당수익률이 낮은 이유는 다음과 같습니다.
성장에 대한 투자 : 포스코퓨처엠은 첨단산업 소재 시장의 성장에 대응하기 위해 지속적으로 투자를 진행하고 있습니다. 이는 단기적으로는 배당 성향에 부정적인 영향을 미칠 수 있습니다.
순이익의 감소 : 포스코퓨처엠의 순이익은 최근 몇 년간 감소하고 있습니다. 이는 원자재 가격 상승과 글로벌 경기 침체의 영향으로 분석됩니다.
포스코퓨처엠은 향후 첨단산업 소재 시장의 성장과 순이익의 개선이 이루어진다면 배당 성향을 높일 수 있을 것으로 전망됩니다.

포스코퓨처엠은 E등급으로 분류되며, 이는 5년 평균 배당률이 0.982% 미만인 기업을 의미합니다. 최하위 배당주들은 배당에 대한 관심이 낮은 투자자들에게 적합합니다.]

data:[Name : 삼성전자
dividend : C
dividendYield : 2.1
dividendRate : 1444
5년평균dividendYield : 2.87]

contents:[삼성전자

삼성전자는 보통 배당주로 분류됩니다. 1년 평균 배당수익률은 2.1%로, 이는 5년 평균 배당수익률인 2.87%에 비해 소폭 낮습니다. 삼성전자는 전자, 반도체, 디스플레이 등 다양한 사업을 영위하는 글로벌 리딩 기업입니다. 최근에는 반도체 사업의 호조로 실적이 크게 개선되고 있습니다.

삼성전자의 배당수익률이 낮은 이유는 다음과 같습니다.
성장에 대한 투자 : 삼성전자는 미래 성장을 위해 지속적으로 투자를 진행하고 있습니다. 이는 단기적으로는 배당 성향에 부정적인 영향을 미칠 수 있습니다.
배당성향의 조정 : 삼성전자는 최근 배당성향을 조정하여 주주환원 정책을 강화하고 있습니다. 이는 장기적인 관점에서 배당수익률을 높이기 위한 노력으로 볼 수 있습니다.
삼성전자는 C등급으로 분류되며, 이는 5년 평균 배당률이 3.674% 미만인 기업을 의미합니다. 보통 배당주들은 배당을 중요하게 생각하는 투자자들에게 적합합니다.]
"""
growth_str = """이건 주어진 data만을 활용해서 재무분석가로써 contents를 작성하는 task이다. 외부의 데이터를 활용해서는 안된다. 글자수는 최대 500자로 제한. 각각의 contents에서는 개별기업에 대해서만 다루어야한다.
bard는 마지막에 입력된 data에 대한 contents 부분만 출력한다. 답변 외 내용 및 수정사항, 변경사항은 출력 하지않는다.

class:[    A(class3) : 연별 성장이 큰 그룹
i.  분기 순익 성장은 부족하지만, 분기 매출성장과 순익성장률이 큼(상위84%)
ii. 분기 매출성장은 낮지만 연 순익성장이 매우큼(상위94%)
iii.    전반적으로 장기적 관점에서 성장률이 좋은 그룹
   A-(class6) : A그룹 중 연성장이 크지만 단기 손실폭이 큰 그룹
i.  분기 순익성장률이 매우 낮음(하위15%이하)
ii. 한국가스공사, 롯데웰푸드, 코스모화학
   B(class0) : 단기 성장성이 큰 그룹
i.  분기별 매출,순이익 성장이 높다 (상위 59%)
ii. 분기별 매출성장과 연 순익성장이 낮지만 분기 순이익 성장이 크다 (상위 84%)
iii.    전반적으로 순이익 성장이 높은 편이 아니지만 C(class4) 대비 순이익 성장이 높은편.
iv. 전반적으로 C,D(class2)그룹 대비 좋은 성장세를 보여줌.
   C(class4) : 전반적으로 대부분의 수치가 중위에 있는 그룹
   D(class2) : 분기 매출성장, 순익성장 모두 부실하며 순이익 성장은 하위 2%로 매우 낮은 그룹
]

data설명:[Name : 기업명
revenueGrowth: 2021년 대비 2022년 매출성장률
earningsGrowth: 2021년 대비 2022년 영업이익성장률
earningsQuarterlyGrowth: 전년동기 대비 2023년 2분기 영업이익성장률
revenueQuarterlyGrowth: 전년동기 대비 2023년 2분기 매출성장률
heldPercentInsiders: 내부자 주식보유비율
목표주가 : 전문가들이 예측한 주가
recommendationKey : 0~5사이의 값으로 5에 가까울수록 강한 매수추천
growth : 위 class 데이터 기반 등급
]

data:[Name : 포스코퓨처엠
revenueGrowth : 65.96632319678312
earningsGrowth : -8.89387144992526
earningsQuarterlyGrowth : 11.666666666666666
revenueQuarterlyGrowth : 70.80950947938611
heldPercentInsiders : 0.6372
목표주가 : 547000.0
recommendationKey : 3.9
growth : B]

contents:[포스코퓨처엠, 단기 실적 악화에도 외형 성장세 주목

포스코퓨처엠의 지난 해 매출액은 65.96% 증가, 영업이익은 -8.89% 감소했다.
반면, 2023년 2분기 기준 전년 동기대비 매출은 약 70%, 영업이익은 약 12% 증가하는 모습으로, 단기적으로 실적이 향상되고 있는 것을 알 수 있다.
포스코퓨처엠은 에너지 소재 중심으로 올해부터 오는 2025년 사이 연평균 성장률이 약 80%가 될 것으로 전망했다. 이는 100조원 이상의 양극재 수주 계약을 반영한 것이다.
포스코퓨처엠은 포스코의 2차전지 소재 사업을 담당하는 기업으로, 양극재, 음극재, 전해액, 분리막 등 다양한 소재를 생산하고 있다. 회사는 포스코의 강점인 원료 조달과 제조 기술을 바탕으로 2차전지 소재 시장에서 주도적인 역할을 하고 있다.
증권가에서는 포스코퓨처엠의 단기 실적 악화보다는 외형 성장 가능성에 주목하고 있다. 전문가들은 포스코퓨처엠의 목표주가를 54만7천원으로 예상하고 있으며, 매수추천도는 3.9로 매우 높은 편이다.

포스코퓨처엠의 성장 포인트
포스코의 강점인 원료 조달과 제조 기술을 바탕으로 한 2차전지 소재 사업의 경쟁력
에너지 소재 중심으로 연평균 80%의 성장률을 목표로 하는 외형 성장 계획
100조원 이상의 양극재 수주 계약을 통한 안정적인 매출 및 수익 창출
포스코퓨처엠은 2차전지 소재 시장의 성장세에 따라 지속적인 성장을 이어갈 것으로 전망된다.]

data:[Name : 현대모비스
revenueGrowth : 24.46897285994504
earningsGrowth : 5.278306878306879
earningsQuarterlyGrowth : 61.57389635316699
revenueQuarterlyGrowth : 29.70233989494349
heldPercentInsiders : 0.31472
목표주가 : 296500.0
recommendationKey : 4.0
growth : B]

contents:[
현대모비스, 전기차 부문 성장세 주목
현대모비스의 지난 해 매출액은 24.47% 증가, 영업이익은 5.28% 증가했다.
반면, 2023년 2분기 기준 전년 동기대비 매출은 약 30%, 영업이익은 약 62% 증가하는 모습으로, 단기적으로 실적이 크게 개선되고 있는 것을 알 수 있다.
현대모비스는 전기차 부문의 성장세가 실적 개선의 주된 원인이라고 밝혔다. 현대모비스는 전기차 부문에서 모터, 인버터, 배터리 시스템, 충전기 등 다양한 부품을 생산하고 있다. 회사는 전 세계적으로 전기차 시장이 확대됨에 따라 전기차 부문의 매출이 크게 증가할 것으로 전망하고 있다.
현대모비스의 전기차 부문 매출은 2022년 2조4,800억원을 기록했으며, 2023년에는 3조원, 2024년에는 4조원을 돌파할 것으로 예상된다. 현대모비스는 2025년까지 전기차 부문 매출을 10조원까지 확대한다는 목표를 세우고 있다.

현대모비스의 성장 포인트
전 세계적으로 확대되는 전기차 시장
현대차와 기아의 전기차 판매 확대
전기차 부문의 높은 성장세
현대모비스는 전기차 부문의 성장세를 바탕으로 지속적인 성장을 이어갈 것으로 전망된다.]
"""



str_dict = {'value':[value,value_str],
            'volitality':[volitality,volitality_str],
            'performance':[performance,performance_str],
            'finance' : [finance,finance_str],
            "business":[business,business_str],
            "dividend":[dividend,dividend_str],
            "growth":[growth,growth_str]}


API_KEY = st.sidebar.text_input(":blue[Enter Your OPENAI API-KEY :key:]", 
                placeholder="본인의 API 키를 입력해 주세요! (sk-...)",
                type="password", key= "password", help="[바드 API KEY 가져오는 방법] 크롬 방문기록 --> 인터넷 사용기록 삭제 --> 새로고침 --> bard.google.com --> F12(개발자 모드) --> 애플리케이션 --> 쿠키(bard.google.com) --> __Secure-1PSID --> 값을 복사하기 입력하기")

os.environ["_BARD_API_KEY"] = API_KEY


session = requests.Session()
session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
session.cookies.set("__Secure-1PSID", os.getenv("_BARD_API_KEY")) 




# 질문-답변 로직 구성
# 'generated'와 'past' 키 초기화
st.session_state.setdefault('generated', [{'type': 'normal', 'data': "어떤 주식에 투자하려고 하시나요?"}])
st.session_state.setdefault('past', ['주식 투자를 한번 해보고 싶은데, 어떻게 하면 될까?'])
st.session_state.setdefault('chat_stage', 1)


colored_header(
    label='Stock_Chatbot',
    description=None,
    color_name="blue-70",
)


chat_placeholder = st.empty()



def on_btn_click():
    st.session_state['past'] = ['주식 투자를 한번 해보고 싶은데, 어떻게 하면 될까?']
    st.session_state['generated'] = [{'type': 'normal', 'data': "어떤 주식에 투자하려고 하시나요?"}]
    st.session_state['chat_stage'] = 1

if 'user_input' not in st.session_state: # user_input 키 초기화
    st.session_state['user_input'] = ""

def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.past.append(user_input)
    # 사용자 입력 후, 입력 필드 초기화
    st.session_state['user_input'] = ""

    # sector_interest 키 초기화
    st.session_state.setdefault('sector_interest', '')   

    if st.session_state['chat_stage'] == 1:
        st.session_state['stock_interest'] = user_input
        if user_input not in data['Name'].values:
            st.session_state['generated'].append({"type": "normal", "data": "코스피 200 주식으로 다시 입력해주세요."})
            return
        else:
            st.session_state['generated'].append({"type": "normal", "data": "어떤 sector에 대해서 궁금하신가요?"})
            st.session_state['chat_stage'] = 2
    elif st.session_state['chat_stage'] == 2:
        st.session_state['sector_interest'] = user_input.lower()

        # 찾을 sector 입력
        input_sector = st.session_state['sector_interest']

        # 사용자가 입력한 섹터가 리스트에 없을 경우 다시 입력하게 하기
        if input_sector not in str_dict.keys():
            st.session_state['generated'].append({"type": "normal", "data": "섹터를 다시 입력해주세요."})
            return

        # sector로 feature 추출
        data2 = data[str_dict.get(f'{input_sector}')[0]]

        # 찾을 기업 입력받기
        input_str = st.session_state['stock_interest']

        idx = data2[data2['Name']==input_str].index[0] # 찾는 기업의 인덱스
        lst = []

        for k,v in data2.iloc[idx].to_dict().items():
            lst.append(f"{k} : {v}")
        target = '\n'.join(lst) # 타겟기업의 정보
        target_str = f"""data:[{target}]
        contents:""" # 앞의 예시와 붙이기 전의 글

        try:
            bard = Bard(token=os.environ["_BARD_API_KEY"], token_from_browser=True, session=session, timeout=30)
            response = bard.get_answer(str_dict.get(f'{input_sector}')[1]+"\n"+target_str)
            st.session_state['generated'].append({"type": "normal", "data": response['content']})
            
            # 바드 API 응답 후 "처음으로 돌아가시겠습니까?" 메시지 추가
            st.session_state['generated'].append({"type": "normal", "data": "처음으로 돌아가시겠습니까?"})
            st.session_state['past'].append(None)  # None으로 위치는 유지하면서 안 보이게
            
            st.session_state['chat_stage'] = 3  # chat_stage를 3으로 설정하여 다음 단계로 진행
        except Exception as e:
            st.error(f"API 요청 중 오류가 발생했습니다.쿠키를 초기화하고 새로운 API 키를 입력해 주세요. ")
            response = {'content': 'API 요청에 문제가 발생했습니다. 쿠키를 초기화하고 새로운 API 키를 입력해 주세요..'}

    elif st.session_state['chat_stage'] == 3:
        if user_input.lower() in ["네", "예", "yes"]:
            st.session_state['past'] = ['주식 투자를 한번 해보고 싶은데, 어떻게 하면 될까?']
            st.session_state['generated'] = [{'type': 'normal', 'data': "어떤 종목에 투자하려고 하시나요?"}]
            st.session_state['chat_stage'] = 1
        elif user_input.lower() in ["아니오", "아니요", "no"]:
            st.session_state['generated'].append({"type": "normal", "data": "챗봇을 이어서 사용하시겠습니까?"})
            st.session_state['chat_stage'] = 4

    elif st.session_state['chat_stage'] == 4:
        if user_input.lower() in ["네", "예", "yes"]:
            st.session_state['generated'].append({"type": "normal", "data": "질문을 입력해주세요."})
            st.session_state['chat_stage'] = 5
        elif user_input.lower() in ["아니오", "아니요", "no"]:
            st.session_state['generated'].append({"type": "normal", "data": "대화를 종료하겠습니다."})
            st.session_state['chat_stage'] = 6

    elif st.session_state['chat_stage'] == 5:
        try:
            bard = Bard(token=os.environ["_BARD_API_KEY"], token_from_browser=True, session=session, timeout=30)
            response = bard.get_answer(user_input)
            st.session_state['generated'].append({"type": "normal", "data": response['content']})
        except Exception as e:
            st.error(f"API 요청 중 오류가 발생했습니다.쿠키를 초기화하고 새로운 API 키를 입력해 주세요. ")
            response = {'content': 'API 요청에 문제가 발생했습니다. 쿠키를 초기화하고 새로운 API 키를 입력해 주세요..'}

with chat_placeholder.container():
    for i in range(len(st.session_state['generated'])):
        message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
        message(
            st.session_state['generated'][i]['data'],
            key=f"{i}",
            allow_html=True,
            is_table=True if st.session_state['generated'][i]['type'] == 'table' else False
        )
    
    st.button("대화 초기화", on_click=on_btn_click, key="clear_key")


with st.container():
    st.text_input("챗봇과 대화하기:", value=st.session_state['user_input'], on_change=on_input_change, key="user_input", help="대화 초기화 버튼을 누르면 초기화면으로 돌아옵니다.")


