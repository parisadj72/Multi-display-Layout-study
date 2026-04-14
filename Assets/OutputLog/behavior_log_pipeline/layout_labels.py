"""
Normalize legacy Unity / JSON naming: Curve/Curved -> Cylindrical/cylindrical for reporting.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, MutableMapping, Sequence

# Keys on trial / block dicts that may contain "curve" wording
_TRIAL_KEYS = (
    "layout_raw",
    "condition_name",
    "layout_family",
    "grid_label",
)
_BLOCK_KEYS = ("layout_raw",)


def normalize_curve_terms(s: str) -> str:
    """
    Thesis-facing labels: Curve/Curved→Cylindrical, whole word Stack→Stacked (e.g. 2by2Stack→2by2Stacked).
    """
    if not s or not isinstance(s, str):
        return s
    # Longer tokens first so "Curved" is not turned into "Cylindricald"
    out = (
        s.replace("Curved", "Cylindrical")
        .replace("curved", "cylindrical")
        .replace("Curve", "Cylindrical")
        .replace("curve", "cylindrical")
    )
    # Unity / JSON use "Stack"; thesis layout name is "stacked" (word-boundary safe).
    out = re.sub(r"\bStack\b", "Stacked", out)
    out = re.sub(r"\bstack\b", "stacked", out)
    return out


def normalize_record(rec: MutableMapping[str, Any], keys: Sequence[str]) -> None:
    for k in keys:
        if k in rec and isinstance(rec[k], str):
            rec[k] = normalize_curve_terms(rec[k])


def normalize_trials_and_blocks(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
) -> None:
    for t in trials:
        normalize_record(t, _TRIAL_KEYS)
    for b in blocks:
        normalize_record(b, _BLOCK_KEYS)


def unique_studies(trials: List[Dict[str, Any]]) -> List[str]:
    s = {str(t.get("study", "")).strip() for t in trials if not missing_study(t.get("study"))}
    return sorted(s, key=str)


def studies_for_outputs(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
) -> List[str]:
    """Study labels present in trials, or if none, inferred from blocks."""
    s = set(unique_studies(trials))
    if not s and blocks:
        s = {str(b.get("study", "")).strip() for b in blocks if not missing_study(b.get("study"))}
    return sorted(s, key=str)


def missing_study(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    return False


def filter_by_study(
    rows: List[Dict[str, Any]],
    study: str,
) -> List[Dict[str, Any]]:
    return [r for r in rows if str(r.get("study", "")) == study]
