import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

export default function MetricChart({ history, metrics, colors }) {
  return (
    <div className="panel p-3">
      <div className="text-textDim text-xs tracking-widest mb-3">
        {metrics.map((m, i) => (
          <span key={m} style={{ color: colors[i] }} className="mr-4">{m.toUpperCase()}</span>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={100}>
        <LineChart data={history} margin={{ top: 2, right: 0, bottom: 0, left: -28 }}>
          <XAxis dataKey="step" tick={{ fill: "#2a3040", fontSize: 9, fontFamily: "Roboto Mono" }} tickLine={false} axisLine={{ stroke: "#1a1f2e" }} />
          <YAxis tick={{ fill: "#2a3040", fontSize: 9, fontFamily: "Roboto Mono" }} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{ background: "#08090c", border: "1px solid #1a1f2e", borderRadius: 0, fontSize: 10, fontFamily: "Roboto Mono" }}
            labelStyle={{ color: "#3a4a5a" }}
            cursor={{ stroke: "#1a1f2e" }}
          />
          {metrics.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={colors[i]}
              strokeWidth={1} dot={false} isAnimationActive={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}