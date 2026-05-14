from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
import math
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_floats(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, list):
        return [clean_floats(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_floats(v) for k, v in obj.items()}
    return obj

def fetch_df(ticker: str, period: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if df.empty:
        raise HTTPException(status_code=404, detail="Ticker not found")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    return df


@app.get("/stock/{ticker}")
def get_stock(ticker: str, period: str = "6mo"):
    try:
        df = fetch_df(ticker, period)
        records = df[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")
        return clean_floats({"ticker": ticker.upper(), "data": records})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/indicators/{ticker}")
def get_indicators(ticker: str, period: str = "6mo"):
    try:
        df = fetch_df(ticker, period)
        close = df["Close"].astype(float)

        rsi = ta.momentum.RSIIndicator(close, window=14).rsi().round(2).tolist()
        macd_obj = ta.trend.MACD(close)
        macd = macd_obj.macd().round(4).tolist()
        macd_signal = macd_obj.macd_signal().round(4).tolist()
        bb = ta.volatility.BollingerBands(close, window=20)
        bb_upper = bb.bollinger_hband().round(2).tolist()
        bb_lower = bb.bollinger_lband().round(2).tolist()

        return clean_floats({
            "dates": df["Date"].tolist(),
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "close": close.round(2).tolist(),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analyze/{ticker}")
def analyze(ticker: str):
    try:
        df = fetch_df(ticker, "3mo")
        close = df["Close"].astype(float)

        rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
        macd_obj = ta.trend.MACD(close)
        macd_line = macd_obj.macd()
        signal_line = macd_obj.macd_signal()
        bb = ta.volatility.BollingerBands(close, window=20)

        latest_close = round(close.iloc[-1], 2)
        latest_rsi = round(rsi.dropna().iloc[-1], 2)
        latest_macd = round(macd_line.dropna().iloc[-1], 4)
        latest_signal = round(signal_line.dropna().iloc[-1], 4)
        latest_bb_upper = round(bb.bollinger_hband().iloc[-1], 2)
        latest_bb_lower = round(bb.bollinger_lband().iloc[-1], 2)
        price_change = round(((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100, 2)

        prompt = f"""
You are a stock market analyst. Analyze the following technical indicators for {ticker.upper()} and give a concise summary.

Current Data:
- Price: ${latest_close}
- 3-month price change: {price_change}%
- RSI (14): {latest_rsi} — above 70 is overbought, below 30 is oversold
- MACD: {latest_macd}, Signal: {latest_signal} — if MACD > Signal it is bullish
- Bollinger Bands: Upper ${latest_bb_upper}, Lower ${latest_bb_lower} — price near upper band means overbought, near lower means oversold

Write a 3-4 sentence analysis covering:
1. Overall signal (bullish, bearish, or neutral)
2. What the RSI suggests
3. What the MACD suggests
4. One sentence conclusion with a caution that this is not financial advice

Keep it simple and clear for a retail investor.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return {"ticker": ticker.upper(), "analysis": response.text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))