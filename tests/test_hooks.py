import torch
import torch.nn as nn
from manifold.core.hooks import watch, EmbeddingHook


def _make_encoder(in_dim=32, out_dim=64) -> nn.Module:
    return nn.Sequential(nn.Linear(in_dim, out_dim), nn.ReLU())


def test_watch_returns_hook():
    model = _make_encoder()
    hook = watch(model, log_every=1)
    assert isinstance(hook, EmbeddingHook)
    hook.remove()


def test_hook_captures_metrics():
    model = _make_encoder()
    captured = []

    hook = watch(model, log_every=1, on_metrics=lambda step, m: captured.append(m))

    x = torch.randn(64, 32)
    with torch.no_grad():
        model(x)

    hook.remove()
    assert len(captured) == 1
    assert "uniformity" in captured[0]
    assert "isotropy" in captured[0]
    assert "step" in captured[0]


def test_hook_history_accumulates():
    model = _make_encoder()
    hook = watch(model, log_every=1)

    with torch.no_grad():
        for _ in range(5):
            model(torch.randn(64, 32))

    hook.remove()
    assert len(hook.history["uniformity"]) == 5


def test_context_manager():
    model = _make_encoder()
    with watch(model, log_every=1) as hook:
        with torch.no_grad():
            model(torch.randn(64, 32))
    assert len(hook.history["uniformity"]) == 1


def test_log_every_respected():
    model = _make_encoder()
    captured = []
    hook = watch(model, log_every=10, on_metrics=lambda s, m: captured.append(m))

    with torch.no_grad():
        for _ in range(25):
            model(torch.randn(64, 32))

    hook.remove()
    assert len(captured) == 2  # steps 10 y 20