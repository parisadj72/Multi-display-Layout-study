"""Figures for behavioral / overlooked analysis (numpy + matplotlib only; tables as list[dict])."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .io_tables import col_float, missing


def _mpl():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def plot_metric_boxplot_by_group(
    trials: List[Dict[str, Any]],
    output_path: Path,
    group_col: str,
    value_col: str,
    title: str,
    ylabel: str,
    dpi: int = 200,
) -> None:
    """Boxplot of a numeric trial column by group (skips non-finite values)."""
    plt = _mpl()
    if not trials or not any(group_col in t and value_col in t for t in trials):
        return
    _ensure_dir(output_path.parent)
    groups: Dict[str, List[float]] = {}
    for t in trials:
        g = t.get(group_col)
        v = t.get(value_col)
        if missing(g) or str(g) == "nan":
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if np.isnan(fv):
            continue
        gs = str(g)
        groups.setdefault(gs, []).append(fv)
    labels = sorted(groups.keys(), key=str)
    if not labels:
        return
    data = [np.array(groups[g], dtype=float) for g in labels]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot(data, labels=labels, showfliers=True)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(group_col.replace("_", " "))
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_reengagement_vs_overlook_sample_count(
    trials: List[Dict[str, Any]],
    output_path: Path,
    title: str,
    dpi: int = 200,
    max_points: int = 2500,
) -> None:
    """Scatter: intermediate view count vs re-engagement time (trials with both finite)."""
    plt = _mpl()
    if not trials:
        return
    _ensure_dir(output_path.parent)
    xs: List[float] = []
    ys: List[float] = []
    for t in trials:
        try:
            nx = float(t.get("overlooked_view_sample_count", np.nan))
            ny = float(t.get("reengagement_after_overlook_sec", np.nan))
        except (TypeError, ValueError):
            continue
        if np.isnan(nx) or np.isnan(ny):
            continue
        if nx <= 0:
            continue
        xs.append(nx)
        ys.append(ny)
    if len(xs) > max_points:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(xs), size=max_points, replace=False)
        xs = [xs[i] for i in idx]
        ys = [ys[i] for i in idx]
    if not xs:
        return
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(xs, ys, alpha=0.35, s=14)
    ax.set_xlabel("Intermediate view samples (after first target hit, before next trial)")
    ax.set_ylabel("Re-engagement time (s): selection − last intermediate view")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_ttff_by_group(
    trials: List[Dict[str, Any]],
    output_path: Path,
    group_col: str,
    title: str,
    dpi: int = 200,
) -> None:
    plt = _mpl()
    if not trials or not any(group_col in t for t in trials):
        return
    _ensure_dir(output_path.parent)
    groups: Dict[str, List[float]] = {}
    for t in trials:
        ttff = t.get("unity_ttff_sec")
        g = t.get(group_col)
        if missing(ttff) or missing(g) or str(g) == "nan":
            continue
        try:
            fv = float(ttff)
        except (TypeError, ValueError):
            continue
        gs = str(g)
        groups.setdefault(gs, []).append(fv)
    labels = sorted(groups.keys(), key=str)
    if not labels:
        return
    data = [np.array(groups[g], dtype=float) for g in labels]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot(data, labels=labels, showfliers=True)
    ax.set_ylabel("Time to first view (s), Unity log")
    ax.set_xlabel(group_col.replace("_", " "))
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_delayed_discovery_rate(
    trials: List[Dict[str, Any]],
    output_path: Path,
    group_col: str,
    title: str,
    dpi: int = 200,
) -> None:
    plt = _mpl()
    if not trials or not any("delayed_discovery_flag" in t for t in trials):
        return
    if not any(group_col in t for t in trials):
        return
    _ensure_dir(output_path.parent)
    sums: Dict[str, List[float]] = {}
    for t in trials:
        g = t.get(group_col)
        if missing(g) or str(g) == "nan":
            continue
        d = t.get("delayed_discovery_flag", 0)
        try:
            dv = float(d)
        except (TypeError, ValueError):
            dv = 0.0
        gs = str(g)
        sums.setdefault(gs, []).append(dv)
    labels = sorted(sums.keys(), key=str)
    if not labels:
        return
    rates = [float(np.mean(sums[g])) for g in labels]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(range(len(labels)), rates, color="steelblue", alpha=0.85)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Proportion of trials (delayed discovery)")
    ax.set_ylim(0, 1.05)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_ttff_ecdf_single_study(
    trials: List[Dict[str, Any]],
    output_path: Path,
    study_label: str,
    dpi: int = 200,
) -> None:
    """ECDF of TTFF for one study only (all participants in that study)."""
    plt = _mpl()
    if not trials:
        return
    _ensure_dir(output_path.parent)
    xs = col_float(trials, "unity_ttff_sec")
    arr = np.array([x for x in xs if not np.isnan(x)], dtype=float)
    if len(arr) == 0:
        return
    arr.sort()
    ys = np.arange(1, len(arr) + 1) / len(arr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.step(arr, ys, where="post", label=study_label)
    ax.set_xlabel("Time to first view (s)")
    ax.set_ylabel("ECDF")
    ax.set_title(f"Time-to-first-view (TTFF) — {study_label}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_ttff_ecdf_by_study(
    trials: List[Dict[str, Any]],
    output_path: Path,
    dpi: int = 200,
) -> None:
    plt = _mpl()
    if not trials:
        return
    _ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    studies = sorted(set(str(t.get("study", "")) for t in trials if not missing(t.get("study"))))
    for study in studies:
        xs = col_float([t for t in trials if str(t.get("study")) == study], "unity_ttff_sec")
        arr = np.array([x for x in xs if not np.isnan(x)], dtype=float)
        if len(arr) == 0:
            continue
        arr.sort()
        ys = np.arange(1, len(arr) + 1) / len(arr)
        ax.step(arr, ys, where="post", label=study)
    ax.set_xlabel("Time to first view (s)")
    ax.set_ylabel("ECDF")
    ax.set_title("Cumulative distribution of time-to-first-view (all parsed sessions)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_errors_by_layout_block(
    blocks: List[Dict[str, Any]],
    output_path: Path,
    dpi: int = 200,
) -> None:
    plt = _mpl()
    if not blocks:
        return
    _ensure_dir(output_path.parent)
    labels_list: List[str] = []
    totals: List[float] = []
    keys = {}
    for b in blocks:
        lab = f"{b.get('study', '')} / {b.get('layout_raw', '')}"
        e = b.get("errors_wrong_selections", 0)
        try:
            ev = float(e) if not missing(e) else 0.0
        except (TypeError, ValueError):
            ev = 0.0
        if np.isnan(ev):
            ev = 0.0
        keys[lab] = keys.get(lab, 0.0) + ev
    for lab in sorted(keys.keys()):
        labels_list.append(lab)
        totals.append(keys[lab])
    if not labels_list:
        return
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(range(len(labels_list)), totals, color="coral", alpha=0.85)
    ax.set_yticks(range(len(labels_list)))
    ax.set_yticklabels(labels_list, fontsize=8)
    ax.set_xlabel("Total wrong selections (sum over blocks)")
    ax.set_title("Search errors by study and Unity layout label")
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_errors_by_layout(
    blocks: List[Dict[str, Any]],
    output_path: Path,
    title: str,
    dpi: int = 200,
) -> None:
    """Total wrong selections summed by layout label only (one study’s blocks)."""
    plt = _mpl()
    if not blocks:
        return
    _ensure_dir(output_path.parent)
    keys: Dict[str, float] = {}
    for b in blocks:
        lab = str(b.get("layout_raw", "") or "")
        if not lab or lab == "nan":
            continue
        e = b.get("errors_wrong_selections", 0)
        try:
            ev = float(e) if not missing(e) else 0.0
        except (TypeError, ValueError):
            ev = 0.0
        if np.isnan(ev):
            ev = 0.0
        keys[lab] = keys.get(lab, 0.0) + ev
    labels_list = sorted(keys.keys(), key=str)
    if not labels_list:
        return
    totals = [keys[g] for g in labels_list]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(range(len(labels_list)), totals, color="coral", alpha=0.85)
    ax.set_yticks(range(len(labels_list)))
    ax.set_yticklabels(labels_list, fontsize=9)
    ax.set_xlabel("Total wrong selections (sum over blocks)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_process_samples_vs_ttff(
    trials: List[Dict[str, Any]],
    output_path: Path,
    dpi: int = 200,
    max_points: int = 2000,
) -> None:
    plt = _mpl()
    if not trials or not any("overlooked_view_sample_count" in t for t in trials):
        return
    _ensure_dir(output_path.parent)
    xs: List[float] = []
    ys: List[float] = []
    for t in trials:
        a = t.get("unity_ttff_sec")
        b = t.get("overlooked_view_sample_count")
        if missing(a) or missing(b):
            continue
        try:
            xs.append(float(a))
            ys.append(float(b))
        except (TypeError, ValueError):
            continue
    if len(xs) > max_points:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(xs), size=max_points, replace=False)
        xs = [xs[i] for i in idx]
        ys = [ys[i] for i in idx]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(xs, ys, alpha=0.35, s=12)
    ax.set_xlabel("Time to first view (s)")
    ax.set_ylabel("View samples before first-time milestone (overlooked log)")
    ax.set_title("Process density: Unity high-rate view samples vs TTFF")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
