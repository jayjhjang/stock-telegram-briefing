import os
import requests
import yfinance as yf
from openai import OpenAI
from datetime import datetime

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

client = OpenAI(api_key=OPENAI_API_KEY)

TICKERS = ["IONQ", "NVDA", "TSLA", "QQQ", "SOXX"]

def get_stock_summary(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")

    if hist.empty:
        return f"{ticker}: 데이터 없음"

    last = hist.iloc[-1]
    prev = hist.iloc[-2]

    price = last["Close"]
    change = price - prev["Close"]
    pct = change / prev["Close"] * 100

    volume = int(last["Volume"])

    return f"{ticker}: ${price:.2f} ({pct:+.2f}%), 거래량 {volume:,}주"

def make_briefing():
    market_data = "\n".join(
        get_stock_summary(t)
        for t in TICKERS
    )

    prompt = f"""
너는 미국주식 전문 애널리스트다.

아래 데이터를 바탕으로 한국어 데일리 브리핑을 작성해라.

{market_data}

형식:

[미국장 데일리 브리핑]

■ 시장 요약
■ IonQ 분석
■ NVDA 분석
■ 오늘 체크할 가격대
■ 리스크
■ 한줄 결론
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text[:4000]
        }
    )

if __name__ == "__main__":
    briefing = make_briefing()
    send_telegram(briefing)
