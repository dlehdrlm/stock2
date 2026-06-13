import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="주가 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📈 최근 1년 주가 분석")
st.markdown("### 인텔 · LG전자 · 한화에어로스페이스")

# 야후 파이낸스 티커
TICKERS = {
    "인텔": "INTC",
    "LG전자": "066570.KS",
    "한화에어로스페이스": "012450.KS"
}


@st.cache_data(ttl=3600)
def load_stock_data():
    stock_data = {}

    for name, ticker in TICKERS.items():
        try:
            df = yf.download(
                ticker,
                period="1y",
                auto_adjust=True,
                progress=False
            )

            if len(df) > 0:
                stock_data[name] = df

        except Exception as e:
            st.warning(f"{name} 데이터 수집 실패: {e}")

    return stock_data


with st.spinner("주가 데이터를 불러오는 중..."):
    data = load_stock_data()

if len(data) == 0:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

st.success("데이터 로딩 완료!")

# -----------------------
# 정규화 그래프
# -----------------------

st.subheader("📊 최근 1년 주가 추이 비교")

fig = go.Figure()

performance = []

for company, df in data.items():

    close = df["Close"]

    normalized = close / close.iloc[0] * 100

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=normalized,
            mode="lines",
            name=company
        )
    )

    change = (
        (close.iloc[-1] - close.iloc[0])
        / close.iloc[0]
        * 100
    )

    performance.append(
        {
            "종목": company,
            "1년 수익률 (%)": round(float(change), 2)
        }
    )

fig.update_layout(
    title="초기값 100 기준 상대 성과 비교",
    xaxis_title="날짜",
    yaxis_title="상대 주가",
    hovermode="x unified",
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------
# 수익률 표
# -----------------------

st.subheader("🏆 종목별 수익률")

result_df = pd.DataFrame(performance)
result_df = result_df.sort_values(
    "1년 수익률 (%)",
    ascending=False
)

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

# -----------------------
# 막대 그래프
# -----------------------

bar_fig = go.Figure()

bar_fig.add_trace(
    go.Bar(
        x=result_df["종목"],
        y=result_df["1년 수익률 (%)"],
        text=result_df["1년 수익률 (%)"],
        textposition="outside"
    )
)

bar_fig.update_layout(
    title="최근 1년 수익률 비교",
    xaxis_title="종목",
    yaxis_title="수익률 (%)",
    height=500
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)

# -----------------------
# 투자 분석
# -----------------------

best_stock = result_df.iloc[0]

st.subheader("💡 자동 분석")

st.metric(
    label="최근 1년 최고 성과",
    value=best_stock["종목"],
    delta=f"{best_stock['1년 수익률 (%)']}%"
)

st.info(
    f"""
📌 최근 1년 동안 가장 높은 수익률을 기록한 종목은
**{best_stock['종목']}** 입니다.

그래프는 시작 가격을 100으로 맞춘 상대 비교 그래프이므로
세 종목의 성장 속도를 쉽게 비교할 수 있습니다.
"""
)
