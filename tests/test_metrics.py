import torch
from manifold.core.metrics import compute_all, uniformity, isotropy, dead_dimensions
import pytest

def test_uniformity_range():
    z = torch.randn(64, 128)
    score = uniformity(z)
    assert isinstance(score, float)


def test_isotropy_collapsed():
    z = torch.ones(64, 128)
    score = isotropy(z)
    assert score == pytest.approx(0.0, abs=1e-6)


def test_dead_dimensions():
    z = torch.randn(64, 128)
    z[:, :32] = 0.0  # 32 dimensiones muertas
    result = dead_dimensions(z)
    assert result["count"] == 32


def test_compute_all_no_positives():
    z = torch.randn(64, 128)
    metrics = compute_all(z)
    assert "uniformity" in metrics
    assert "effective_rank" in metrics
    assert "isotropy" in metrics
    assert "dead_dimensions" in metrics
    assert "angular_spread" in metrics


def test_compute_all_with_positives():
    z = torch.randn(64, 128)
    p = torch.randn(64, 128)
    metrics = compute_all(z, positives=p)
    assert "alignment" in metrics