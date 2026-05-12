import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function CandlestickChart({ data }) {
  if (!data || data.length === 0) return null;

  const processed = data.map((d) => ({
    date: d.Date.slice(5),
    open: d.Open,
    close: d.Close,
    high: d.High,
    low: d.Low,
    body: [Math.min(d.Open, d.Close), Math.max(d.Open, d.Close)],
    isUp: d.Close >= d.Open,
  }));

  return (
    <div style={{ marginBottom: "32px" }}>
      <h3 style={{ marginBottom: "8px" }}>Price chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={processed}>
          <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={Math.floor(processed.length / 8)} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name) => [
              Array.isArray(value)
                ? `${value[0].toFixed(2)} – ${value[1].toFixed(2)}`
                : value?.toFixed(2),
              name,
            ]}
          />
          <Bar dataKey="body" isAnimationActive={false}>
            {processed.map((d, i) => (
              <Cell key={i} fill={d.isUp ? "#22c55e" : "#ef4444"} />
            ))}
          </Bar>
          <Line dataKey="high" dot={false} stroke="#888" strokeWidth={1} />
          <Line dataKey="low" dot={false} stroke="#888" strokeWidth={1} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}