"""
Participant-level (between-subject unit) nonparametric tests to complement trial-level
inferential_stats: paired Wilcoxon for 4 vs 15; Friedman or paired Wilcoxon for layout.

Each participant contributes one summary (median of trials or blocks) per stratum cell.
Trials remain nested within participant; these tests use one observation per participant
per contrast where paired/complete designs allow.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .inferential_stats import (
    _block_error_rate_value,
    _block_stratum,
    _display_bin,
    _finite_float,
    _layout_key,
    _layouts_in_session,
    _trial_stratum,
)
from .io_tables import write_csv

try:
    from scipy.stats import friedmanchisquare, wilcoxon

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False
    friedmanchisquare = None  # type: ignore
    wilcoxon = None  # type: ignore


def _median(xs: List[float]) -> float:
    if not xs:
        return float("nan")
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return float(s[mid - 1] + s[mid]) / 2.0


def _subject_id(row: Dict[str, Any]) -> Optional[int]:
    v = row.get("subject_id")
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _append_row(
    out: List[Dict[str, Any]],
    *,
    study: str,
    experiment_num: int,
    analysis_type: str,
    outcome: str,
    factor: str,
    test: str,
    statistic: float,
    p_value: float,
    n_participants: int,
    detail: str,
    subset_display_count: str = "",
    subset_layout: str = "",
) -> None:
    sig = ""
    if not math.isnan(p_value):
        sig = "yes" if p_value < 0.05 else "no"
    out.append(
        {
            "study": study,
            "experiment_num": experiment_num,
            "analysis_type": analysis_type,
            "subset_display_count": subset_display_count,
            "subset_layout": subset_layout,
            "outcome": outcome,
            "factor": factor,
            "test": test,
            "statistic": statistic,
            "p_value": p_value,
            "significant_alpha_0.05": sig,
            "n_participants": n_participants,
            "detail": detail,
            "test_level": "participant_median_per_cell",
        }
    )


def _wilcoxon_paired(
    a: Sequence[float], b: Sequence[float]
) -> Tuple[str, float, float, str]:
    """Paired two-sided Wilcoxon on equal-length vectors."""
    if not _HAS_SCIPY:
        return "wilcoxon_signed_rank", float("nan"), float("nan"), "scipy_not_installed"
    aa = [float(x) for x in a]
    bb = [float(x) for x in b]
    if len(aa) != len(bb) or len(aa) < 2:
        return "wilcoxon_signed_rank", float("nan"), float("nan"), "n_paired_lt_2"
    try:
        stat, p = wilcoxon(aa, bb, alternative="two-sided", zero_method="wilcox")  # type: ignore[misc]
    except Exception as e:
        return "wilcoxon_signed_rank", float("nan"), float("nan"), f"test_failed:{e}"
    return "wilcoxon_signed_rank", float(stat), float(p), f"n_pairs={len(aa)}"


def _friedman_layout(
    layouts: List[str], subject_vals: Dict[int, Dict[str, float]]
) -> Tuple[str, float, float, str, int]:
    """Friedman test on complete cases (each subject has a value for every layout)."""
    if not _HAS_SCIPY:
        return "friedman", float("nan"), float("nan"), "scipy_not_installed", 0
    if len(layouts) < 3:
        return "friedman", float("nan"), float("nan"), "fewer_than_three_layouts", 0
    complete: List[int] = []
    for sj, by_lay in subject_vals.items():
        if all(l in by_lay for l in layouts):
            complete.append(sj)
    if len(complete) < 3:
        return "friedman", float("nan"), float("nan"), "fewer_than_three_complete_subjects", len(complete)
    cols: List[List[float]] = []
    for l in layouts:
        cols.append([subject_vals[sj][l] for sj in complete])
    try:
        stat, p = friedmanchisquare(*cols)  # type: ignore[misc]
    except Exception as e:
        return "friedman", float("nan"), float("nan"), f"test_failed:{e}", len(complete)
    detail = f"n_complete={len(complete)}; layouts={','.join(layouts)}"
    return "friedman", float(stat), float(p), detail, len(complete)


def _layout_test_participant_medians(
    subject_vals: Dict[int, Dict[str, float]],
) -> Tuple[str, float, float, str, int]:
    """Two layouts: paired Wilcoxon on per-subject medians; 3+: Friedman on complete cases."""
    layouts = sorted({l for d in subject_vals.values() for l in d.keys()}, key=str)
    if len(layouts) < 2:
        return "layout_participant", float("nan"), float("nan"), "fewer_than_two_layouts", 0
    if len(layouts) == 2:
        l1, l2 = layouts[0], layouts[1]
        paired_a: List[float] = []
        paired_b: List[float] = []
        for _, by_l in subject_vals.items():
            if l1 in by_l and l2 in by_l:
                paired_a.append(by_l[l1])
                paired_b.append(by_l[l2])
        tn, st, pv, det = _wilcoxon_paired(paired_a, paired_b)
        return tn, st, pv, f"{det}; layout_pair={l1}_vs_{l2}", len(paired_a)
    tn, st, pv, det, n_c = _friedman_layout(layouts, subject_vals)
    return tn, st, pv, det, n_c


def _trial_subject_medians_by_layout(
    rows: List[Dict[str, Any]], col: str, fixed_dc: Optional[int] = None
) -> Dict[int, Dict[str, float]]:
    """subject_id -> layout -> median of trial metric."""
    buckets: Dict[Tuple[int, str], List[float]] = {}
    for t in rows:
        sj = _subject_id(t)
        if sj is None:
            continue
        lay = _layout_key(t)
        if lay is None:
            continue
        if fixed_dc is not None and _display_bin(t.get("display_count")) != fixed_dc:
            continue
        y = _finite_float(t.get(col))
        if y is None:
            continue
        buckets.setdefault((sj, lay), []).append(y)
    out: Dict[int, Dict[str, float]] = {}
    for (sj, lay), ys in buckets.items():
        out.setdefault(sj, {})[lay] = _median(ys)
    return out


def _trial_paired_m4_m15(
    rows: List[Dict[str, Any]], col: str, fixed_layout: Optional[str] = None
) -> Tuple[List[float], List[float], str]:
    """Per-subject medians for 4- and 15-display trials; paired lists for Wilcoxon."""
    by_sj: Dict[int, Dict[str, List[float]]] = {}
    for t in rows:
        sj = _subject_id(t)
        if sj is None:
            continue
        lay = _layout_key(t)
        if fixed_layout is not None and lay != fixed_layout:
            continue
        dc = _display_bin(t.get("display_count"))
        if dc not in (4, 15):
            continue
        y = _finite_float(t.get(col))
        if y is None:
            continue
        by_sj.setdefault(sj, {}).setdefault(str(dc), []).append(y)
    a: List[float] = []
    b: List[float] = []
    for _, g in by_sj.items():
        v4 = g.get("4") or []
        v15 = g.get("15") or []
        if v4 and v15:
            a.append(_median(v4))
            b.append(_median(v15))
    return a, b, f"n_subjects_with_both_4_and_15={len(a)}"


def _block_subject_medians_by_layout(
    rows: List[Dict[str, Any]], fixed_dc: Optional[int] = None
) -> Dict[int, Dict[str, float]]:
    buckets: Dict[Tuple[int, str], List[float]] = {}
    for b in rows:
        sj = _subject_id(b)
        if sj is None:
            continue
        lay = _layout_key(b)
        if lay is None:
            continue
        if fixed_dc is not None and _display_bin(b.get("display_count")) != fixed_dc:
            continue
        rate = _block_error_rate_value(b)
        if rate is None:
            continue
        buckets.setdefault((sj, lay), []).append(rate)
    out: Dict[int, Dict[str, float]] = {}
    for (sj, lay), ys in buckets.items():
        out.setdefault(sj, {})[lay] = _median(ys)
    return out


def _block_paired_m4_m15(
    rows: List[Dict[str, Any]], fixed_layout: Optional[str] = None
) -> Tuple[List[float], List[float], str]:
    by_sj: Dict[int, Dict[str, List[float]]] = {}
    for b in rows:
        sj = _subject_id(b)
        if sj is None:
            continue
        lay = _layout_key(b)
        if fixed_layout is not None and lay != fixed_layout:
            continue
        dc = _display_bin(b.get("display_count"))
        if dc not in (4, 15):
            continue
        rate = _block_error_rate_value(b)
        if rate is None:
            continue
        by_sj.setdefault(sj, {}).setdefault(str(dc), []).append(rate)
    a: List[float] = []
    b: List[float] = []
    for _, g in by_sj.items():
        v4 = g.get("4") or []
        v15 = g.get("15") or []
        if v4 and v15:
            a.append(_median(v4))
            b.append(_median(v15))
    return a, b, f"n_subjects_with_both_4_and_15={len(a)}"


def run_participant_level_inferential(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    out: List[Dict[str, Any]] = []
    studies = ("Study1", "Study2")
    exps = (1, 2, 3)

    trial_outcomes_exp12 = (
        ("selection_time_sec", "time_per_selection"),
        ("unity_ttff_sec", "ttff"),
        ("reengagement_after_overlook_sec", "reengagement_after_overlook"),
        ("overlooked_view_sample_count", "overlooked_view_samples_post_first_hit"),
        ("delayed_discovery_flag", "delayed_binary_flag"),
        ("log_process_density", "log_process_density"),
    )
    trial_outcomes_exp3 = (("selection_time_sec", "time_per_selection"),)

    if not _HAS_SCIPY:
        stub = [
            {
                "study": "",
                "experiment_num": "",
                "analysis_type": "",
                "subset_display_count": "",
                "subset_layout": "",
                "outcome": "",
                "factor": "",
                "test": "",
                "statistic": "",
                "p_value": "",
                "significant_alpha_0.05": "",
                "n_participants": "",
                "detail": "scipy_not_installed",
                "test_level": "participant_median_per_cell",
            }
        ]
        write_csv(tables_dir / "inferential_participant_level_tests.csv", stub)
        for std in studies:
            (output_dir / std / "tables").mkdir(parents=True, exist_ok=True)
            write_csv(output_dir / std / "tables" / "inferential_participant_level_tests.csv", stub)
        return {"n_participant_level_rows": 0, "participant_level_note": "scipy_not_installed"}

    for study in studies:
        for exp_num in exps:
            trial_outcomes = trial_outcomes_exp3 if exp_num == 3 else trial_outcomes_exp12
            tr_sub = _trial_stratum(trials, study, exp_num)
            bl_sub = _block_stratum(blocks, study, exp_num)

            # --- Session omnibus: layout (participant medians), 4 vs 15 paired ---
            for col, short_name in trial_outcomes:
                sm = _trial_subject_medians_by_layout(tr_sub, col, None)
                tn, st, pv, det, n_p = _layout_test_participant_medians(sm)
                _append_row(
                    out,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="session_omnibus",
                    outcome=short_name,
                    factor="layout",
                    test=tn,
                    statistic=st,
                    p_value=pv,
                    n_participants=n_p,
                    detail=det,
                )
                pa, pb, d4 = _trial_paired_m4_m15(tr_sub, col, None)
                tn, st, pv, det2 = _wilcoxon_paired(pa, pb)
                _append_row(
                    out,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="session_omnibus",
                    outcome=short_name,
                    factor="display_count_4_vs_15",
                    test=tn,
                    statistic=st,
                    p_value=pv,
                    n_participants=len(pa),
                    detail=f"{d4}; {det2}",
                )

            sm_b = _block_subject_medians_by_layout(bl_sub, None)
            tn, st, pv, det, n_pb = _layout_test_participant_medians(sm_b)
            _append_row(
                out,
                study=study,
                experiment_num=exp_num,
                analysis_type="session_omnibus",
                outcome="block_error_rate",
                factor="layout",
                test=tn,
                statistic=st,
                p_value=pv,
                n_participants=n_pb,
                detail=det,
            )
            ba, bb, db4 = _block_paired_m4_m15(bl_sub, None)
            tn, st, pv, det2 = _wilcoxon_paired(ba, bb)
            _append_row(
                out,
                study=study,
                experiment_num=exp_num,
                analysis_type="session_omnibus",
                outcome="block_error_rate",
                factor="display_count_4_vs_15",
                test=tn,
                statistic=st,
                p_value=pv,
                n_participants=len(ba),
                detail=f"{db4}; {det2}",
            )

            # --- layout_within_display ---
            for fixed_dc in (4, 15):
                sdc = str(fixed_dc)
                for col, short_name in trial_outcomes:
                    sm = _trial_subject_medians_by_layout(tr_sub, col, fixed_dc)
                    tn, st, pv, det, n_p = _layout_test_participant_medians(sm)
                    _append_row(
                        out,
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="layout_within_display",
                        outcome=short_name,
                        factor="layout",
                        test=tn,
                        statistic=st,
                        p_value=pv,
                        n_participants=n_p,
                        detail=det,
                        subset_display_count=sdc,
                    )
                sm_bb = _block_subject_medians_by_layout(bl_sub, fixed_dc)
                tn, st, pv, det, n_p_b = _layout_test_participant_medians(sm_bb)
                _append_row(
                    out,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="layout_within_display",
                    outcome="block_error_rate",
                    factor="layout",
                    test=tn,
                    statistic=st,
                    p_value=pv,
                    n_participants=n_p_b,
                    detail=det,
                    subset_display_count=sdc,
                )

            # --- display_within_layout ---
            for lay in _layouts_in_session(tr_sub):
                for col, short_name in trial_outcomes:
                    pa, pb, d4 = _trial_paired_m4_m15(tr_sub, col, lay)
                    tn, st, pv, det2 = _wilcoxon_paired(pa, pb)
                    _append_row(
                        out,
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="display_within_layout",
                        outcome=short_name,
                        factor="display_count_4_vs_15",
                        test=tn,
                        statistic=st,
                        p_value=pv,
                        n_participants=len(pa),
                        detail=f"{d4}; layout={lay}; {det2}",
                        subset_layout=lay,
                    )
                ba, bb, db4 = _block_paired_m4_m15(bl_sub, lay)
                tn, st, pv, det2 = _wilcoxon_paired(ba, bb)
                _append_row(
                    out,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="display_within_layout",
                    outcome="block_error_rate",
                    factor="display_count_4_vs_15",
                    test=tn,
                    statistic=st,
                    p_value=pv,
                    n_participants=len(ba),
                    detail=f"{db4}; layout={lay}; {det2}",
                    subset_layout=lay,
                )

    write_csv(tables_dir / "inferential_participant_level_tests.csv", out)
    for std in studies:
        sub = [r for r in out if str(r.get("study")) == std]
        (output_dir / std / "tables").mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / std / "tables" / "inferential_participant_level_tests.csv", sub)

    return {
        "n_participant_level_rows": len(out),
        "participant_level_note": (
            "Participant-level tests: paired Wilcoxon on per-participant medians for 4 vs 15; "
            "two layouts = paired Wilcoxon on layout medians; three or more layouts = Friedman on "
            "subjects with complete medians across all layouts. Complements trial-level screening."
        ),
    }
