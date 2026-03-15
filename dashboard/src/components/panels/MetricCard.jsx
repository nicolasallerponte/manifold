function Spark({ history }) {
  if (!history || history.length < 2) return null;
  const vals = history.map((h) => h.value).filter((v) => v !== undefined);
  if (vals.length < 2) return null;
  const min = Math.min(...vals), max = Math.max(...vals);
  const range = max - min || 1;
  const W = 80, H = 24;
  const pts = vals.slice(-60).map((v, i, arr) => {
    const x = (i / (arr.length - 1)) * W;
    const y = H - ((v - min) / range) * H;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg width={W} height={H}>
      <polyline points={pts} fill="none" stroke="#00ff88" strokeWidth="1" opacity="0.7" />
    </svg>
  );
}

export default function MetricCard({ label, value, good, history }) {
  const fmt = value !== undefined ? value.toFixed(5) : "——————";
  const vals = history?.map((h) => h.value).filter((v) => v !== undefined) ?? [];
  const trend = vals.length > 5 ? vals[vals.length - 1] - vals[vals.length - 5] : null;
  const isGood = trend === null ? null : (good === "high" ? trend > 0 : trend < 0);

  return (
    <div className="panel p-3 scan-line">
      <div className="text-textDim text-xs tracking-widest mb-3">{label}</div>
      <div className={`text-xl font-light tabular-nums ${value !== undefined ? "text-phosphor phosphor-glow" : "text-textDim"}`}>
        {fmt}
      </div>
      <div className="flex items-end justify-between mt-3">
        <div className="text-xs text-textDim">
          {trend !== null && (
            <span className={isGood ? "text-phosphor" : "text-red"}>
              {trend > 0 ? "+" : ""}{trend.toFixed(4)}
            </span>
          )}
          <span className="ml-2 opacity-50">{good === "high" ? "↑ better" : "↓ better"}</span>
        </div>
        <Spark history={history} />
      </div>
    </div>
  );
}