"""
Parse Unity session logs (Study*subject*Exp*.txt and *_overlooked.txt; default folder: session_logs/).

Uses list[dict] rows only (no pandas) so a broken site-packages pandas cannot break this pipeline.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .io_tables import missing

TTFF_RE = re.compile(
    r"View\s+looked\s+at\s+in\s+([\d.]+)\s+seconds\s+for\s+the\s+first\s+time",
    re.IGNORECASE,
)
SEL_RE = re.compile(r"Time\s+per\s+selection\s*=\s*([\d.]+)", re.IGNORECASE)
BLOCK_TIME_RE = re.compile(
    r"\(\s*time\s+per\s+(\d+)\s+Selections\s+for\s+the\s+(.+?)\s+layout\s*\)\s*:\s*([\d.]+)",
    re.IGNORECASE,
)
BLOCK_ERR_RE = re.compile(
    r"\(\s*Errors\s*/\s*Wrong\s+Selections\s+per\s+(\d+)\s+Selections\s+for\s+the\s+(.+?)\s+layout\s*\)\s*:\s*(\d+)",
    re.IGNORECASE,
)

# Overlooked log: two Unity formats — short "View looked at in …" or long "… was looked at in …"
FIRST_TIME_ANY_RE = re.compile(
    r"(?:View\s+looked\s+at|was\s+looked\s+at)\s+in\s+([\d.]+)\s+seconds?\s+for\s+the\s+first\s+time",
    re.IGNORECASE,
)
VIEW_SAMPLE_RE = re.compile(r"View\s+looked\s+at\s+in\s+([\d.]+)\s*sec\s*!", re.IGNORECASE)

_NAN = float("nan")


@dataclass
class ParseWarning:
    message: str
    source_file: str = ""


def parse_stem(path: Path) -> Tuple[str, int, int]:
    stem = path.stem.replace("_overlooked", "")
    m = re.match(r"(Study\d+)subject(\d+)Exp(\d+)$", stem, re.IGNORECASE)
    if not m:
        raise ValueError(f"Filename does not match Study*subject*Exp*: {path.name}")
    return m.group(1), int(m.group(2)), int(m.group(3))


def condition_json_stem(study: str, subject_id: int, exp_num: int) -> str:
    """Stem for Varjo condition JSON, aligned with Unity logs (zero-padded subject id)."""
    return f"{study}subject{int(subject_id):02d}Exp{int(exp_num)}"


def guess_condition_json_path(
    study: str, subject_id: int, exp_num: int, json_dir: Optional[Path] = None
) -> Path:
    from . import config

    base = Path(json_dir) if json_dir is not None else config.VARJO_JSON_DIR
    return base / f"{condition_json_stem(study, subject_id, exp_num)}.json"


def condition_json_candidate_paths(
    study: str, subject_id: int, exp_num: int, json_dir: Path
) -> List[Path]:
    """Condition JSON files to try (block order must match Unity). Exp3: Exp3→Exp2→Exp1 fallbacks."""
    if exp_num == 3:
        return [
            json_dir / f"{condition_json_stem(study, subject_id, 3)}.json",
            json_dir / f"{condition_json_stem(study, subject_id, 2)}.json",
            json_dir / f"{condition_json_stem(study, subject_id, 1)}.json",
        ]
    return [json_dir / f"{condition_json_stem(study, subject_id, exp_num)}.json"]


def _condition_order_usable(order: Optional[List[str]]) -> bool:
    if not order:
        return False
    return any(str(x).strip() for x in order)


def resolve_condition_order(
    study: str, subject_id: int, exp_num: int, json_dir: Optional[Path] = None
) -> Tuple[Optional[List[str]], Path, List[str]]:
    """
    Load condition labels for enrich_trials_with_conditions.

    Exp3 normally expects ``StudyNsubject##Exp3.json``. If missing or empty, we try Exp2 then Exp1
    for the same study/subject so ``display_count`` (4 vs 15) can still be filled when block order
    matches those sessions.
    """
    from . import config

    base = Path(json_dir) if json_dir is not None else config.VARJO_JSON_DIR
    paths = condition_json_candidate_paths(study, subject_id, exp_num, base)
    primary = paths[0]
    notes: List[str] = []
    for p in paths:
        if not p.is_file():
            continue
        order = load_condition_order(p)
        if not _condition_order_usable(order):
            continue
        if p.resolve() != primary.resolve():
            notes.append(
                f"Exp{exp_num}: using condition order from {p.name} ({primary.name} missing or has no usable conditions). "
                f"Add {condition_json_stem(study, subject_id, 3)}.json if session 3 counterbalancing differs."
            )
        return order, p, notes
    parts = [
        f"{p.name} ({'missing' if not p.is_file() else 'no usable conditions'})" for p in paths
    ]
    notes.append(
        "No condition JSON for enrichment: " + "; ".join(parts) + ". display_count will be empty."
    )
    return None, primary, notes


def load_condition_order(json_path: Path) -> Optional[List[str]]:
    if not json_path.is_file():
        return None
    import json

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    conds = data.get("conditions") or []
    return [c.get("condition", "") for c in conds if isinstance(c, dict)]


def condition_name_to_features(name: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "condition_name": name,
        "display_count": _NAN,
        "grid_label": "",
        "layout_family": "",
    }
    if not name:
        return out
    lower = name.lower()
    if "2by2" in lower or lower.startswith("2by2"):
        out["display_count"] = 4
        out["grid_label"] = "2x2 (4 displays)"
    elif "3by5" in lower or lower.startswith("3by5"):
        out["display_count"] = 15
        out["grid_label"] = "3x5 (15 displays)"
    if "flat" in lower:
        out["layout_family"] = "flat"
    elif "stack" in lower:
        out["layout_family"] = "stacked"
    elif "sphere" in lower:
        out["layout_family"] = "spherical"
    elif "cylindrical" in lower or "curve" in lower:
        out["layout_family"] = "cylindrical"
    return out


def _parse_main_session_exp3_swap(path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[ParseWarning]]:
    """
    Exp3: swap puzzle — per-swap lines, then ``Trial time (# N swaps for the … layout):`` and
    ``Errors per trial for the … layout:``. One trial per block; no TTFF.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    study, subject_id, exp_num = parse_stem(path)
    warnings: List[ParseWarning] = []
    trials: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    pending_swaps: List[float] = []

    swap_re = re.compile(
        r"Time\s+per\s+swap\s+for\s+the\s+(.+?)\s+layout\s*=\s*([\d.]+)",
        re.IGNORECASE,
    )
    trial_time_re = re.compile(
        r"Trial\s+time\s*\(\s*#\s*(\d+)\s+swaps\s+for\s+the\s+(.+?)\s+layout\s*\)\s*:\s*([\d.]+)",
        re.IGNORECASE,
    )
    err_re = re.compile(
        r"Errors\s+per\s+trial\s+for\s+the\s+(.+?)\s+layout\s*:\s*(\d+)",
        re.IGNORECASE,
    )

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = swap_re.search(line)
        if m:
            pending_swaps.append(float(m.group(2)))
            continue
        m = trial_time_re.search(line)
        if m:
            n_sw = int(m.group(1))
            layout_raw = m.group(2).strip()
            total_t = float(m.group(3))
            if pending_swaps and len(pending_swaps) != n_sw:
                warnings.append(
                    ParseWarning(
                        f"Swap line count ({len(pending_swaps)}) != trial header N={n_sw} "
                        f"({layout_raw}); mean_time_per_swap may be partial.",
                        path.name,
                    )
                )
            mean_sw = float(np.mean(pending_swaps)) if pending_swaps else _NAN
            ti = len(trials)
            bidx = len(blocks)
            trials.append(
                {
                    "study": study,
                    "subject_id": subject_id,
                    "experiment_num": exp_num,
                    "source_file": path.name,
                    "trial_within_session": ti,
                    "unity_ttff_sec": _NAN,
                    "selection_time_sec": total_t,
                    "selection_time_line_count": n_sw,
                    "layout_raw": layout_raw,
                    "block_index": bidx,
                    "swap_count_in_trial": n_sw,
                    "mean_time_per_swap_sec": mean_sw,
                    "trial_swap_errors": _NAN,
                }
            )
            pending_swaps = []
            blocks.append(
                {
                    "study": study,
                    "subject_id": subject_id,
                    "experiment_num": exp_num,
                    "source_file": path.name,
                    "block_index": bidx,
                    "layout_raw": layout_raw,
                    "time_per_5_selections_sec": total_t,
                    "errors_wrong_selections": _NAN,
                    "block_n_selections": 1,
                    "trial_start_index": ti,
                    "trial_end_index": ti,
                }
            )
            continue
        m = err_re.search(line)
        if m:
            lay_err = m.group(1).strip()
            err_n = int(m.group(2))
            if not trials or not blocks:
                warnings.append(
                    ParseWarning(f"Errors line without preceding trial: {line}", path.name)
                )
                continue
            trials[-1]["trial_swap_errors"] = err_n
            blocks[-1]["errors_wrong_selections"] = err_n
            br_lay = str(blocks[-1].get("layout_raw", "")).strip()
            if br_lay and lay_err != br_lay:
                warnings.append(
                    ParseWarning(
                        f"Errors layout ({lay_err}) != trial layout ({br_lay})", path.name
                    )
                )
            continue

    for i, t in enumerate(trials):
        t["trial_within_session"] = i
    return trials, blocks, warnings


def parse_main_session_txt(path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[ParseWarning]]:
    study, subject_id, exp_num = parse_stem(path)
    if exp_num == 3:
        return _parse_main_session_exp3_swap(path)

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    warnings: List[ParseWarning] = []
    trials: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []

    pending_ttff: Optional[float] = None
    pending_sels: List[float] = []

    def flush_trial() -> None:
        nonlocal pending_ttff, pending_sels
        if pending_ttff is None and not pending_sels:
            return
        sel_last = pending_sels[-1] if pending_sels else _NAN
        trials.append(
            {
                "study": study,
                "subject_id": subject_id,
                "experiment_num": exp_num,
                "source_file": path.name,
                "trial_within_session": len(trials),
                "unity_ttff_sec": pending_ttff if pending_ttff is not None else _NAN,
                "selection_time_sec": sel_last,
                "selection_time_line_count": len(pending_sels),
                "layout_raw": _NAN,
                "block_index": _NAN,
            }
        )
        pending_ttff = None
        pending_sels = []

    pending_block: Optional[Dict[str, Any]] = None

    def close_open_block() -> None:
        nonlocal pending_block
        if pending_block:
            blocks.append(pending_block)
            pending_block = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = TTFF_RE.search(line)
        if m:
            flush_trial()
            pending_ttff = float(m.group(1))
            continue
        m = SEL_RE.search(line)
        if m:
            v = float(m.group(1))
            if pending_ttff is None:
                warnings.append(
                    ParseWarning(
                        f"Time per selection without preceding TTFF line ({v}); trial indexed with missing TTFF.",
                        path.name,
                    )
                )
                trials.append(
                    {
                        "study": study,
                        "subject_id": subject_id,
                        "experiment_num": exp_num,
                        "source_file": path.name,
                        "trial_within_session": len(trials),
                        "unity_ttff_sec": _NAN,
                        "selection_time_sec": v,
                        "selection_time_line_count": 1,
                        "layout_raw": _NAN,
                        "block_index": _NAN,
                    }
                )
            else:
                pending_sels.append(v)
            continue
        m = BLOCK_TIME_RE.search(line)
        if m:
            close_open_block()
            flush_trial()
            n_sel = int(m.group(1))
            layout_raw = m.group(2).strip()
            block_total = float(m.group(3))
            pending_block = {
                "study": study,
                "subject_id": subject_id,
                "experiment_num": exp_num,
                "source_file": path.name,
                "block_index": len(blocks),
                "layout_raw": layout_raw,
                "time_per_5_selections_sec": block_total,
                "errors_wrong_selections": _NAN,
                "block_n_selections": n_sel,
                "trial_start_index": max(0, len(trials) - n_sel),
                "trial_end_index": len(trials) - 1,
            }
            continue
        m = BLOCK_ERR_RE.search(line)
        if m:
            n_err_line = int(m.group(1))
            layout_err = m.group(2).strip()
            err_n = int(m.group(3))
            if pending_block is not None and int(pending_block["block_index"]) == len(blocks):
                pb_n = int(pending_block.get("block_n_selections", n_err_line))
                if pb_n != n_err_line:
                    warnings.append(
                        ParseWarning(
                            f"Block N mismatch: time line N={pb_n} vs errors line N={n_err_line}",
                            path.name,
                        )
                    )
                pending_block["errors_wrong_selections"] = err_n
                blocks.append(pending_block)
                pending_block = None
            else:
                blocks.append(
                    {
                        "study": study,
                        "subject_id": subject_id,
                        "experiment_num": exp_num,
                        "source_file": path.name,
                        "block_index": len(blocks),
                        "layout_raw": layout_err,
                        "time_per_5_selections_sec": _NAN,
                        "errors_wrong_selections": err_n,
                        "block_n_selections": n_err_line,
                        "trial_start_index": _NAN,
                        "trial_end_index": _NAN,
                    }
                )
            continue

    flush_trial()
    close_open_block()

    for br in blocks:
        ts, te = br.get("trial_start_index"), br.get("trial_end_index")
        if missing(ts) or missing(te):
            continue
        ts_i, te_i = int(ts), int(te)
        for pos_idx in range(ts_i, te_i + 1):
            if 0 <= pos_idx < len(trials):
                trials[pos_idx]["block_index"] = int(br["block_index"])
                trials[pos_idx]["layout_raw"] = br["layout_raw"]

    for i, t in enumerate(trials):
        t["trial_within_session"] = i

    return trials, blocks, warnings


def parse_overlooked_txt(path: Path) -> Tuple[List[Dict[str, Any]], List[ParseWarning]]:
    """
    Each ``for the first time`` line aligns with one main-log trial.

    - ``unity_ttff_sec_overlooked_file``: time (s) until the target view was first acquired.
    - ``overlooked_view_sample_count``: count of ``View looked at in … sec!`` samples **after**
      that milestone and before the next trial’s milestone (intermediate views, e.g. non-targets,
      before looking back and completing selection).
    - ``overlooked_last_view_sample_sec``: timestamp on the **last** such sample before the next trial.
    """
    study, subject_id, exp_num = parse_stem(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    warnings: List[ParseWarning] = []

    matches = list(FIRST_TIME_ANY_RE.finditer(text))
    if not matches:
        warnings.append(ParseWarning("No 'for the first time' markers found.", path.name))
        return [], warnings

    rows: List[Dict[str, Any]] = []
    for i, m in enumerate(matches):
        ft = float(m.group(1))
        post_start = m.end()
        post_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        post_chunk = text[post_start:post_end]
        sample_vals = [float(x) for x in VIEW_SAMPLE_RE.findall(post_chunk)]
        last_sample = float(sample_vals[-1]) if sample_vals else _NAN
        span = float(np.ptp(sample_vals)) if len(sample_vals) > 1 else 0.0
        rows.append(
            {
                "study": study,
                "subject_id": subject_id,
                "experiment_num": exp_num,
                "trial_within_session": i,
                "overlooked_view_sample_count": len(sample_vals),
                "overlooked_last_view_sample_sec": last_sample,
                "overlooked_view_time_span_sec": span,
                "unity_ttff_sec_overlooked_file": ft,
            }
        )

    return rows, warnings


def enrich_trials_with_conditions(
    trials: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    condition_order: Optional[List[str]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    for t in trials:
        t["condition_name"] = ""
        t["display_count"] = _NAN
        t["grid_label"] = ""
        t["layout_family"] = ""
    for b in blocks:
        b["condition_name"] = ""
        b["display_count"] = _NAN
        b["grid_label"] = ""
        b["layout_family"] = ""

    if not condition_order or not blocks:
        return trials, blocks

    sorted_blocks = sorted(blocks, key=lambda x: int(x["block_index"]))
    for bi, br in enumerate(sorted_blocks):
        if bi >= len(condition_order):
            break
        cname = condition_order[bi]
        feats = condition_name_to_features(cname)
        bidx = int(br["block_index"])
        br["condition_name"] = cname
        br["display_count"] = feats["display_count"]
        br["grid_label"] = feats["grid_label"]
        br["layout_family"] = feats["layout_family"]
        for t in trials:
            if not missing(t.get("block_index")) and int(t["block_index"]) == bidx:
                t["condition_name"] = cname
                t["display_count"] = feats["display_count"]
                t["grid_label"] = feats["grid_label"]
                t["layout_family"] = feats["layout_family"]

    return trials, blocks


def merge_trial_and_overlooked(
    trials: List[Dict[str, Any]],
    overlooked: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not trials:
        return trials
    key_names = ("study", "subject_id", "experiment_num", "trial_within_session")

    def key(r: Dict[str, Any]) -> Tuple:
        return tuple(r[k] for k in key_names)

    ov_map = {key(r): r for r in overlooked}
    for t in trials:
        ov = ov_map.get(key(t))
        if ov is None:
            t["overlooked_view_sample_count"] = _NAN
            t["overlooked_view_time_span_sec"] = _NAN
            t["overlooked_last_view_sample_sec"] = _NAN
            t["unity_ttff_sec_overlooked_file"] = _NAN
            t["ttff_main_vs_overlooked_abs_diff"] = _NAN
            t["reengagement_after_overlook_sec"] = _NAN
            continue
        t["overlooked_view_sample_count"] = ov.get("overlooked_view_sample_count", _NAN)
        t["overlooked_view_time_span_sec"] = ov.get("overlooked_view_time_span_sec", _NAN)
        t["overlooked_last_view_sample_sec"] = ov.get("overlooked_last_view_sample_sec", _NAN)
        t["unity_ttff_sec_overlooked_file"] = ov.get("unity_ttff_sec_overlooked_file", _NAN)
        a = t.get("unity_ttff_sec", _NAN)
        b = t.get("unity_ttff_sec_overlooked_file", _NAN)
        try:
            fa = float(a)
            fb = float(b)
            if not math.isnan(fa) and not math.isnan(fb):
                t["ttff_main_vs_overlooked_abs_diff"] = abs(fa - fb)
            else:
                t["ttff_main_vs_overlooked_abs_diff"] = _NAN
        except (TypeError, ValueError):
            t["ttff_main_vs_overlooked_abs_diff"] = _NAN
        st = t.get("selection_time_sec", _NAN)
        last_v = t.get("overlooked_last_view_sample_sec", _NAN)
        try:
            fst = float(st)
            flast = float(last_v)
            if not math.isnan(fst) and not math.isnan(flast) and fst + 1e-9 >= flast:
                t["reengagement_after_overlook_sec"] = fst - flast
            else:
                t["reengagement_after_overlook_sec"] = _NAN
        except (TypeError, ValueError):
            t["reengagement_after_overlook_sec"] = _NAN
    return trials
