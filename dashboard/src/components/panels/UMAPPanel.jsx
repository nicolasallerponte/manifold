import { useEffect, useRef } from "react";

export default function UMAPPanel({ embeddings }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;

    ctx.clearRect(0, 0, W, H);

    // grid
    ctx.strokeStyle = "rgba(0,255,136,0.06)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 32) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += 32) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // axes
    ctx.strokeStyle = "rgba(0,255,136,0.15)";
    ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.moveTo(W / 2, 0); ctx.lineTo(W / 2, H); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke();

    if (!embeddings || embeddings.length === 0) {
      ctx.fillStyle = "rgba(0,255,136,0.2)";
      ctx.font = "11px 'Roboto Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText("NO_SIGNAL", W / 2, H / 2 - 8);
      ctx.fillText("waiting for data", W / 2, H / 2 + 8);
      return;
    }

    const xs = embeddings.map(([x]) => x);
    const ys = embeddings.map(([, y]) => y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const pad = 16;

    embeddings.forEach(([x, y]) => {
      const px = pad + ((x - minX) / (maxX - minX + 1e-8)) * (W - pad * 2);
      const py = pad + ((y - minY) / (maxY - minY + 1e-8)) * (H - pad * 2);
      ctx.beginPath();
      ctx.arc(px, py, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(0,255,136,0.7)";
      ctx.shadowBlur = 6;
      ctx.shadowColor = "#00ff88";
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }, [embeddings]);

  return (
    <div className="panel flex flex-col" style={{ minHeight: 400 }}>
      <div className="text-textDim text-xs tracking-widest p-3 pb-1">UMAP_PROJECTION</div>
      <canvas
        ref={canvasRef}
        style={{ width: "100%", flex: 1, display: "block" }}
      />
    </div>
  );
}