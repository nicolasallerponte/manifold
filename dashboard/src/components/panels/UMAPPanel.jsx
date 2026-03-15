export default function UMAPPanel({ embeddings }) {
  const hasData = embeddings && embeddings.length > 0;
  return (
    <div className="panel p-3 flex flex-col" style={{ minHeight: 220 }}>
      <div className="text-textDim text-xs tracking-widest mb-3">UMAP_PROJECTION</div>
      {hasData ? (
        <svg className="flex-1 w-full" viewBox="0 0 200 200">
          <line x1="0" y1="100" x2="200" y2="100" stroke="#1a1f2e" strokeWidth="0.5" />
          <line x1="100" y1="0" x2="100" y2="200" stroke="#1a1f2e" strokeWidth="0.5" />
          {embeddings.map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r="1.5" fill="#00ff88" opacity="0.5"
              style={{ filter: "drop-shadow(0 0 2px #00ff88)" }} />
          ))}
        </svg>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center gap-3">
          <div className="w-full h-px bg-border" />
          <div className="text-xs text-textDim tracking-widest text-center">
            NO_SIGNAL<br />
            <span className="text-phosphor opacity-30">waiting for data</span>
          </div>
          <div className="w-full h-px bg-border" />
        </div>
      )}
    </div>
  );
}