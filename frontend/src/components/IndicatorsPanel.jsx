import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

export default function IndicatorsPanel({ indicators }) {
  if (!indicators) return null;

  const { dates, rsi, macd, macd_signal, close, bb_upper, bb_lower } = indicators;

  const rsiData = dates.map((d, i) => ({ date: d.slice(5), rsi: rsi[i] }));
  const macdData = dates.map((d, i) => ({ date: d.slice(5), macd: macd[i], signal: macd_signal[i] }));
  const bbData = dates.map((d, i) => ({ date: d.slice(5), close: close[i], upper: bb_upper[i], lower: bb_lower[i] }));

  return (
    <div style={{ display: "grid", gap: "32px" }}>
      <div>
        <h3>RSI (14)</h3>
        <p style={{ fontSize: "13px", color: "#666", marginBottom: "8px" }}>
          Above 70 = overbought · Below 30 = oversold
        </p>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={rsiData}>
            <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={Math.floor(rsiData.length / 8)} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2" />
            <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 2" />
            <Line type="monotone" dataKey="rsi" dot={false} stroke="#7c3aed" strokeWidth={1.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3>MACD</h3>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={macdData}>
            <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={Math.floor(macdData.length / 8)} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line type="monotone" dataKey="macd" dot={false} stroke="#2563eb" strokeWidth={1.5} />
            <Line type="monotone" dataKey="signal" dot={false} stroke="#f97316" strokeWidth={1.5} strokeDasharray="4 2" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3>Bollinger Bands</h3>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={bbData}>
            <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={Math.floor(bbData.length / 8)} />
            <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line type="monotone" dataKey="upper" dot={false} stroke="#94a3b8" strokeWidth={1} />
            <Line type="monotone" dataKey="close" dot={false} stroke="#0ea5e9" strokeWidth={1.5} />
            <Line type="monotone" dataKey="lower" dot={false} stroke="#94a3b8" strokeWidth={1} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}