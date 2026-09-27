"""Ranking metrics shared by all notebooks (BAF and AML). Higher score = more suspicious."""
import numpy as np
from sklearn.metrics import average_precision_score, roc_curve


def pr_auc(y, s):
    return float(average_precision_score(y, s))


def recall_at_fpr(y, s, fpr_target=0.05):
    """Best recall (TPR) reachable while FPR <= fpr_target.
    With few negatives the FPR grid is coarse (step = 1/n_neg); meaningful on full splits."""
    fpr, tpr, _ = roc_curve(y, s)
    return float(tpr[fpr <= fpr_target].max())


def threshold_at_fpr(y, s, fpr_target=0.05):
    """Score cut-off that flags fpr_target of the negatives.
    Use on VALIDATION to pick an operating threshold; apply unchanged on test."""
    return float(np.quantile(np.asarray(s)[np.asarray(y) == 0], 1 - fpr_target))


def precision_at_k(y, s, k=100):
    top = np.argsort(-np.asarray(s), kind="stable")[:k]
    return float(np.asarray(y)[top].mean())


def lift_at_frac(y, s, frac=0.01):
    k = max(1, int(len(y) * frac))
    return precision_at_k(y, s, k) / float(np.mean(y))


def summary(y, s, ks=(100, 500)):
    out = {"prevalence": float(np.mean(y)), "pr_auc": pr_auc(y, s),
           "recall_at_5fpr": recall_at_fpr(y, s, 0.05), "lift_at_1pct": lift_at_frac(y, s, 0.01)}
    for k in ks:
        out[f"precision_at_{k}"] = precision_at_k(y, s, k)
    return out
