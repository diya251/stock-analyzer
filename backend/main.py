from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_floats(obj):
    """Replace NaN/Inf with None so JSON serialization doesn't fail."""
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
    # yfinance 0.2+ returns MultiIndex columns — flatten them
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