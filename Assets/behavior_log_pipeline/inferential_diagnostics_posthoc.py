"""
Companion outputs for inferential stats: group descriptives, normality screening,
Holm-corrected pairwise Mann–Whitney after significant Kruskal–Wallis (layout),
and Cliff's delta after significant two-sample Mann–Whitney (4 vs 15).

Trials remain non-independent within participant; all outputs are exploratory.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .io_tables import write_csv

# For latency / error-style outcomes, larger values are typically worse for thesis wording.
OUTCOME_HIGHER_IS_WORSE: Dict[str, bool] = {
    "time_per_selection": True,
    "ttff": True,
    "reengagement_after_overlook": True,
    "overlooked_view_samples_post_first_hit": True,
    "delayed_binary_flag": True,
    "log_process_density": True,
    "block_error_rate": True,
}


def _median(xs: List[float]) -> float:
    if not xs:
        return float("nan")
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return float(s[mid - 1] + s[mid]) / 2.0


def _mean(xs: List[float]) -> float:
    if not xs:
        return float("nan")
    return float(sum(xs) / len(xs))


def _stdev(xs: List[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    m = _mean(xs)
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return float(math.sqrt(v))


def cliffs_delta(a: List[float], b: List[float]) -> float:
    """Cliff's delta: P(X>Y) - P(X<Y) with X from a, Y from b. Range [-1, 1]."""
    na, nb = len(a), len(b)
    if na == 0 or nb == 0:
        return float("nan")
    more = less = 0
    for x in a:
        for y in b:
            if x > y:
                more += 1
            elif x < y:
                less += 1
    return (more - less) / float(na * nb)


def holm_adjusted_pvalues(p_values: Sequence[float]) -> List[float]:
    """Holm–Bonferroni adjusted p-values (same order as inputs)."""
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    sorted_p = [p_values[i] for i in order]
    adj_sorted: List[float] = []
    running_max = 0.0
    for i in range(m):
        val = min(1.0, sorted_p[i] * (m - i))
        running_max = max(running_max, val)
        adj_sorted.append(running_max)
    out = [0.0] * m
    for j in range(m):
        out[order[j]] = adj_sorted[j]
    return out


def _shapiro_on_group(vals: List[float]) -> Tuple[str, float, float]:
    """Return (note, W, p). May skip large n or small n."""
    n = len(vals)
    if n < 3:
        return "skipped_n_lt_3", float("nan"), float("nan")
    if n > 5000:
        return "skipped_n_gt_5000_not_recommended_for_shapiro", float("nan"), float("nan")
    try:
        from scipy.stats import shapiro

        w, p = shapiro(vals)
        return "ok", float(w), float(p)
    except Exception:
        return "shapiro_failed", float("nan"), float("nan")


def _kruskal_context_key(r: Dict[str, Any]) -> Tuple[Any, ...]:
    sdc = r.get("subset_display_count", "")
    if sdc == "" or sdc is None:
        sdc_k = ""
    else:
        try:
            sdc_k = str(int(float(sdc)))
        except (TypeError, ValueError):
            sdc_k = str(sdc)
    return (
        str(r.get("study", "")),
        int(r.get("experiment_num", -1)),
        str(r.get("analysis_type", "")),
        str(r.get("outcome", "")),
        sdc_k,
        str(r.get("subset_layout", "") or ""),
    )


def _significant_kruskal_layout_keys(results: List[Dict[str, Any]]) -> Set[Tuple[Any, ...]]:
    keys: Set[Tuple[Any, ...]] = set()
    for r in results:
        if str(r.get("test", "")) != "kruskal_wallis":
            continue
        if str(r.get("factor", "")) != "layout":
            continue
        try:
            p = float(r.get("p_value"))
        except (TypeError, ValueError):
            continue
        if math.isnan(p) or p >= 0.05:
            continue
        keys.add(_kruskal_context_key(r))
    return keys


def _significant_mw_display_keys(results: List[Dict[str, Any]]) -> Set[Tuple[Any, ...]]:
    keys: Set[Tuple[Any, ...]] = set()
    for r in results:
        if str(r.get("test", "")) != "mannwhitney_u":
            continue
        if str(r.get("factor", "")) != "display_count_4_vs_15":
            continue
        try:
            p = float(r.get("p_value"))
        except (TypeError, ValueError):
            continue
        if math.isnan(p) or p >= 0.05:
            continue
        keys.add(_kruskal_context_key(r))
    return keys


def _mw_direction_label(
    outcome: str, median_4: float, median_15: float
) -> str:
    worse = OUTCOME_HIGHER_IS_WORSE.get(outcome, True)
    if math.isnan(median_4) or math.isnan(median_15):
        return "ambiguous"
    if median_4 == median_15:
        return "medians_equal"
    higher = "4 displays" if median_4 > median_15 else "15 displays"
    if worse:
        return f"{higher} shows larger (worse) median for this outcome"
    return f"{higher} shows larger median (interpret with outcome semantics)"


def _pairwise_direction(
    outcome: str, med_a: float, med_b: float, label_a: str, label_b: str
) -> str:
    worse = OUTCOME_HIGHER_IS_WORSE.get(outcome, True)
    if math.isnan(med_a) or math.isnan(med_b):
        return "ambiguous"
    mb = med_b
    if med_a == mb:
        return "medians_equal"
    hi = label_a if med_a > mb else label_b
    lo = label_b if med_a > mb else label_a
    if worse:
        return f"higher median (worse): {hi}; lower (better): {lo}"
    return f"higher median: {hi}; lower: {lo}"


def run_companion_outputs(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    """Emit descriptives / normality, post-hoc layout pairs, MW effect CSVs; return manifest snippet."""
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    from . import inferential_stats as is_

    sig_kw = _significant_kruskal_layout_keys(results)
    sig_mw = _significant_mw_display_keys(results)

    descriptive_rows: List[Dict[str, Any]] = []
    posthoc_rows: List[Dict[str, Any]] = []
    mw_effect_rows: List[Dict[str, Any]] = []

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

    def emit_descriptives_for_groups(
        by_l: Dict[str, List[float]],
        *,
        study: str,
        experiment_num: int,
        analysis_type: str,
        outcome: str,
        subset_display_count: str,
        subset_layout: str,
        data_level: str,
    ) -> None:
        for gname, vals in sorted(by_l.items(), key=lambda x: str(x[0])):
            if not vals:
                continue
            note, sw, sp = _shapiro_on_group(vals)
            descriptive_rows.append(
                {
                    "study": study,
                    "experiment_num": experiment_num,
                    "analysis_type": analysis_type,
                    "outcome": outcome,
                    "subset_display_count": subset_display_count,
                    "subset_layout": subset_layout,
                    "data_level": data_level,
                    "group": gname,
                    "n": len(vals),
                    "mean": round(_mean(vals), 6),
                    "median": round(_median(vals), 6),
                    "stdev": round(_stdev(vals), 6) if len(vals) > 1 else "",
                    "shapiro_note": note,
                    "shapiro_statistic": "" if math.isnan(sw) else sw,
                    "shapiro_p": "" if math.isnan(sp) else sp,
                }
            )

    def maybe_posthoc_layout(
        by_l: Dict[str, List[float]],
        *,
        study: str,
        experiment_num: int,
        analysis_type: str,
        outcome: str,
        subset_display_count: str,
        subset_layout: str,
        data_level: str,
    ) -> None:
        key = (
            study,
            experiment_num,
            analysis_type,
            outcome,
            subset_display_count,
            subset_layout,
        )
        if key not in sig_kw:
            return
        groups = {k: v for k, v in by_l.items() if len(v) > 0}
        labels = sorted(groups.keys(), key=str)
        if len(labels) < 2:
            return
        pairs: List[Tuple[str, str, float]] = []
        try:
            from scipy.stats import mannwhitneyu
        except ImportError:
            return
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                la, lb = labels[i], labels[j]
                va, vb = groups[la], groups[lb]
                try:
                    _, p = mannwhitneyu(va, vb, alternative="two-sided")
                except ValueError:
                    continue
                pairs.append((la, lb, float(p)))

        if not pairs:
            return
        raw_ps = [p for _, _, p in pairs]
        holm_ps = holm_adjusted_pvalues(raw_ps)
        for k, (la, lb, p_raw) in enumerate(pairs):
            va, vb = groups[la], groups[lb]
            ma, mb = _median(va), _median(vb)
            posthoc_rows.append(
                {
                    "study": study,
                    "experiment_num": experiment_num,
                    "analysis_type": analysis_type,
                    "outcome": outcome,
                    "subset_display_count": subset_display_count,
                    "subset_layout": subset_layout,
                    "data_level": data_level,
                    "group_a": la,
                    "group_b": lb,
                    "n_a": len(va),
                    "n_b": len(vb),
                    "median_a": round(ma, 6),
                    "median_b": round(mb, 6),
                    "median_diff_a_minus_b": round(ma - mb, 6),
                    "mannwhitney_p_uncorrected": p_raw,
                    "holm_adjusted_p": holm_ps[k],
                    "significant_holm_0.05": "yes" if holm_ps[k] < 0.05 else "no",
                    "direction_summary": _pairwise_direction(outcome, ma, mb, la, lb),
                    "posthoc_method": "pairwise_mannwhitney_holm_within_omnibus_context",
                }
            )

    def maybe_mw_effects(
        v4: List[float],
        v15: List[float],
        *,
        study: str,
        experiment_num: int,
        analysis_type: str,
        outcome: str,
        subset_display_count: str,
        subset_layout: str,
        data_level: str,
    ) -> None:
        key = (
            study,
            experiment_num,
            analysis_type,
            outcome,
            subset_display_count,
            subset_layout,
        )
        if key not in sig_mw:
            return
        if not v4 or not v15:
            return
        d = cliffs_delta(v4, v15)
        m4, m15 = _median(v4), _median(v15)
        mw_effect_rows.append(
            {
                "study": study,
                "experiment_num": experiment_num,
                "analysis_type": analysis_type,
                "outcome": outcome,
                "subset_display_count": subset_display_count,
                "subset_layout": subset_layout,
                "data_level": data_level,
                "n_4": len(v4),
                "n_15": len(v15),
                "median_4": round(m4, 6),
                "median_15": round(m15, 6),
                "median_diff_4_minus_15": round(m4 - m15, 6),
                "cliffs_delta_4_vs_15": round(d, 6) if not math.isnan(d) else "",
                "direction_summary": _mw_direction_label(outcome, m4, m15),
                "cliffs_delta_note": "positive => values tend larger in 4-display sample than 15-display sample",
            }
        )

    for study in studies:
        for exp_num in exps:
            trial_outcomes = trial_outcomes_exp3 if exp_num == 3 else trial_outcomes_exp12
            tr_sub = is_._trial_stratum(trials, study, exp_num)
            bl_sub = is_._block_stratum(blocks, study, exp_num)

            for col, short_name in trial_outcomes:
                by_l, v4, v15 = is_._gather_trial_outcome(tr_sub, col)
                emit_descriptives_for_groups(
                    by_l,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="session_omnibus",
                    outcome=short_name,
                    subset_display_count="",
                    subset_layout="",
                    data_level="trial",
                )
                maybe_posthoc_layout(
                    by_l,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="session_omnibus",
                    outcome=short_name,
                    subset_display_count="",
                    subset_layout="",
                    data_level="trial",
                )
                maybe_mw_effects(
                    v4,
                    v15,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="session_omnibus",
                    outcome=short_name,
                    subset_display_count="",
                    subset_layout="",
                    data_level="trial",
                )

            by_l_b, v4b, v15b = is_._gather_block_error_rate(bl_sub)
            emit_descriptives_for_groups(
                by_l_b,
                study=study,
                experiment_num=exp_num,
                analysis_type="session_omnibus",
                outcome="block_error_rate",
                subset_display_count="",
                subset_layout="",
                data_level="block",
            )
            maybe_posthoc_layout(
                by_l_b,
                study=study,
                experiment_num=exp_num,
                analysis_type="session_omnibus",
                outcome="block_error_rate",
                subset_display_count="",
                subset_layout="",
                data_level="block",
            )
            maybe_mw_effects(
                v4b,
                v15b,
                study=study,
                experiment_num=exp_num,
                analysis_type="session_omnibus",
                outcome="block_error_rate",
                subset_display_count="",
                subset_layout="",
                data_level="block",
            )

            for fixed_dc in (4, 15):
                sdc = str(fixed_dc)
                for col, short_name in trial_outcomes:
                    by_l = is_._gather_trial_by_layout_for_dc(tr_sub, col, fixed_dc)
                    emit_descriptives_for_groups(
                        by_l,
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="layout_within_display",
                        outcome=short_name,
                        subset_display_count=sdc,
                        subset_layout="",
                        data_level="trial",
                    )
                    maybe_posthoc_layout(
                        by_l,
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="layout_within_display",
                        outcome=short_name,
                        subset_display_count=sdc,
                        subset_layout="",
                        data_level="trial",
                    )
                by_lb = is_._gather_block_error_by_layout_for_dc(bl_sub, fixed_dc)
                emit_descriptives_for_groups(
                    by_lb,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="layout_within_display",
                    outcome="block_error_rate",
                    subset_display_count=sdc,
                    subset_layout="",
                    data_level="block",
                )
                maybe_posthoc_layout(
                    by_lb,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="layout_within_display",
                    outcome="block_error_rate",
                    subset_display_count=sdc,
                    subset_layout="",
                    data_level="block",
                )

            for lay in is_._layouts_in_session(tr_sub):
                for col, short_name in trial_outcomes:
                    v4t, v15t = is_._gather_trial_4_vs_15_for_layout(tr_sub, col, lay)
                    emit_descriptives_for_groups(
                        {"4": v4t, "15": v15t},
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="display_within_layout",
                        outcome=short_name,
                        subset_display_count="",
                        subset_layout=lay,
                        data_level="trial",
                    )
                    maybe_mw_effects(
                        v4t,
                        v15t,
                        study=study,
                        experiment_num=exp_num,
                        analysis_type="display_within_layout",
                        outcome=short_name,
                        subset_display_count="",
                        subset_layout=lay,
                        data_level="trial",
                    )
                v4b2, v15b2 = is_._gather_block_4_vs_15_for_layout(bl_sub, lay)
                emit_descriptives_for_groups(
                    {"4": v4b2, "15": v15b2},
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="display_within_layout",
                    outcome="block_error_rate",
                    subset_display_count="",
                    subset_layout=lay,
                    data_level="block",
                )
                maybe_mw_effects(
                    v4b2,
                    v15b2,
                    study=study,
                    experiment_num=exp_num,
                    analysis_type="display_within_layout",
                    outcome="block_error_rate",
                    subset_display_count="",
                    subset_layout=lay,
                    data_level="block",
                )

    write_csv(tables_dir / "inferential_group_descriptives_shapiro.csv", descriptive_rows)
    write_csv(tables_dir / "inferential_posthoc_layout_pairwise_holm.csv", posthoc_rows)
    write_csv(tables_dir / "inferential_effect_sizes_4_vs_15_cliffs_delta.csv", mw_effect_rows)

    for std in studies:
        sub_d = [r for r in descriptive_rows if str(r.get("study")) == std]
        sub_p = [r for r in posthoc_rows if str(r.get("study")) == std]
        sub_m = [r for r in mw_effect_rows if str(r.get("study")) == std]
        (output_dir / std / "tables").mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / std / "tables" / "inferential_group_descriptives_shapiro.csv", sub_d)
        write_csv(output_dir / std / "tables" / "inferential_posthoc_layout_pairwise_holm.csv", sub_p)
        write_csv(output_dir / std / "tables" / "inferential_effect_sizes_4_vs_15_cliffs_delta.csv", sub_m)

    return {
        "n_companion_descriptive_rows": len(descriptive_rows),
        "n_companion_posthoc_rows": len(posthoc_rows),
        "n_companion_mw_effect_rows": len(mw_effect_rows),
    }
