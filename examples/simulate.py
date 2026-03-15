"""
Simula un entrenamiento contrastivo con colapso progresivo.
"""
import time
import torch
import torch.nn as nn
from manifold.core.hooks import watch
from manifold.core.metrics import alignment as calc_alignment
from manifold.server.watcher import get_server

server = get_server()
time.sleep(1)

encoder = nn.Sequential(nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, 128))

def on_metrics(step, metrics, embeddings):
    positives = embeddings + torch.randn_like(embeddings) * 0.05
    metrics["alignment"] = calc_alignment(embeddings, positives)
    server.emit(step, metrics, embeddings=embeddings)
    print(f"step {step:04d} | uniformity={metrics.get('uniformity', 0):.4f} | isotropy={metrics.get('isotropy', 0):.4f} | alignment={metrics.get('alignment', 0):.4f}")

hook = watch(encoder, log_every=1, on_metrics=on_metrics)

print("Simulando entrenamiento... abre http://localhost:5173")
for step in range(500):
    collapse = max(0, (step - 200) / 300)
    noise = torch.randn(64, 512)
    with torch.no_grad():
        out = encoder(noise)
        if collapse > 0:
            out = out * (1 - collapse) + out.mean(dim=0) * collapse
    time.sleep(0.05)

hook.remove()
print("Done.")