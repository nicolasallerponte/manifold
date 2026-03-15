export default function AlarmPanel({ alarms }) {
  if (!alarms.length) return null;
  return (
    <div className="panel p-3">
      <div className="text-textDim text-xs tracking-widest mb-3">ALARMS [{alarms.length}]</div>
      <div className="space-y-1 max-h-36 overflow-y-auto">
        {alarms.map((a, i) => (
          <div key={i} className={`flex items-center gap-3 text-xs py-1 px-2 border-l-2 ${
            a.type === "danger" ? "border-red text-red bg-red/5" : "border-amber text-amber bg-amber/5"
          }`}>
            <span className="text-textDim tabular-nums">{String(a.step).padStart(6, "0")}</span>
            <span>{a.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}