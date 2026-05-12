import { useState } from "react";
import axios from "axios";
import SearchBar from "./components/SearchBar";
import CandlestickChart from "./components/CandlestickChart";
import IndicatorsPanel from "./components/IndicatorsPanel";

const BASE = "http://localhost:8000";

export default function App() {
  const [ticker, setTicker] = useState(null);
  const [stockData, setStockData] = useState(null);
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (symbol) => {
    setLoading(true);
    setError(null);
    try {
      const [stockRes, indRes] = await Promise.all([
        axios.get(`${BASE}/stock/${symbol}`),
        axios.get(`${BASE}/indicators/${symbol}`),
      ]);
      setTicker(symbol);
      setStockData(stockRes.data.data);
      setIndicators(indRes.data);
    } catch (e) {
      setError("Could not load data. Check the ticker and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "32px 16px", fontFamily: "sans-serif" }}>
      <h1 style={{ marginBottom: "4px" }}>Stock analyzer</h1>
      <p style={{ color: "#666", marginBottom: "24px" }}>
        Search any ticker to view price history and technical indicators
      </p>
      <SearchBar onSearch={handleSearch} />
      {loading && <p>Loading {ticker}...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && stockData && (
        <>
          <h2>{ticker}</h2>
          <CandlestickChart data={stockData} />
          <IndicatorsPanel indicators={indicators} />
        </>
      )}
    </div>
  );
}