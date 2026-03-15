export default function StatusBar({ connected, step }) {
  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-border bg-panel">
      <div className="flex items-center gap-4">
        <span className="text-phosphor tracking-[0.3em] text-xs font-medium phosphor-glow">MANIFOLD</span>
        <span className="text-textDim text-xs">// embedding geometry debugger v0.1.0</span>
      </div>
      <div className="flex items-center gap-6 text-xs">
        {step !== undefined && (
          <span className="text-textDim">STEP:<span className="text-text ml-1">{String(step).padStart(6, "0")}</span></span>
        )}
        <div className="flex items-center gap-2">
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? "bg-phosphor" : "bg-red"}`}
            style={connected ? { boxShadow: "0 0 6px #00ff88" } : {}} />
          <span className={`tracking-widest ${connected ? "text-phosphor" : "text-red"}`}>
            {connected ? "LIVE" : "DISCONNECTED"}
          </span>
        </div>
      </div>
    </header>
  );
}