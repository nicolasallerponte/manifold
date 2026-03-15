from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable

import torch

from manifold.core.metrics import compute_all


class EmbeddingHook:
    """
    Attaches to any PyTorch module and captures embeddings
    at every forward pass, computing geometry metrics on the fly.
    """

    def __init__(
        self,
        module: torch.nn.Module,
        log_every: int = 100,
        on_metrics: Callable[[int, dict], None] | None = None,
        device: str = "cpu",
    ):
        self.module = module
        self.log_every = log_every
        self.on_metrics = on_metrics
        self.device = device

        self._step = 0
        self._history: dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        self._handle = module.register_forward_hook(self._hook_fn)

    def _hook_fn(self, module, input, output):
        self._step += 1
        if self._step % self.log_every != 0:
            return

        embeddings = self._extract_tensor(output)
        if embeddings is None:
            return

        embeddings = embeddings.detach().to(self.device).float()

        if embeddings.ndim != 2:
            return

        metrics = compute_all(embeddings)
        metrics["step"] = self._step

        with self._lock:
            for k, v in metrics.items():
                if k != "dead_dimensions" and k != "angular_spread":
                    self._history[k].append(v)

        if self.on_metrics:
            self.on_metrics(self._step, metrics)

    def _extract_tensor(self, output) -> torch.Tensor | None:
        if isinstance(output, torch.Tensor):
            return output
        if isinstance(output, (tuple, list)):
            for item in output:
                if isinstance(item, torch.Tensor) and item.ndim == 2:
                    return item
        return None

    @property
    def history(self) -> dict:
        with self._lock:
            return dict(self._history)

    def remove(self):
        self._handle.remove()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.remove()


def watch(
    module: torch.nn.Module,
    log_every: int = 100,
    on_metrics: Callable[[int, dict], None] | None = None,
) -> EmbeddingHook:
    """
    One-liner API.

        hook = watch(encoder, log_every=100)

    Returns an EmbeddingHook. Call hook.remove() when done,
    or use as a context manager.
    """
    return EmbeddingHook(module, log_every=log_every, on_metrics=on_metrics)