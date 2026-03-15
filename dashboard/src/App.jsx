import { useState, useEffect, useRef } from "react";
import MetricCard from "./components/panels/MetricCard";
import MetricChart from "./components/panels/MetricChart";
import UMAPPanel from "./components/panels/UMAPPanel";
import AlarmPanel from "./components/panels/AlarmPanel";
import StatusBar from "./components/StatusBar";

const WS_URL = "ws://127.0.0.1:7331/ws";
const MAX_HISTORY = 200;

const METRIC_META = {
  uniformity:     { label: "UNIFORMITY",  good: "low"  },
  alignment:      { label: "ALIGNMENT",   good: "low"  },
  isotropy:       { label: "ISOTROPY",    good: "high" },
  effective_rank: { label: "EFF. RANK",   good: "high" },
};

export default function App() {
  const [connected, setConnected] = useState(false);
  const [history, setHistory] = useState([]);
  const [latest, setLatest] = useState(null);
  const [alarms, setAlarms] = useState([]);
  const [umapPoints, setUmapPoints] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      ws.onopen = () => setConnected(true);
      ws.onclose = () => { setConnected(false); setTimeout(connect, 2000); };
      ws.onmessage = (e) => {
        const { step, metrics } = JSON.parse(e.data);
        const { umap_points, ...rest } = metrics;
        const point = { step, ...rest };
        setLatest(point);
        setHistory((prev) => [...prev.slice(-MAX_HISTORY), point]);
        if (umap_points) setUmapPoints(umap_points);
        checkAlarms(step, rest);
      };
    }
    connect();
    return () => wsRef.current?.close();
  }, []);

  function checkAlarms(step, metrics) {
    const triggered = [];
    if (metrics.isotropy !== undefined && metrics.isotropy < 0.02)
      triggered.push({ step, type: "danger", msg: "ISOTROPY < 0.02 // dimensional collapse detected" });
    if (metrics.effective_rank !== undefined && metrics.effective_rank < 5)
      triggered.push({ step, type: "danger", msg: "EFF_RANK < 5 // severe representation collapse" });
    if (metrics.uniformity !== undefined && metrics.uniformity > -0.5)
      triggered.push({ step, type: "warn", msg: "UNIFORMITY > -0.5 // embeddings clustering" });
    if (triggered.length > 0)
      setAlarms((prev) => [...triggered, ...prev].slice(0, 50));
  }

  const cur = latest ?? {};
  const deadDims = cur.dead_dimensions ?? { count: 0, ratio: 0 };
  const spread = cur.angular_spread ?? { mean: 0, std: 0 };

  return (
    <div className="min-h-screen bg-bg grid-bg font-mono text-text">
      <StatusBar connected={connected} step={latest?.step} />
      <main className="p-3 space-y-3">

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {Object.entries(METRIC_META).map(([key, meta]) => (
            <MetricCard
              key={key}
              label={meta.label}
              value={cur[key]}
              good={meta.good}
              history={history.map((h) => ({ step: h.step, value: h[key] }))}
            />
          ))}
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="panel p-4">
            <div className="text-textDim text-xs mb-2 tracking-widest">DEAD_DIMS</div>
            <div className="text-4xl font-light text-red" style={{ textShadow: "0 0 12px rgba(255,51,51,0.5)" }}>
              {deadDims.count}
            </div>
            <div className="text-textDim text-xs mt-2">{(deadDims.ratio * 100).toFixed(1)}% of D</div>
          </div>
          <div className="panel p-4">
            <div className="text-textDim text-xs mb-2 tracking-widest">ANGULAR_SPREAD</div>
            <div className="text-4xl font-light text-phosphor phosphor-glow">
              {spread.mean.toFixed(3)}
            </div>
            <div className="text-textDim text-xs mt-2">σ {spread.std.toFixed(3)}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
          <div className="lg:col-span-2 space-y-2">
            <MetricChart
              history={history}
              metrics={["uniformity", "isotropy"]}
              colors={["#00ff88", "#4488ff"]}
            />
            <MetricChart
              history={history}
              metrics={["effective_rank"]}
              colors={["#ffaa00"]}
            />
            <AlarmPanel alarms={alarms} />
          </div>
          <UMAPPanel embeddings={umapPoints} />
        </div>

      </main>
    </div>
  );
}