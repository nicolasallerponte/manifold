from __future__ import annotations

import torch
import torch.nn.functional as F


def uniformity(embeddings: torch.Tensor, t: float = 2.0) -> float:
    """
    Wang & Isola (2020) uniformity loss.
    Measures how uniformly embeddings are distributed on the hypersphere.
    Lower = more uniform (better).
    """
    z = F.normalize(embeddings, dim=-1)
    sq_dists = torch.pdist(z, p=2).pow(2)
    return sq_dists.mul(-t).exp().mean().log().item()


def alignment(anchors: torch.Tensor, positives: torch.Tensor, alpha: float = 2.0) -> float:
    """
    Wang & Isola (2020) alignment loss.
    Measures average distance between positive pairs.
    Lower = better aligned (better).
    """
    a = F.normalize(anchors, dim=-1)
    p = F.normalize(positives, dim=-1)
    return (a - p).norm(dim=1).pow(alpha).mean().item()


def effective_rank(embeddings: torch.Tensor) -> float:
    """
    Roy & Vetterli (2007) effective rank.
    Measures how many dimensions are actively used.
    Higher = more spread across dimensions (better).
    """
    z = embeddings - embeddings.mean(dim=0)
    singular_values = torch.linalg.svdvals(z)
    singular_values = singular_values[singular_values > 1e-10]
    probs = singular_values / singular_values.sum()
    entropy = -(probs * probs.log()).sum()
    return entropy.exp().item()


def dead_dimensions(embeddings: torch.Tensor, threshold: float = 1e-3) -> dict:
    """
    Counts dimensions with near-zero variance across the batch.
    Returns count and indices of dead dimensions.
    """
    variances = embeddings.var(dim=0)
    dead_mask = variances < threshold
    return {
        "count": dead_mask.sum().item(),
        "ratio": (dead_mask.sum() / embeddings.shape[1]).item(),
        "indices": dead_mask.nonzero(as_tuple=True)[0].tolist(),
    }


def isotropy(embeddings: torch.Tensor) -> float:
    """
    Mu & Viswanath (2018) isotropy score.
    Ratio of minimum to maximum singular value of the embedding matrix.
    1.0 = perfectly isotropic, 0.0 = fully collapsed.
    """
    z = F.normalize(embeddings, dim=-1)
    singular_values = torch.linalg.svdvals(z)
    singular_values = singular_values[singular_values > 1e-10]
    if len(singular_values) < 2:
        return 0.0
    return (singular_values.min() / singular_values.max()).item()


def angular_spread(embeddings: torch.Tensor) -> dict:
    """
    Distribution of pairwise cosine similarities.
    Collapsed spaces have similarities clustered near 1.0.
    """
    z = F.normalize(embeddings, dim=-1)
    cosines = z @ z.T
    mask = ~torch.eye(len(z), dtype=torch.bool, device=z.device)
    cosines = cosines[mask]
    return {
        "mean": cosines.mean().item(),
        "std": cosines.std().item(),
        "max": cosines.max().item(),
        "min": cosines.min().item(),
    }


def compute_all(
    embeddings: torch.Tensor,
    positives: torch.Tensor | None = None,
) -> dict:
    """
    Computes all geometry metrics in one call.
    embeddings: (N, D) tensor
    positives:  (N, D) tensor of positive pairs (optional, for alignment)
    """
    metrics = {
        "uniformity": uniformity(embeddings),
        "effective_rank": effective_rank(embeddings),
        "isotropy": isotropy(embeddings),
        "dead_dimensions": dead_dimensions(embeddings),
        "angular_spread": angular_spread(embeddings),
    }
    if positives is not None:
        metrics["alignment"] = alignment(embeddings, positives)

    return metrics