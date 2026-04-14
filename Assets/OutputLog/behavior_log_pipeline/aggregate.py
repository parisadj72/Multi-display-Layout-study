"""Summaries for thesis tables (no pandas)."""

from __future__ import annotations

import math
from typing import Any, Dict, List

from . import config
from .io_tables import col_float, group_keys, mean, median, missing, q90

_NAN = float("nan")


def add_derived_trial_flags(trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for t in trials:
        ttff = t.get("unity_ttff_sec", _NAN)
        try:
            ft = float(ttff)
        except (TypeError, ValueError):
            ft = _NAN
        t["ttff_immediate_flag"] = 1.0 if (not math.isnan(ft) and ft <= config.TTFF_IMMEDIATE_SEC) else 0.0
        t["delayed_discovery_flag"] = 1.0 if (not math.isnan(ft) and ft >= config.DELAYED_TTFF_THRESHOLD_SEC) else 0.0
        proc = t.get("overlooked_view_sample_count", _NAN)
        try:
            pc = float(proc)
        except (TypeError, ValueError):
            pc = _NAN
        if not math.isnan(ft) and not math.isnan(pc) and ft > 0:
            t["log_process_density"] = pc / ft
        else:
            t["log_process_density"] = _NAN
    return trials


def has_any_condition_name(trials: List[Dict[str, Any]]) -> bool:
    for t in trials:
        c = t.get("condition_name", "")
        if c is not None and str(c).strip() != "":
            return True
    return False


def summarize_by_condition(trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not trials:
        return []
    key_names = (
        ["study", "condition_name"] if has_any_condition_name(trials) else ["study", "layout_raw"]
    )
    groups = group_keys(trials, key_names)
    out: List[Dict[str, Any]] = []
    for key, grp in sorted(groups.items(), key=lambda x: x[0]):
        ttff = col_float(grp, "unity_ttff_sec")
        sel = col_float(grp, "selection_time_sec")
        del_f = col_float(grp, "delayed_discovery_flag")
        imm = col_float(grp, "ttff_immediate_flag")
        proc = col_float(grp, "overlooked_view_sample_count")
        reeng = col_float(grp, "reengagement_after_overlook_sec")
        row = {
            key_names[0]: key[0],
            key_names[1]: key[1],
            "n_trials": len(grp),
            "ttff_mean": mean(ttff),
            "ttff_median": median(ttff),
            "ttff_q90": q90(ttff),
            "selection_time_mean": mean(sel),
            "delayed_discovery_rate": mean(del_f),
            "immediate_ttff_rate": mean(imm),
            "process_samples_mean": mean(proc),
            "reengagement_after_overlook_mean": mean(reeng),
            "reengagement_after_overlook_median": median(reeng),
        }
        out.append(row)
    return out


def has_any_display_count(trials: List[Dict[str, Any]]) -> bool:
    for t in trials:
        v = t.get("display_count")
        if not missing(v):
            try:
                float(v)
                if not math.isnan(float(v)):
                    return True
            except (TypeError, ValueError):
                pass
    return False


def summarize_by_display_count(trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not trials or not has_any_display_count(trials):
        return []
    filt = [t for t in trials if not missing(t.get("display_count"))]
    groups = group_keys(filt, ["study", "display_count"])
    out: List[Dict[str, Any]] = []
    for key, grp in sorted(groups.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        ttff = col_float(grp, "unity_ttff_sec")
        sel = col_float(grp, "selection_time_sec")
        del_f = col_float(grp, "delayed_discovery_flag")
        reeng = col_float(grp, "reengagement_after_overlook_sec")
        out.append(
            {
                "study": key[0],
                "display_count": key[1],
                "n_trials": len(grp),
                "ttff_median": median(ttff),
                "delayed_discovery_rate": mean(del_f),
                "selection_time_mean": mean(sel),
                "reengagement_after_overlook_median": median(reeng),
            }
        )
    return out


def summarize_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not blocks:
        return []
    groups = group_keys(blocks, ["study", "layout_raw"])
    out: List[Dict[str, Any]] = []
    for key, grp in sorted(groups.items(), key=lambda x: x[0]):
        times = col_float(grp, "time_per_5_selections_sec")
        errs = col_float(grp, "errors_wrong_selections")
        errs_clean = [e for e in errs if not math.isnan(e)]
        out.append(
            {
                "study": key[0],
                "layout_raw": key[1],
                "n_blocks": len(grp),
                "mean_time_5_selections": mean(times),
                "total_errors": float(sum(errs_clean)) if errs_clean else 0.0,
                "mean_errors_per_block": mean(errs),
            }
        )
    return out


def participant_level_table(trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not trials:
        return []
    groups = group_keys(trials, ["study", "subject_id", "experiment_num"])
    out: List[Dict[str, Any]] = []
    for key, grp in sorted(groups.items(), key=lambda x: x[0]):
        ttff = col_float(grp, "unity_ttff_sec")
        del_f = col_float(grp, "delayed_discovery_flag")
        proc = col_float(grp, "overlooked_view_sample_count")
        reeng = col_float(grp, "reengagement_after_overlook_sec")
        out.append(
            {
                "study": key[0],
                "subject_id": key[1],
                "experiment_num": key[2],
                "n_trials": len(grp),
                "ttff_median": median(ttff),
                "delayed_rate": mean(del_f),
                "mean_process_samples": mean(proc),
                "median_reengagement_after_overlook": median(reeng),
            }
        )
    return out
