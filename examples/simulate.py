"""
Simula un entrenamiento contrastivo con colapso progresivo.
Útil para testear el dashboard sin entrenar un modelo real.
"""
import time
import torch
import torch.nn as nn
from manifold.core.hooks import watch
from manifold.server.watcher import get_server

server = get_server()
time.sleep(1)  # espera a que arranque

encoder = nn.Sequential(nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, 128))

def on_metrics(step, metrics):
    server.emit(step, metrics)
    print(f"step {step:04d} | uniformity={metrics.get('uniformity', 0):.4f} | isotropy={metrics.get('isotropy', 0):.4f}")

hook = watch(encoder, log_every=1, on_metrics=on_metrics)

print("Simulando entrenamiento... abre http://localhost:5173")
for step in range(500):
    # simula colapso progresivo a partir del step 200
    collapse = max(0, (step - 200) / 300)
    noise = torch.randn(64, 512)
    with torch.no_grad():
        out = encoder(noise)
        # introduce colapso gradual
        if collapse > 0:
            out = out * (1 - collapse) + out.mean(dim=0) * collapse
    time.sleep(0.05)

hook.remove()
print("Done.")