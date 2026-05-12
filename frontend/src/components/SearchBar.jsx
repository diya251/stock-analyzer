export default function SearchBar({ onSearch }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    const ticker = e.target.ticker.value.trim().toUpperCase();
    if (ticker) onSearch(ticker);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
      <input
        name="ticker"
        placeholder="Enter ticker (e.g. AAPL)"
        style={{ flex: 1, padding: "8px 12px", fontSize: "15px", borderRadius: "8px", border: "1px solid #ccc" }}
      />
      <button type="submit" style={{ padding: "8px 20px", borderRadius: "8px", cursor: "pointer" }}>
        Search
      </button>
    </form>
  );
}