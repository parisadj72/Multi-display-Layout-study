"""
Readable tables and figures for inferential_stats (matplotlib + numpy).

FDR is **within** each family: (study, experiment_num, analysis_type, subset_display, subset_layout).
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import config
from .io_tables import missing, read_csv_dicts, write_csv

OUTCOME_LABELS: Dict[str, str] = {
    "time_per_selection": "Time per selection",
    "ttff": "TTFF",
    "reengagement_after_overlook": "Re-engagement (after first hit)",
    "block_error_rate": "Block error rate (wrong / N per block)",
    "overlooked_view_samples_post_first_hit": "Intermediate view samples (after first hit)",
    "delayed_binary_flag": "Delayed discovery (binary)",
    "log_process_density": "Log process density (samples / TTFF)",
}

FACTOR_LABELS: Dict[str, str] = {
    "layout": "Layout (Kruskal–Wallis)",
    "display_count_4_vs_15": "4 vs 15 displays (Mann–Whitney)",
}

OUTCOME_ORDER: Tuple[str, ...] = (
    "time_per_selection",
    "ttff",
    "reengagement_after_overlook",
    "overlooked_view_samples_post_first_hit",
    "delayed_binary_flag",
    "log_process_density",
    "block_error_rate",
)

STRATA_ORDER: Tuple[Tuple[str, int], ...] = tuple(
    (s, e) for s in ("Study1", "Study2") for e in (1, 2, 3)
)


def _fdr_key(r: Dict[str, Any]) -> Tuple[Any, ...]:
    st = str(r.get("study", ""))
    try:
        ex = int(r.get("experiment_num", -1))
    except (TypeError, ValueError):
        ex = -1
    at = str(r.get("analysis_type", "session_omnibus"))
    sdc = r.get("subset_display_count", "")
    if sdc == "" or sdc is None:
        sdc_k = ""
    else:
        try:
            sdc_k = str(int(float(sdc)))
        except (TypeError, ValueError):
            sdc_k = str(sdc)
    sl = str(r.get("subset_layout", "") or "")
    return (st, ex, at, sdc_k, sl)


def _fdr_family_label(k: Tuple[Any, ...]) -> str:
    st, ex, at, sdc, sl = k
    parts = [st, f"Exp{ex}", at]
    if sdc:
        parts.append(f"dc{sdc}")
    if sl:
        parts.append(sl[:24])
    return "_".join(parts)


def _parse_p(row: Dict[str, Any]) -> float:
    v = row.get("p_value")
    if v == "" or v is None:
        return float("nan")
    try:
        p = float(v)
    except (TypeError, ValueError):
        return float("nan")
    if math.isnan(p):
        return float("nan")
    return p


def _test_ran(row: Dict[str, Any]) -> bool:
    d = str(row.get("detail", "") or "")
    bad_prefixes = (
        "fewer_than_two_layout_groups",
        "missing_4_or_15_group",
        "scipy_not_installed",
        "scipy_required",
    )
    if d.startswith("test_failed:"):
        return False
    return not any(d.startswith(p) for p in bad_prefixes) and "scipy_not_installed" not in d


def benjamini_hochberg_fdr(p_values: Sequence[float]) -> List[float]:
    n = len(p_values)
    q_out = [float("nan")] * n
    valid_idx = [i for i, p in enumerate(p_values) if not math.isnan(p) and 0 <= p <= 1]
    m = len(valid_idx)
    if m == 0:
        return q_out
    pairs = sorted((p_values[i], i) for i in valid_idx)
    qs = [0.0] * m
    for k in range(m - 1, -1, -1):
        rank = k + 1
        p, _orig_i = pairs[k]
        q_adj = p * m / rank
        if k < m - 1:
            q_adj = min(q_adj, qs[k + 1])
        qs[k] = min(q_adj, 1.0)
    for k in range(m):
        _, orig_i = pairs[k]
        q_out[orig_i] = qs[k]
    return q_out


def add_readable_columns(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not results:
        return results

    by_fdr: Dict[Tuple[Any, ...], List[int]] = defaultdict(list)
    for i, r in enumerate(results):
        by_fdr[_fdr_key(r)].append(i)

    p_list = [_parse_p(r) for r in results]
    q_list = [float("nan")] * len(results)
    for indices in by_fdr.values():
        ps_sub = [p_list[i] for i in indices]
        q_sub = benjamini_hochberg_fdr(ps_sub)
        for j, i in enumerate(indices):
            q_list[i] = q_sub[j]

    enriched: List[Dict[str, Any]] = []
    for i, r in enumerate(results):
        rr = dict(r)
        oc = str(r.get("outcome", ""))
        fc = str(r.get("factor", ""))
        at = str(r.get("analysis_type", "session_omnibus"))
        rr["outcome_label"] = OUTCOME_LABELS.get(oc, oc)
        rr["factor_label"] = FACTOR_LABELS.get(fc, fc)
        rr["study_exp_label"] = f"{r.get('study','')}_Exp{r.get('experiment_num','')}"
        rr["fdr_family"] = _fdr_family_label(_fdr_key(r))
        p = p_list[i]
        rr["neg_log10_p"] = "" if math.isnan(p) or p <= 0 else round(-math.log10(max(p, 1e-300)), 4)
        rr["q_value_fdr_within_family"] = "" if math.isnan(q_list[i]) else float(q_list[i])
        if not math.isnan(p):
            rr["significant_uncorrected_0.05"] = "yes" if p < 0.05 else "no"
        else:
            rr["significant_uncorrected_0.05"] = ""
        qv = q_list[i]
        if not math.isnan(qv):
            rr["significant_fdr_0.05_within_family"] = "yes" if qv < 0.05 else "no"
        else:
            rr["significant_fdr_0.05_within_family"] = ""
        ran = _test_ran(r)
        rr["test_executed"] = "yes" if ran else "no"

        subset_dc = r.get("subset_display_count", "")
        subset_lay = str(r.get("subset_layout", "") or "")
        scope = ""
        if at == "layout_within_display" and subset_dc != "":
            scope = f" (only {subset_dc} displays)"
        elif at == "display_within_layout" and subset_lay:
            scope = f" (only layout {subset_lay})"

        if ran and not math.isnan(p):
            flab = rr.get("factor_label", FACTOR_LABELS.get(fc, fc))
            if p < 0.05:
                rr["interpretation_note"] = (
                    f"{rr['study_exp_label']}{scope}: {rr['outcome_label']} vs {flab} "
                    f"(p={p:.4g}; exploratory; non-independent observations)."
                )
            else:
                rr["interpretation_note"] = (
                    f"{rr['study_exp_label']}{scope}: no rank difference for {rr['outcome_label']} vs {flab} "
                    f"(p={p:.4g})."
                )
        elif not ran:
            rr["interpretation_note"] = str(r.get("detail", ""))[:220]
        else:
            rr["interpretation_note"] = ""
        enriched.append(rr)

    for rr in enriched:
        p = _parse_p(rr)
        if math.isnan(p):
            rr["significant_alpha_0.05"] = ""
        else:
            rr["significant_alpha_0.05"] = "yes" if p < 0.05 else "no"

    return enriched


def write_supplemental_tables(
    enriched: List[Dict[str, Any]], tables_dir: Path
) -> None:
    tables_dir.mkdir(parents=True, exist_ok=True)
    write_csv(tables_dir / "inferential_tests_long_enriched.csv", enriched)

    session_only = [r for r in enriched if str(r.get("analysis_type")) == "session_omnibus"]

    sig = [
        r
        for r in enriched
        if str(r.get("significant_uncorrected_0.05")) == "yes"
        and str(r.get("test_executed")) == "yes"
    ]
    write_csv(tables_dir / "inferential_tests_significant_uncorrected.csv", sig)

    sig_fdr = [
        r
        for r in enriched
        if str(r.get("significant_fdr_0.05_within_family")) == "yes"
        and str(r.get("test_executed")) == "yes"
    ]
    write_csv(tables_dir / "inferential_tests_significant_fdr_within_family.csv", sig_fdr)

    # Session-omnibus wide pivot (backward compatible)
    wide_rows: List[Dict[str, Any]] = []
    for oc in OUTCOME_ORDER:
        for fac in ("layout", "display_count_4_vs_15"):
            row: Dict[str, Any] = {
                "outcome": oc,
                "outcome_label": OUTCOME_LABELS.get(oc, oc),
                "factor": fac,
                "factor_label": FACTOR_LABELS.get(fac, fac),
            }
            for st, ex in STRATA_ORDER:
                slug = f"{st}_Exp{ex}"
                p = float("nan")
                qv = float("nan")
                for r in session_only:
                    if (
                        str(r.get("outcome")) == oc
                        and str(r.get("factor")) == fac
                        and str(r.get("study")) == st
                        and int(r.get("experiment_num", -1)) == ex
                    ):
                        p = _parse_p(r)
                        qraw = r.get("q_value_fdr_within_family")
                        try:
                            qv = float(qraw) if qraw != "" and qraw is not None else float("nan")
                        except (TypeError, ValueError):
                            qv = float("nan")
                        break
                row[f"p_{slug}"] = "" if math.isnan(p) else p
                row[f"q_fdr_{slug}"] = "" if math.isnan(qv) else qv
            wide_rows.append(row)
    write_csv(tables_dir / "inferential_pvalues_wide_session_omnibus.csv", wide_rows)

    # Stratified-only export (layout fixed DC; display fixed layout)
    strat = [r for r in enriched if str(r.get("analysis_type")) != "session_omnibus"]
    write_csv(tables_dir / "inferential_tests_stratified_enriched.csv", strat)

    summary_rows: List[Dict[str, Any]] = []
    by_st_at: Dict[Tuple[str, str], int] = defaultdict(int)
    for r in enriched:
        st = str(r.get("study", ""))
        at = str(r.get("analysis_type", ""))
        by_st_at[(st, at)] += 1
    for (st, at), n in sorted(by_st_at.items()):
        summary_rows.append({"study": st, "analysis_type": at, "n_test_rows": n})
    write_csv(tables_dir / "inferential_test_counts_by_study_and_analysis.csv", summary_rows)


def _mpl():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_inferential_figures(
    enriched: List[Dict[str, Any]],
    figures_dir: Path,
    dpi: int | None = None,
    study_filter: Optional[str] = None,
    strata_order: Optional[Tuple[Tuple[str, int], ...]] = None,
    title_suffix: str = "",
) -> List[str]:
    dpi = dpi or config.FIGURE_DPI
    figures_dir.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []

    session = [
        r
        for r in enriched
        if str(r.get("analysis_type")) == "session_omnibus"
        and (study_filter is None or str(r.get("study")) == study_filter)
    ]
    if not session:
        return errors

    order = strata_order if strata_order is not None else STRATA_ORDER
    if study_filter and strata_order is None:
        order = tuple((s, e) for s, e in STRATA_ORDER if s == study_filter)

    try:
        plt = _mpl()
    except Exception as e:  # pragma: no cover
        return [f"matplotlib: {e}"]

    def matrix_for_factor(factor: str) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
        nrow, ncol = len(OUTCOME_ORDER), len(order)
        P = np.full((nrow, ncol), np.nan, dtype=float)
        mask = np.ones((nrow, ncol), dtype=bool)
        col_labels: List[str] = [f"{s}\nExp{e}" for s, e in order]
        row_labels: List[str] = [OUTCOME_LABELS[o] for o in OUTCOME_ORDER]
        for r in session:
            if str(r.get("factor")) != factor:
                continue
            oc = str(r.get("outcome", ""))
            if oc not in OUTCOME_ORDER:
                continue
            try:
                st = str(r.get("study", ""))
                ex = int(r.get("experiment_num", -1))
            except (TypeError, ValueError):
                continue
            if (st, ex) not in order:
                continue
            i = OUTCOME_ORDER.index(oc)
            j = order.index((st, ex))
            p = _parse_p(r)
            if not math.isnan(p) and _test_ran(r):
                P[i, j] = p
                mask[i, j] = False
        return P, mask, row_labels, col_labels

    suf = title_suffix or (f" — {study_filter}" if study_filter else "")

    try:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
        vmax = 3.0
        for ax, factor, title in zip(
            axes,
            ("layout", "display_count_4_vs_15"),
            (
                f"Session omnibus: layout (K–W){suf}",
                f"Session omnibus: 4 vs 15 (M–W){suf}",
            ),
        ):
            P, mask_m, ylabs, xlabs = matrix_for_factor(factor)
            NL = np.full_like(P, np.nan, dtype=float)
            for i in range(P.shape[0]):
                for j in range(P.shape[1]):
                    if not mask_m[i, j] and P[i, j] > 0:
                        NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
            im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
            ax.set_xticks(range(len(xlabs)))
            ax.set_xticklabels(xlabs, fontsize=8)
            ax.set_yticks(range(len(ylabs)))
            ax.set_yticklabels(ylabs, fontsize=8)
            ax.set_title(title, fontsize=10)
            for i in range(NL.shape[0]):
                for j in range(NL.shape[1]):
                    if mask_m[i, j]:
                        ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=8)
                    else:
                        pv = P[i, j]
                        star = "*" if pv < 0.05 else ""
                        ax.text(
                            j,
                            i,
                            f"{pv:.3f}{star}",
                            ha="center",
                            va="center",
                            color="k" if (math.isnan(NL[i, j]) or NL[i, j] < 1.5) else "w",
                            fontsize=6,
                        )
            plt.colorbar(im, ax=ax, fraction=0.046, label="−log10(p)")
        fig.suptitle(f"Uncorrected p; * p<0.05; FDR within each family (see CSV){suf}", fontsize=10, y=1.01)
        fig.tight_layout()
        name = "inferential_pvalue_heatmaps_session.png"
        if study_filter:
            name = f"inferential_pvalue_heatmaps_session_{study_filter}.png"
        fig.savefig(figures_dir / name, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        errors.append(f"session_pvalue_heatmaps: {e}")

    try:
        hits = [
            r
            for r in enriched
            if str(r.get("significant_uncorrected_0.05")) == "yes"
            and _test_ran(r)
            and (study_filter is None or str(r.get("study")) == study_filter)
        ]
        hits.sort(key=lambda r: _parse_p(r))
        plt = _mpl()
        if hits:
            fig, ax = plt.subplots(figsize=(9, max(4, 0.32 * len(hits))))
            ylabs = []
            for r in hits:
                at = str(r.get("analysis_type", ""))[:18]
                sub = ""
                if r.get("subset_display_count"):
                    sub += f"dc{r.get('subset_display_count')} "
                if r.get("subset_layout"):
                    sub += str(r.get("subset_layout"))[:12]
                ylabs.append(
                    f"{r.get('study')}_Exp{r.get('experiment_num')} | {at}\n"
                    f"{OUTCOME_LABELS.get(str(r.get('outcome')), r.get('outcome'))} | "
                    f"{'layout' if str(r.get('factor'))=='layout' else '4v15'} {sub.strip()}"
                )
            xs = [min(-math.log10(max(_parse_p(r), 1e-300)), 4.0) for r in hits]
            ax.barh(range(len(hits)), xs, color="steelblue", alpha=0.85)
            ax.axvline(-math.log10(0.05), color="crimson", linestyle="--", label="p=0.05")
            ax.set_yticks(range(len(hits)))
            ax.set_yticklabels(ylabs, fontsize=7)
            ax.set_xlabel("−log10(p)")
            ax.set_title(f"Significant tests (uncorrected){suf}")
            ax.legend(loc="lower right")
            ax.grid(True, axis="x", alpha=0.3)
            fig.tight_layout()
            bn = "inferential_significant_uncorrected_bars.png"
            if study_filter:
                bn = f"inferential_significant_uncorrected_bars_{study_filter}.png"
            fig.savefig(figures_dir / bn, dpi=dpi, bbox_inches="tight")
            plt.close(fig)
        else:
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.text(0.5, 0.5, f"No uncorrected significant tests{suf}.", ha="center", va="center")
            ax.axis("off")
            bn = "inferential_significant_uncorrected_bars.png"
            if study_filter:
                bn = f"inferential_significant_uncorrected_bars_{study_filter}.png"
            fig.savefig(figures_dir / bn, dpi=dpi)
            plt.close(fig)
    except Exception as e:
        errors.append(f"significant_bars: {e}")

    try:
        plt = _mpl()
        fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
        for ax, factor, title in zip(
            axes,
            ("layout", "display_count_4_vs_15"),
            (
                f"FDR q — layout tests{suf}",
                f"FDR q — 4 vs 15 tests{suf}",
            ),
        ):
            nrow, ncol = len(OUTCOME_ORDER), len(order)
            Q = np.full((nrow, ncol), np.nan, dtype=float)
            mask_m = np.ones((nrow, ncol), dtype=bool)
            col_labels = [f"{s}\nExp{e}" for s, e in order]
            row_labels = [OUTCOME_LABELS[o] for o in OUTCOME_ORDER]
            for r in session:
                if str(r.get("factor")) != factor:
                    continue
                oc = str(r.get("outcome", ""))
                if oc not in OUTCOME_ORDER:
                    continue
                try:
                    st = str(r.get("study", ""))
                    ex = int(r.get("experiment_num", -1))
                    qraw = r.get("q_value_fdr_within_family")
                    qv = float(qraw) if qraw != "" and qraw is not None else float("nan")
                except (TypeError, ValueError):
                    continue
                if (st, ex) not in order:
                    continue
                if not _test_ran(r) or math.isnan(qv):
                    continue
                i = OUTCOME_ORDER.index(oc)
                j = order.index((st, ex))
                Q[i, j] = qv
                mask_m[i, j] = False
            im = ax.imshow(
                Q, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=0.5, interpolation="nearest"
            )
            ax.set_xticks(range(len(col_labels)))
            ax.set_xticklabels(col_labels, fontsize=8)
            ax.set_yticks(range(len(row_labels)))
            ax.set_yticklabels(row_labels, fontsize=8)
            ax.set_title(title, fontsize=10)
            for i in range(nrow):
                for j in range(ncol):
                    if mask_m[i, j]:
                        ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=8)
                    else:
                        qv = Q[i, j]
                        star = "*" if qv < 0.05 else ""
                        ax.text(j, i, f"{qv:.3f}{star}", ha="center", va="center", color="k", fontsize=6)
            plt.colorbar(im, ax=ax, fraction=0.046, label="FDR q")
        fig.suptitle(f"BH-FDR within each (Study×Exp×analysis family){suf}", fontsize=10, y=1.01)
        fig.tight_layout()
        fn = "inferential_fdr_q_heatmaps_session.png"
        if study_filter:
            fn = f"inferential_fdr_q_heatmaps_session_{study_filter}.png"
        fig.savefig(figures_dir / fn, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        errors.append(f"fdr_heatmaps: {e}")

    return errors


def plot_stratified_layout_within_display(
    enriched: List[Dict[str, Any]],
    figures_dir: Path,
    study: str,
    dpi: int | None = None,
) -> List[str]:
    """Heatmaps: fix display count 4 vs 15; rows=outcomes, cols=Exp1..3."""
    dpi = dpi or config.FIGURE_DPI
    errors: List[str] = []
    rows_f = [
        r
        for r in enriched
        if str(r.get("analysis_type")) == "layout_within_display"
        and str(r.get("study")) == study
        and str(r.get("factor")) == "layout"
    ]
    if not rows_f:
        return errors
    try:
        plt = _mpl()
        fig, axes = plt.subplots(1, 2, figsize=(11, 5.8))
        exp_order = (1, 2, 3)
        for ax, fixed_dc, title in zip(
            axes,
            (4, 15),
            (f"{study}: layout effect at 4 displays (K–W)", f"{study}: layout effect at 15 displays (K–W)"),
        ):
            nrow, ncol = len(OUTCOME_ORDER), len(exp_order)
            P = np.full((nrow, ncol), np.nan, dtype=float)
            mask_m = np.ones((nrow, ncol), dtype=bool)
            for r in rows_f:
                try:
                    dc = int(float(r.get("subset_display_count", -1)))
                except (TypeError, ValueError):
                    continue
                if dc != fixed_dc:
                    continue
                oc = str(r.get("outcome", ""))
                if oc not in OUTCOME_ORDER:
                    continue
                try:
                    ex = int(r.get("experiment_num", -1))
                except (TypeError, ValueError):
                    continue
                if ex not in exp_order:
                    continue
                p = _parse_p(r)
                if not _test_ran(r) or math.isnan(p):
                    continue
                i = OUTCOME_ORDER.index(oc)
                j = exp_order.index(ex)
                P[i, j] = p
                mask_m[i, j] = False
            vmax = 3.0
            NL = np.full_like(P, np.nan, dtype=float)
            for i in range(P.shape[0]):
                for j in range(P.shape[1]):
                    if not mask_m[i, j] and P[i, j] > 0:
                        NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
            im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
            ax.set_xticks(range(len(exp_order)))
            ax.set_xticklabels([f"Exp{e}" for e in exp_order], fontsize=9)
            ax.set_yticks(range(len(OUTCOME_ORDER)))
            ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOME_ORDER], fontsize=7)
            ax.set_title(title, fontsize=10)
            for i in range(nrow):
                for j in range(ncol):
                    if mask_m[i, j]:
                        ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=8)
                    else:
                        pv = P[i, j]
                        st = "*" if pv < 0.05 else ""
                        ax.text(
                            j, i, f"{pv:.3f}{st}", ha="center", va="center",
                            color="k" if NL[i, j] < 1.5 else "w", fontsize=6,
                        )
            plt.colorbar(im, ax=ax, fraction=0.046, label="−log10(p)")
        fig.suptitle(
            f"{study}: layout comparisons holding set size fixed (exploratory)",
            fontsize=11,
            y=1.02,
        )
        fig.tight_layout()
        fig.savefig(figures_dir / f"inferential_layout_within_display_{study}.png", dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        errors.append(f"layout_within_display_{study}: {e}")
    return errors


def plot_stratified_display_within_layout(
    enriched: List[Dict[str, Any]],
    figures_dir: Path,
    study: str,
    dpi: int | None = None,
) -> List[str]:
    """For each layout with tests, small multiples or one heat: cols = Exp×layout keys."""
    dpi = dpi or config.FIGURE_DPI
    errors: List[str] = []
    rows_f = [
        r
        for r in enriched
        if str(r.get("analysis_type")) == "display_within_layout"
        and str(r.get("study")) == study
        and str(r.get("factor")) == "display_count_4_vs_15"
    ]
    if not rows_f:
        return errors
    try:
        keys_sorted: List[Tuple[int, str]] = sorted(
            {
                (int(r.get("experiment_num", -1)), str(r.get("subset_layout", "")))
                for r in rows_f
                if r.get("subset_layout")
            },
            key=lambda x: (x[0], x[1]),
        )
        if not keys_sorted:
            return errors
        plt = _mpl()
        ncol = len(keys_sorted)
        nrow = len(OUTCOME_ORDER)
        P = np.full((nrow, ncol), np.nan, dtype=float)
        mask_m = np.ones((nrow, ncol), dtype=bool)
        for r in rows_f:
            oc = str(r.get("outcome", ""))
            if oc not in OUTCOME_ORDER:
                continue
            try:
                ex = int(r.get("experiment_num", -1))
            except (TypeError, ValueError):
                continue
            lay = str(r.get("subset_layout", ""))
            if not lay or (ex, lay) not in keys_sorted:
                continue
            p = _parse_p(r)
            if not _test_ran(r) or math.isnan(p):
                continue
            i = OUTCOME_ORDER.index(oc)
            j = keys_sorted.index((ex, lay))
            P[i, j] = p
            mask_m[i, j] = False
        fig, ax = plt.subplots(figsize=(max(8, ncol * 1.1), 6))
        vmax = 3.0
        NL = np.full_like(P, np.nan, dtype=float)
        for i in range(P.shape[0]):
            for j in range(P.shape[1]):
                if not mask_m[i, j] and P[i, j] > 0:
                    NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
        im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
        ax.set_xticks(range(ncol))
        ax.set_xticklabels([f"Exp{ex}\n{lay[:10]}" for ex, lay in keys_sorted], fontsize=7)
        ax.set_yticks(range(nrow))
        ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOME_ORDER], fontsize=8)
        ax.set_title(f"{study}: 4 vs 15 Mann–Whitney within each layout (exploratory)", fontsize=10)
        for i in range(nrow):
            for j in range(ncol):
                if mask_m[i, j]:
                    ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=7)
                else:
                    pv = P[i, j]
                    st = "*" if pv < 0.05 else ""
                    ax.text(
                        j, i, f"{pv:.3f}{st}", ha="center", va="center",
                        color="k" if NL[i, j] < 1.5 else "w", fontsize=6,
                    )
        plt.colorbar(im, ax=ax, fraction=0.035, label="−log10(p)")
        fig.tight_layout()
        fig.savefig(figures_dir / f"inferential_display_within_layout_{study}.png", dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        errors.append(f"display_within_layout_{study}: {e}")
    return errors


def _participant_p_valid(r: Dict[str, Any]) -> bool:
    """True if row has a usable p-value for plotting."""
    v = r.get("p_value")
    if v == "" or v is None:
        return False
    try:
        p = float(v)
    except (TypeError, ValueError):
        return False
    return not math.isnan(p) and 0.0 <= p <= 1.0


def plot_participant_level_session_heatmaps(
    tables_dir: Path,
    figures_dir: Path,
    *,
    study_filter: Optional[str] = None,
    strata_order: Optional[Tuple[Tuple[str, int], ...]] = None,
    title_suffix: str = "",
    dpi: int | None = None,
) -> List[str]:
    """
    Session omnibus heatmaps from ``inferential_participant_level_tests.csv``:
    layout (Friedman or paired Wilcoxon) vs 4 vs 15 (paired Wilcoxon).
    Mirrors trial-level session p-value heatmaps for side-by-side reporting.
    """
    dpi = dpi or config.FIGURE_DPI
    figures_dir.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    csv_path = tables_dir / "inferential_participant_level_tests.csv"
    if not csv_path.is_file():
        return errors
    rows = read_csv_dicts(csv_path)
    session = [
        r
        for r in rows
        if str(r.get("analysis_type")) == "session_omnibus"
        and str(r.get("test_level")) == "participant_median_per_cell"
        and (study_filter is None or str(r.get("study")) == study_filter)
    ]
    if not session:
        return errors

    order = strata_order if strata_order is not None else STRATA_ORDER
    if study_filter and strata_order is None:
        order = tuple((s, e) for s, e in STRATA_ORDER if s == study_filter)

    def matrix_for_factor(factor: str) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
        nrow, ncol = len(OUTCOME_ORDER), len(order)
        P = np.full((nrow, ncol), np.nan, dtype=float)
        mask = np.ones((nrow, ncol), dtype=bool)
        col_labels: List[str] = [f"{s}\nExp{e}" for s, e in order]
        row_labels: List[str] = [OUTCOME_LABELS[o] for o in OUTCOME_ORDER]
        for r in session:
            if str(r.get("factor")) != factor:
                continue
            oc = str(r.get("outcome", ""))
            if oc not in OUTCOME_ORDER:
                continue
            try:
                st = str(r.get("study", ""))
                ex = int(r.get("experiment_num", -1))
            except (TypeError, ValueError):
                continue
            if (st, ex) not in order:
                continue
            if not _participant_p_valid(r):
                continue
            p = float(r.get("p_value"))
            i = OUTCOME_ORDER.index(oc)
            j = order.index((st, ex))
            P[i, j] = p
            mask[i, j] = False
        return P, mask, row_labels, col_labels

    suf = title_suffix or (f" — {study_filter}" if study_filter else "")

    try:
        plt = _mpl()
        fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
        vmax = 3.0
        for ax, factor, title in zip(
            axes,
            ("layout", "display_count_4_vs_15"),
            (
                f"Participant level: layout (Friedman / paired Wilcoxon){suf}",
                f"Participant level: 4 vs 15 (paired Wilcoxon){suf}",
            ),
        ):
            P, mask_m, ylabs, xlabs = matrix_for_factor(factor)
            NL = np.full_like(P, np.nan, dtype=float)
            for i in range(P.shape[0]):
                for j in range(P.shape[1]):
                    if not mask_m[i, j] and P[i, j] > 0:
                        NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
            im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
            ax.set_xticks(range(len(xlabs)))
            ax.set_xticklabels(xlabs, fontsize=8)
            ax.set_yticks(range(len(ylabs)))
            ax.set_yticklabels(ylabs, fontsize=8)
            ax.set_title(title, fontsize=10)
            for i in range(NL.shape[0]):
                for j in range(NL.shape[1]):
                    if mask_m[i, j]:
                        ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=8)
                    else:
                        pv = P[i, j]
                        star = "*" if pv < 0.05 else ""
                        ax.text(
                            j,
                            i,
                            f"{pv:.3f}{star}",
                            ha="center",
                            va="center",
                            color="k" if (math.isnan(NL[i, j]) or NL[i, j] < 1.5) else "w",
                            fontsize=6,
                        )
            plt.colorbar(im, ax=ax, fraction=0.046, label="−log10(p)")
        fig.suptitle(
            f"Participant medians per cell; uncorrected p; * p<0.05 (see CSV for tests & n_participants){suf}",
            fontsize=10,
            y=1.01,
        )
        fig.tight_layout()
        name = "inferential_participant_level_pvalue_heatmaps_session.png"
        if study_filter:
            name = f"inferential_participant_level_pvalue_heatmaps_session_{study_filter}.png"
        fig.savefig(figures_dir / name, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        errors.append(f"participant_session_pvalue_heatmaps: {e}")

    return errors


def plot_participant_level_layout_within_display(
    tables_dir: Path,
    figures_dir: Path,
    study: str,
    dpi: int | None = None,
) -> List[str]:
    """Participant-level layout K–W analogue: Friedman / paired Wilcoxon at fixed 4 vs 15 displays."""
    dpi = dpi or config.FIGURE_DPI
    errors: List[str] = []
    csv_path = tables_dir / "inferential_participant_level_tests.csv"
    if not csv_path.is_file():
        return errors
    rows_all = read_csv_dicts(csv_path)
    rows_f = [
        r
        for r in rows_all
        if str(r.get("analysis_type")) == "layout_within_display"
        and str(r.get("study")) == study
        and str(r.get("factor")) == "layout"
        and str(r.get("test_level")) == "participant_median_per_cell"
    ]
    if not rows_f:
        return errors
    try:
        plt = _mpl()
        fig, axes = plt.subplots(1, 2, figsize=(11, 5.8))
        exp_order = (1, 2, 3)
        for ax, fixed_dc, title in zip(
            axes,
            (4, 15),
            (
                f"{study} (participant): layout at 4 displays",
                f"{study} (participant): layout at 15 displays",
            ),
        ):
            nrow, ncol = len(OUTCOME_ORDER), len(exp_order)
            P = np.full((nrow, ncol), np.nan, dtype=float)
            mask_m = np.ones((nrow, ncol), dtype=bool)
            for r in rows_f:
                try:
                    dc = int(float(r.get("subset_display_count", -1)))
                except (TypeError, ValueError):
                    continue
                if dc != fixed_dc:
                    continue
                oc = str(r.get("outcome", ""))
                if oc not in OUTCOME_ORDER:
                    continue
                try:
                    ex = int(r.get("experiment_num", -1))
                except (TypeError, ValueError):
                    continue
                if ex not in exp_order:
                    continue
                if not _participant_p_valid(r):
                    continue
                p = float(r.get("p_value"))
                i = OUTCOME_ORDER.index(oc)
                j = exp_order.index(ex)
                P[i, j] = p
                mask_m[i, j] = False
            vmax = 3.0
            NL = np.full_like(P, np.nan, dtype=float)
            for i in range(P.shape[0]):
                for j in range(P.shape[1]):
                    if not mask_m[i, j] and P[i, j] > 0:
                        NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
            im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
            ax.set_xticks(range(len(exp_order)))
            ax.set_xticklabels([f"Exp{e}" for e in exp_order], fontsize=9)
            ax.set_yticks(range(len(OUTCOME_ORDER)))
            ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOME_ORDER], fontsize=7)
            ax.set_title(title, fontsize=10)
            for i in range(nrow):
                for j in range(ncol):
                    if mask_m[i, j]:
                        ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=8)
                    else:
                        pv = P[i, j]
                        st = "*" if pv < 0.05 else ""
                        ax.text(
                            j,
                            i,
                            f"{pv:.3f}{st}",
                            ha="center",
                            va="center",
                            color="k" if NL[i, j] < 1.5 else "w",
                            fontsize=6,
                        )
            plt.colorbar(im, ax=ax, fraction=0.046, label="−log10(p)")
        fig.suptitle(
            f"{study}: participant-level layout (Friedman / paired Wilcoxon), fixed set size",
            fontsize=11,
            y=1.02,
        )
        fig.tight_layout()
        fig.savefig(
            figures_dir / f"inferential_participant_level_layout_within_display_{study}.png",
            dpi=dpi,
            bbox_inches="tight",
        )
        plt.close(fig)
    except Exception as e:
        errors.append(f"participant_layout_within_display_{study}: {e}")
    return errors


def plot_participant_level_display_within_layout(
    tables_dir: Path,
    figures_dir: Path,
    study: str,
    dpi: int | None = None,
) -> List[str]:
    """Participant-level 4 vs 15 (paired Wilcoxon) within each layout."""
    dpi = dpi or config.FIGURE_DPI
    errors: List[str] = []
    csv_path = tables_dir / "inferential_participant_level_tests.csv"
    if not csv_path.is_file():
        return errors
    rows_all = read_csv_dicts(csv_path)
    rows_f = [
        r
        for r in rows_all
        if str(r.get("analysis_type")) == "display_within_layout"
        and str(r.get("study")) == study
        and str(r.get("factor")) == "display_count_4_vs_15"
        and str(r.get("test_level")) == "participant_median_per_cell"
    ]
    if not rows_f:
        return errors
    try:
        keys_sorted: List[Tuple[int, str]] = sorted(
            {
                (int(r.get("experiment_num", -1)), str(r.get("subset_layout", "")))
                for r in rows_f
                if r.get("subset_layout")
            },
            key=lambda x: (x[0], x[1]),
        )
        if not keys_sorted:
            return errors
        plt = _mpl()
        ncol = len(keys_sorted)
        nrow = len(OUTCOME_ORDER)
        P = np.full((nrow, ncol), np.nan, dtype=float)
        mask_m = np.ones((nrow, ncol), dtype=bool)
        for r in rows_f:
            oc = str(r.get("outcome", ""))
            if oc not in OUTCOME_ORDER:
                continue
            try:
                ex = int(r.get("experiment_num", -1))
            except (TypeError, ValueError):
                continue
            lay = str(r.get("subset_layout", ""))
            if not lay or (ex, lay) not in keys_sorted:
                continue
            if not _participant_p_valid(r):
                continue
            p = float(r.get("p_value"))
            i = OUTCOME_ORDER.index(oc)
            j = keys_sorted.index((ex, lay))
            P[i, j] = p
            mask_m[i, j] = False
        fig, ax = plt.subplots(figsize=(max(8, ncol * 1.1), 6))
        vmax = 3.0
        NL = np.full_like(P, np.nan, dtype=float)
        for i in range(P.shape[0]):
            for j in range(P.shape[1]):
                if not mask_m[i, j] and P[i, j] > 0:
                    NL[i, j] = min(-math.log10(max(P[i, j], 1e-300)), vmax)
        im = ax.imshow(NL, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
        ax.set_xticks(range(ncol))
        ax.set_xticklabels([f"Exp{ex}\n{lay[:10]}" for ex, lay in keys_sorted], fontsize=7)
        ax.set_yticks(range(nrow))
        ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOME_ORDER], fontsize=8)
        ax.set_title(
            f"{study} (participant): paired Wilcoxon 4 vs 15 within each layout",
            fontsize=10,
        )
        for i in range(nrow):
            for j in range(ncol):
                if mask_m[i, j]:
                    ax.text(j, i, "—", ha="center", va="center", color="0.5", fontsize=7)
                else:
                    pv = P[i, j]
                    st = "*" if pv < 0.05 else ""
                    ax.text(
                        j,
                        i,
                        f"{pv:.3f}{st}",
                        ha="center",
                        va="center",
                        color="k" if NL[i, j] < 1.5 else "w",
                        fontsize=6,
                    )
        plt.colorbar(im, ax=ax, fraction=0.035, label="−log10(p)")
        fig.tight_layout()
        fig.savefig(
            figures_dir / f"inferential_participant_level_display_within_layout_{study}.png",
            dpi=dpi,
            bbox_inches="tight",
        )
        plt.close(fig)
    except Exception as e:
        errors.append(f"participant_display_within_layout_{study}: {e}")
    return errors


def plot_inferential_companion_figures(
    tables_dir: Path,
    figures_dir: Path,
    *,
    study_label: str = "",
    dpi: int | None = None,
    split_by_experiment: bool = False,
) -> List[str]:
    """
    Bar figures from companion CSVs (post-hoc layout pairs with Holm q<0.05;
    Cliff's delta for significant 4 vs 15 tests). tables_dir contains the CSVs.

    When ``split_by_experiment`` is True and ``study_label`` is set (e.g. Study1),
    saves one PNG per Exp1–Exp3 to avoid overlapping y-axis labels.
    """
    dpi = dpi or config.FIGURE_DPI
    figures_dir.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    suf = f" {study_label}".strip()

    def _f(x: Any) -> float:
        try:
            return float(x)
        except (TypeError, ValueError):
            return float("nan")

    def _exp_num(r: Dict[str, Any]) -> int:
        try:
            return int(float(r.get("experiment_num", -1)))
        except (TypeError, ValueError):
            return -1

    try:
        plt = _mpl()
    except Exception as e:  # pragma: no cover
        return [f"companion_plots_matplotlib: {e}"]

    posthoc_rows = read_csv_dicts(tables_dir / "inferential_posthoc_layout_pairwise_holm.csv")
    mw_rows = read_csv_dicts(tables_dir / "inferential_effect_sizes_4_vs_15_cliffs_delta.csv")

    def _save_posthoc_bars(sig_ph: List[Dict[str, Any]], path: Path, title_suffix: str) -> None:
        if not sig_ph:
            return
        sig_ph = sorted(sig_ph, key=lambda r: _f(r.get("holm_adjusted_p")))
        row_h = 0.48
        fig, ax = plt.subplots(figsize=(10.5, max(4.2, row_h * len(sig_ph))))
        xs: List[float] = []
        ylabs: List[str] = []
        colors: List[str] = []
        for r in sig_ph:
            dmed = _f(r.get("median_diff_a_minus_b"))
            xs.append(dmed)
            oc = OUTCOME_LABELS.get(str(r.get("outcome")), str(r.get("outcome", "")))
            at = str(r.get("analysis_type", ""))[:22]
            dc = str(r.get("subset_display_count") or "").strip()
            dc_s = f" dc{dc}" if dc else ""
            exp = str(r.get("experiment_num", ""))
            st = str(r.get("study", ""))
            la = str(r.get("group_a", ""))[:14]
            lb = str(r.get("group_b", ""))[:14]
            ylabs.append(f"{st} Exp{exp}{dc_s}\n{la} vs {lb}\n{oc}\n({at})")
            colors.append("coral" if dmed > 0 else "steelblue")
        ax.barh(range(len(sig_ph)), xs, color=colors, alpha=0.85)
        ax.axvline(0, color="0.4", linewidth=0.8)
        ax.set_yticks(range(len(sig_ph)))
        ax.set_yticklabels(ylabs, fontsize=8, linespacing=1.15)
        ax.set_xlabel("Median difference (group A − group B); sign is outcome-specific")
        ax.set_title(f"Post-hoc layout pairs (Mann–Whitney; Holm-adjusted p < 0.05){title_suffix}")
        ax.grid(True, axis="x", alpha=0.3)
        fig.subplots_adjust(left=0.34)
        fig.tight_layout()
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    def _save_cliffs_bars(rows: List[Dict[str, Any]], path: Path, title_suffix: str) -> None:
        if not rows:
            return
        rows = sorted(rows, key=lambda r: abs(_f(r.get("cliffs_delta_4_vs_15"))), reverse=True)
        row_h = 0.42
        fig, ax = plt.subplots(figsize=(10.5, max(4.2, row_h * len(rows))))
        xs2 = [_f(r.get("cliffs_delta_4_vs_15")) for r in rows]
        ylabs2: List[str] = []
        for r in rows:
            oc = OUTCOME_LABELS.get(str(r.get("outcome")), str(r.get("outcome", "")))
            st = str(r.get("study", ""))
            exp = str(r.get("experiment_num", ""))
            at = str(r.get("analysis_type", ""))[:18]
            lay = str(r.get("subset_layout") or "")[:12]
            lay_s = f" {lay}" if lay else ""
            ylabs2.append(f"{st} Exp{exp}{lay_s}\n{oc}\n({at})")
        cols = ["steelblue" if x >= 0 else "coral" for x in xs2]
        ax.barh(range(len(rows)), xs2, color=cols, alpha=0.85)
        ax.axvline(0, color="0.4", linewidth=0.8)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(ylabs2, fontsize=8, linespacing=1.15)
        ax.set_xlabel("Cliff's delta (4 vs 15); + ⇒ 4 tends higher than 15")
        ax.set_title(f"Effect sizes for significant 4 vs 15 (Mann–Whitney p < 0.05){title_suffix}")
        ax.set_xlim(-1.05, 1.05)
        ax.grid(True, axis="x", alpha=0.3)
        fig.subplots_adjust(left=0.34)
        fig.tight_layout()
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    try:
        sig_ph_all = [r for r in posthoc_rows if str(r.get("significant_holm_0.05")) == "yes"]
        sl = study_label.replace(" ", "_") if study_label else ""
        if split_by_experiment and study_label:
            for exp in (1, 2, 3):
                sig_ph = [r for r in sig_ph_all if _exp_num(r) == exp]
                if not sig_ph:
                    continue
                _save_posthoc_bars(
                    sig_ph,
                    figures_dir / f"inferential_posthoc_layout_median_diffs_holm_005_{sl}_Exp{exp}.png",
                    f"{suf} — Exp{exp}",
                )
        elif sig_ph_all:
            fn = "inferential_posthoc_layout_median_diffs_holm_005.png"
            if study_label:
                fn = f"inferential_posthoc_layout_median_diffs_holm_005_{sl}.png"
            _save_posthoc_bars(sig_ph_all, figures_dir / fn, suf)
    except Exception as e:
        errors.append(f"companion_posthoc_bars: {e}")

    try:
        sl = study_label.replace(" ", "_") if study_label else ""
        if split_by_experiment and study_label:
            for exp in (1, 2, 3):
                mwe = [r for r in mw_rows if _exp_num(r) == exp]
                if not mwe:
                    continue
                _save_cliffs_bars(
                    mwe,
                    figures_dir / f"inferential_cliffs_delta_4_vs_15_significant_{sl}_Exp{exp}.png",
                    f"{suf} — Exp{exp}",
                )
        elif mw_rows:
            fn2 = "inferential_cliffs_delta_4_vs_15_significant.png"
            if study_label:
                fn2 = f"inferential_cliffs_delta_4_vs_15_significant_{sl}.png"
            _save_cliffs_bars(mw_rows, figures_dir / fn2, suf)
    except Exception as e:
        errors.append(f"companion_cliffs_bars: {e}")

    return errors


def run_tables_and_plots(
    results: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    snippet: Dict[str, Any] = {"inferential_figure_errors": []}

    enriched = add_readable_columns(results)
    write_supplemental_tables(enriched, output_dir / "tables")

    for std in ("Study1", "Study2"):
        sub = [r for r in enriched if str(r.get("study")) == std]
        write_supplemental_tables(sub, output_dir / std / "tables")

    all_fig_errs: List[str] = []
    study_strata = {
        "Study1": tuple((s, e) for s, e in STRATA_ORDER if s == "Study1"),
        "Study2": tuple((s, e) for s, e in STRATA_ORDER if s == "Study2"),
    }

    all_fig_errs += plot_inferential_figures(
        enriched, output_dir / "figures", study_filter=None, strata_order=STRATA_ORDER, title_suffix=" (all studies)"
    )
    for std in ("Study1", "Study2"):
        all_fig_errs += plot_inferential_figures(
            enriched,
            output_dir / std / "figures",
            study_filter=std,
            strata_order=study_strata[std],
            title_suffix=f" ({std} only)",
        )
        all_fig_errs += plot_stratified_layout_within_display(
            enriched, output_dir / std / "figures", std
        )
        all_fig_errs += plot_stratified_display_within_layout(
            enriched, output_dir / std / "figures", std
        )

    all_fig_errs += plot_inferential_companion_figures(
        output_dir / "tables",
        output_dir / "figures",
        study_label="",
    )
    for std in ("Study1", "Study2"):
        all_fig_errs += plot_inferential_companion_figures(
            output_dir / std / "tables",
            output_dir / std / "figures",
            study_label=std,
            split_by_experiment=True,
        )

    all_fig_errs += plot_participant_level_session_heatmaps(
        output_dir / "tables",
        output_dir / "figures",
        study_filter=None,
        strata_order=STRATA_ORDER,
        title_suffix=" (all studies)",
    )
    for std in ("Study1", "Study2"):
        all_fig_errs += plot_participant_level_session_heatmaps(
            output_dir / std / "tables",
            output_dir / std / "figures",
            study_filter=std,
            strata_order=study_strata[std],
            title_suffix=f" ({std} only)",
        )
        all_fig_errs += plot_participant_level_layout_within_display(
            output_dir / std / "tables",
            output_dir / std / "figures",
            std,
        )
        all_fig_errs += plot_participant_level_display_within_layout(
            output_dir / std / "tables",
            output_dir / std / "figures",
            std,
        )

    snippet["inferential_figure_errors"] = [e for e in all_fig_errs if e]
    snippet["n_enriched_rows"] = len(enriched)

    return snippet
