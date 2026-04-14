"""
Nonparametric inferential tests for layout and display count (SciPy).

Includes:
- **Session omnibus:** pooled layout (Kruskal–Wallis) and 4 vs 15 (Mann–Whitney) per Study×Exp.
- **Layout within display count:** at fixed 4 or 15 displays, compare layouts (Kruskal–Wallis).
- **Display within layout:** at fixed layout, compare 4 vs 15 (Mann–Whitney).

Observations are not independent within participant; exploratory screening — see STATS_README.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .inferential_diagnostics_posthoc import run_companion_outputs
from .inferential_tables_plots import run_tables_and_plots
from .io_tables import missing, write_csv

try:
    from scipy.stats import kruskal, mannwhitneyu

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False
    kruskal = None  # type: ignore
    mannwhitneyu = None  # type: ignore


def _display_bin(v: Any) -> Optional[int]:
    if missing(v):
        return None
    try:
        d = int(round(float(v)))
        if d in (4, 15):
            return d
    except (TypeError, ValueError):
        pass
    return None


def _trial_stratum(
    trials: List[Dict[str, Any]], study: str, experiment_num: int
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for t in trials:
        if str(t.get("study", "")) != study:
            continue
        try:
            if int(t.get("experiment_num", -1)) != experiment_num:
                continue
        except (TypeError, ValueError):
            continue
        out.append(t)
    return out


def _block_stratum(
    blocks: List[Dict[str, Any]], study: str, experiment_num: int
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for b in blocks:
        if str(b.get("study", "")) != study:
            continue
        try:
            if int(b.get("experiment_num", -1)) != experiment_num:
                continue
        except (TypeError, ValueError):
            continue
        out.append(b)
    return out


def _finite_float(x: Any) -> Optional[float]:
    if missing(x):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return v


def _layout_key(row: Dict[str, Any]) -> Optional[str]:
    v = row.get("layout_raw")
    if missing(v) or str(v).strip() == "" or str(v).lower() == "nan":
        return None
    return str(v).strip()


def _block_error_rate_value(b: Dict[str, Any]) -> Optional[float]:
    """Errors per block unit (N selections, or N=1 for swap trials). Legacy default N=5 if missing."""
    err = b.get("errors_wrong_selections")
    if missing(err):
        return None
    try:
        e = int(err)
    except (TypeError, ValueError):
        return None
    denom_v = b.get("block_n_selections")
    if missing(denom_v):
        denom = 5.0
    else:
        try:
            denom = max(1.0, float(denom_v))
        except (TypeError, ValueError):
            denom = 5.0
    return e / denom


def _trial_metric_row(
    t: Dict[str, Any], col: str
) -> Tuple[Optional[float], Optional[str], Optional[int]]:
    y = _finite_float(t.get(col))
    lay = _layout_key(t)
    dc = _display_bin(t.get("display_count"))
    return y, lay, dc


def _layout_test(values_by_layout: Dict[str, List[float]]) -> Tuple[str, float, float, str]:
    groups = {k: v for k, v in values_by_layout.items() if len(v) > 0}
    if len(groups) < 2:
        return "kruskal_wallis", float("nan"), float("nan"), "fewer_than_two_layout_groups"
    samples = [groups[k] for k in sorted(groups.keys(), key=str)]
    if not _HAS_SCIPY:
        return "kruskal_wallis", float("nan"), float("nan"), "scipy_not_installed"
    try:
        stat, p = kruskal(*samples)  # type: ignore[misc]
    except ValueError as e:
        return "kruskal_wallis", float("nan"), float("nan"), f"test_failed:{e}"
    summary = "; ".join(f"{k}_n={len(groups[k])}" for k in sorted(groups.keys(), key=str))
    return "kruskal_wallis", float(stat), float(p), summary


def _display_test(
    vals_four: List[float], vals_fifteen: List[float]
) -> Tuple[str, float, float, str]:
    if not _HAS_SCIPY:
        return "mannwhitney_u", float("nan"), float("nan"), "scipy_not_installed"
    if len(vals_four) == 0 or len(vals_fifteen) == 0:
        return "mannwhitney_u", float("nan"), float("nan"), "missing_4_or_15_group"
    try:
        stat, p = mannwhitneyu(vals_four, vals_fifteen, alternative="two-sided")  # type: ignore[misc]
    except ValueError as e:
        return "mannwhitney_u", float("nan"), float("nan"), f"test_failed:{e}"
    note = f"n_4={len(vals_four)}; n_15={len(vals_fifteen)}"
    return "mannwhitney_u", float(stat), float(p), note


def _gather_trial_outcome(
    rows: List[Dict[str, Any]], col: str
) -> Tuple[Dict[str, List[float]], List[float], List[float]]:
    by_layout: Dict[str, List[float]] = {}
    v4: List[float] = []
    v15: List[float] = []
    for t in rows:
        y, lay, dc = _trial_metric_row(t, col)
        if y is None:
            continue
        if lay is not None:
            by_layout.setdefault(lay, []).append(y)
        if dc == 4:
            v4.append(y)
        elif dc == 15:
            v15.append(y)
    return by_layout, v4, v15


def _gather_trial_by_layout_for_dc(
    rows: List[Dict[str, Any]], col: str, fixed_dc: int
) -> Dict[str, List[float]]:
    by_layout: Dict[str, List[float]] = {}
    for t in rows:
        if _display_bin(t.get("display_count")) != fixed_dc:
            continue
        y, lay, _ = _trial_metric_row(t, col)
        if y is None or lay is None:
            continue
        by_layout.setdefault(lay, []).append(y)
    return by_layout


def _gather_trial_4_vs_15_for_layout(
    rows: List[Dict[str, Any]], col: str, layout: str
) -> Tuple[List[float], List[float]]:
    v4: List[float] = []
    v15: List[float] = []
    for t in rows:
        if _layout_key(t) != layout:
            continue
        y, _, dc = _trial_metric_row(t, col)
        if y is None or dc is None:
            continue
        if dc == 4:
            v4.append(y)
        elif dc == 15:
            v15.append(y)
    return v4, v15


def _gather_block_error_rate(
    rows: List[Dict[str, Any]],
) -> Tuple[Dict[str, List[float]], List[float], List[float]]:
    by_layout: Dict[str, List[float]] = {}
    v4: List[float] = []
    v15: List[float] = []
    for b in rows:
        rate = _block_error_rate_value(b)
        if rate is None:
            continue
        lay = _layout_key(b)
        dc = _display_bin(b.get("display_count"))
        if lay is not None:
            by_layout.setdefault(lay, []).append(rate)
        if dc == 4:
            v4.append(rate)
        elif dc == 15:
            v15.append(rate)
    return by_layout, v4, v15


def _gather_block_error_by_layout_for_dc(
    rows: List[Dict[str, Any]], fixed_dc: int
) -> Dict[str, List[float]]:
    by_layout: Dict[str, List[float]] = {}
    for b in rows:
        if _display_bin(b.get("display_count")) != fixed_dc:
            continue
        rate = _block_error_rate_value(b)
        if rate is None:
            continue
        lay = _layout_key(b)
        if lay is None:
            continue
        by_layout.setdefault(lay, []).append(rate)
    return by_layout


def _gather_block_4_vs_15_for_layout(
    rows: List[Dict[str, Any]], layout: str
) -> Tuple[List[float], List[float]]:
    v4: List[float] = []
    v15: List[float] = []
    for b in rows:
        if _layout_key(b) != layout:
            continue
        dc = _display_bin(b.get("display_count"))
        if dc is None:
            continue
        rate = _block_error_rate_value(b)
        if rate is None:
            continue
        if dc == 4:
            v4.append(rate)
        elif dc == 15:
            v15.append(rate)
    return v4, v15


def _layouts_in_session(rows: List[Dict[str, Any]]) -> List[str]:
    seen: Set[str] = set()
    for t in rows:
        lay = _layout_key(t)
        if lay:
            seen.add(lay)
    return sorted(seen, key=str)


def _append_result(
    out: List[Dict[str, Any]],
    study: str,
    experiment_num: int,
    outcome: str,
    factor: str,
    test_name: str,
    statistic: float,
    p_value: float,
    n_obs: int,
    detail: str,
    *,
    analysis_type: str = "session_omnibus",
    subset_display_count: Optional[int] = None,
    subset_layout: Optional[str] = None,
) -> None:
    sig = ""
    if not math.isnan(p_value):
        sig = "yes" if p_value < 0.05 else "no"
    row: Dict[str, Any] = {
        "study": study,
        "experiment_num": experiment_num,
        "analysis_type": analysis_type,
        "subset_display_count": subset_display_count if subset_display_count is not None else "",
        "subset_layout": subset_layout if subset_layout is not None else "",
        "outcome": outcome,
        "factor": factor,
        "test": test_name,
        "statistic": statistic,
        "p_value": p_value,
        "significant_alpha_0.05": sig,
        "n_observations": n_obs,
        "detail": detail,
    }
    out.append(row)


def run_inferential_analysis(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_directory": str(output_dir.resolve()),
        "scipy_available": _HAS_SCIPY,
        "methods": (
            "session_omnibus: layout (Kruskal–Wallis) and 4 vs 15 (Mann–Whitney) per Study×Exp. "
            "layout_within_display: compare layouts holding display count at 4 or 15. "
            "display_within_layout: compare 4 vs 15 holding layout_fixed. "
            "Trial outcomes for Exp1–2: selection time, TTFF, re-engagement, overlooked samples, "
            "delayed-discovery flag, log process density. Exp3 (swap): completion time only (no TTFF-linked metrics). "
            "Block error rate = errors_wrong_selections / block_n_selections (N selections per Exp1–2 block; 1 per Exp3 trial). "
            "Companions: Shapiro–Wilk per group (exploratory normality screen); "
            "after KW p<0.05, pairwise Mann–Whitney with Holm adjustment; "
            "after MW p<0.05, Cliff delta + median direction for 4 vs 15. "
            "Participant-level: paired Wilcoxon on per-participant medians for 4 vs 15; "
            "two layouts = paired Wilcoxon on layout medians; three or more layouts = Friedman on "
            "complete cases (see inferential_participant_level_tests.csv)."
        ),
    }

    if not _HAS_SCIPY:
        manifest["error"] = "scipy not installed; install with: pip install scipy"
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
                "n_observations": "",
                "detail": "scipy_not_installed_rerun_after_pip_install_scipy",
            }
        ]
        (output_dir / "Study1" / "tables").mkdir(parents=True, exist_ok=True)
        (output_dir / "Study2" / "tables").mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / "Study1" / "tables" / "inferential_tests_long.csv", stub)
        write_csv(output_dir / "Study2" / "tables" / "inferential_tests_long.csv", stub)
        write_csv(tables_dir / "inferential_tests_long.csv", stub)
        stub_pl = [
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
                "detail": "scipy_not_installed_rerun_after_pip_install_scipy",
                "test_level": "participant_median_per_cell",
            }
        ]
        write_csv(tables_dir / "inferential_participant_level_tests.csv", stub_pl)
        write_csv(output_dir / "Study1" / "tables" / "inferential_participant_level_tests.csv", stub_pl)
        write_csv(output_dir / "Study2" / "tables" / "inferential_participant_level_tests.csv", stub_pl)
        (output_dir / "stats_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        readme = Path(__file__).resolve().parent / "report" / "STATS_README.md"
        if readme.is_file():
            (output_dir / "STATS_README.md").write_text(
                readme.read_text(encoding="utf-8"), encoding="utf-8"
            )
        brief_readme = output_dir / "README.md"
        brief_readme.write_text(
            """# Inferential statistics (behavioral logs)

SciPy was **not** installed; **`tables/inferential_tests_long.csv`** contains only a placeholder row.
Install **`scipy`** and re-run with **`--inferential-stats`**.

See **`STATS_README.md`** for methods.
""",
            encoding="utf-8",
        )
        return manifest

    results: List[Dict[str, Any]] = []
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
    # Exp3: swap puzzle — completion time only; TTFF / re-engagement / overlooked not defined in logs.
    trial_outcomes_exp3 = (("selection_time_sec", "time_per_selection"),)

    for study in studies:
        for exp_num in exps:
            trial_outcomes = trial_outcomes_exp3 if exp_num == 3 else trial_outcomes_exp12
            tr_sub = _trial_stratum(trials, study, exp_num)
            bl_sub = _block_stratum(blocks, study, exp_num)

            # --- Session omnibus (same as before, expanded outcomes) ---
            for col, short_name in trial_outcomes:
                by_l, v4, v15 = _gather_trial_outcome(tr_sub, col)
                tn, st, pv, det = _layout_test(by_l)
                n_l = sum(len(v) for v in by_l.values())
                _append_result(
                    results,
                    study,
                    exp_num,
                    short_name,
                    "layout",
                    tn,
                    st,
                    pv,
                    n_l,
                    det,
                    analysis_type="session_omnibus",
                )
                tn, st, pv, det = _display_test(v4, v15)
                n_d = len(v4) + len(v15)
                _append_result(
                    results,
                    study,
                    exp_num,
                    short_name,
                    "display_count_4_vs_15",
                    tn,
                    st,
                    pv,
                    n_d,
                    det,
                    analysis_type="session_omnibus",
                )

            by_l_b, v4b, v15b = _gather_block_error_rate(bl_sub)
            tn, st, pv, det = _layout_test(by_l_b)
            n_lb = sum(len(v) for v in by_l_b.values())
            _append_result(
                results,
                study,
                exp_num,
                "block_error_rate",
                "layout",
                tn,
                st,
                pv,
                n_lb,
                det,
                analysis_type="session_omnibus",
            )
            tn, st, pv, det = _display_test(v4b, v15b)
            n_db = len(v4b) + len(v15b)
            _append_result(
                results,
                study,
                exp_num,
                "block_error_rate",
                "display_count_4_vs_15",
                tn,
                st,
                pv,
                n_db,
                det,
                analysis_type="session_omnibus",
            )

            # --- Layout within fixed display count (4 and 15) ---
            for fixed_dc in (4, 15):
                for col, short_name in trial_outcomes:
                    by_l = _gather_trial_by_layout_for_dc(tr_sub, col, fixed_dc)
                    tn, st, pv, det = _layout_test(by_l)
                    n_l = sum(len(v) for v in by_l.values())
                    _append_result(
                        results,
                        study,
                        exp_num,
                        short_name,
                        "layout",
                        tn,
                        st,
                        pv,
                        n_l,
                        det,
                        analysis_type="layout_within_display",
                        subset_display_count=fixed_dc,
                    )
                by_lb = _gather_block_error_by_layout_for_dc(bl_sub, fixed_dc)
                tn, st, pv, det = _layout_test(by_lb)
                n_lb = sum(len(v) for v in by_lb.values())
                _append_result(
                    results,
                    study,
                    exp_num,
                    "block_error_rate",
                    "layout",
                    tn,
                    st,
                    pv,
                    n_lb,
                    det,
                    analysis_type="layout_within_display",
                    subset_display_count=fixed_dc,
                )

            # --- 4 vs 15 within each layout ---
            for lay in _layouts_in_session(tr_sub):
                for col, short_name in trial_outcomes:
                    v4t, v15t = _gather_trial_4_vs_15_for_layout(tr_sub, col, lay)
                    tn, st, pv, det = _display_test(v4t, v15t)
                    n_d = len(v4t) + len(v15t)
                    _append_result(
                        results,
                        study,
                        exp_num,
                        short_name,
                        "display_count_4_vs_15",
                        tn,
                        st,
                        pv,
                        n_d,
                        det,
                        analysis_type="display_within_layout",
                        subset_layout=lay,
                    )
                v4b2, v15b2 = _gather_block_4_vs_15_for_layout(bl_sub, lay)
                tn, st, pv, det = _display_test(v4b2, v15b2)
                n_db2 = len(v4b2) + len(v15b2)
                _append_result(
                    results,
                    study,
                    exp_num,
                    "block_error_rate",
                    "display_count_4_vs_15",
                    tn,
                    st,
                    pv,
                    n_db2,
                    det,
                    analysis_type="display_within_layout",
                    subset_layout=lay,
                )

    write_csv(tables_dir / "inferential_tests_long.csv", results)
    manifest["n_result_rows"] = len(results)

    for std in studies:
        sub = [r for r in results if str(r.get("study")) == std]
        (output_dir / std / "tables").mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / std / "tables" / "inferential_tests_long.csv", sub)

    companion = run_companion_outputs(trials, blocks, results, output_dir)
    manifest.update(companion)

    from .inferential_participant_level import run_participant_level_inferential

    participant_level = run_participant_level_inferential(trials, blocks, output_dir)
    manifest.update(participant_level)

    extra = run_tables_and_plots(results, output_dir)
    manifest.update(extra)

    (output_dir / "stats_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    readme_src = Path(__file__).resolve().parent / "report" / "STATS_README.md"
    if readme_src.is_file():
        (output_dir / "STATS_README.md").write_text(readme_src.read_text(encoding="utf-8"), encoding="utf-8")

    brief_readme = output_dir / "README.md"
    brief_readme.write_text(
        """# Inferential statistics (behavioral logs)

Output from `run_behavior_logs.py --inferential-stats`. See **`STATS_README.md`**.

**Exp1–3** match **`Study{N}subject{##}Exp{M}`** in `session_logs/` and `VarjoJSONfiles/`: **Exp1** = selection/search, **Exp2** = memory, **Exp3** = puzzle (swap). Charts use this **Exp** prefix consistently.

**Layout:**
- **`Study1/`** and **`Study2/`** — same `tables/` and `figures/` as below, **filtered to that study** (easier thesis chapters per experiment).
- **Root `tables/`** — all studies combined.

**Tables (each location):**
- **`inferential_tests_long.csv`** — all tests with **`analysis_type`**: `session_omnibus`, `layout_within_display`, `display_within_layout`; **`subset_display_count`** / **`subset_layout`** when relevant.
- **`inferential_tests_long_enriched.csv`**, significant extracts, wide session-omnibus pivot, stratified summaries.

**Figures:** session omnibus heatmaps (global + per study); stratified heatmaps for layout-at-fixed-display and display-contrast-at-fixed-layout. Companion bars for **Holm-significant layout pairs** and **Cliff's delta (4 vs 15)** when omnibus tests are significant at **p < 0.05**. Under **`Study1/figures/`** and **`Study2/figures/`**, those companion charts are split **by Exp1–Exp3** (separate PNGs) for readable labels.

**Tables:** see **`STATS_README.md`** for **`inferential_group_descriptives_shapiro.csv`**, **`inferential_posthoc_layout_pairwise_holm.csv`**, **`inferential_effect_sizes_4_vs_15_cliffs_delta.csv`**, and **`inferential_participant_level_tests.csv`** (paired Wilcoxon / Friedman on per-participant medians).

```text
python Assets/OutputLog/run_behavior_logs.py --inferential-stats
```
""",
        encoding="utf-8",
    )

    return manifest
