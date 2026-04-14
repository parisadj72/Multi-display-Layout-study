"""CSV I/O and small helpers (no pandas — avoids broken/shadowed pandas installs)."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def missing(x: Any) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    return False


def read_csv_dicts(path: Path) -> List[Dict[str, Any]]:
    """Load a CSV as a list of row dicts. Returns [] if missing or empty."""
    if not path.is_file():
        return []
    if path.stat().st_size == 0:
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            out = {}
            for k in keys:
                v = r.get(k, "")
                if missing(v):
                    out[k] = ""
                elif isinstance(v, float) and v == int(v) and abs(v) < 1e15:
                    out[k] = int(v)
                else:
                    out[k] = v
            w.writerow(out)


def col_float(rows: Sequence[Dict[str, Any]], name: str) -> List[float]:
    out: List[float] = []
    for r in rows:
        v = r.get(name)
        if missing(v) or v == "":
            out.append(float("nan"))
            continue
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            out.append(float("nan"))
    return out


def col_str(rows: Sequence[Dict[str, Any]], name: str) -> List[str]:
    out = []
    for r in rows:
        v = r.get(name)
        if missing(v) or v == "":
            out.append("")
        else:
            out.append(str(v))
    return out


def median(xs: List[float]) -> float:
    s = [x for x in xs if not math.isnan(x)]
    if not s:
        return float("nan")
    s.sort()
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return float(0.5 * (s[mid - 1] + s[mid]))


def mean(xs: List[float]) -> float:
    s = [x for x in xs if not math.isnan(x)]
    if not s:
        return float("nan")
    return float(sum(s) / len(s))


def q90(xs: List[float]) -> float:
    s = sorted(x for x in xs if not math.isnan(x))
    if not s:
        return float("nan")
    if len(s) == 1:
        return float(s[0])
    pos = 0.9 * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    return float(s[lo] + (s[hi] - s[lo]) * (pos - lo))


def group_keys(rows: List[Dict[str, Any]], key_names: List[str]) -> Dict[Tuple, List[Dict[str, Any]]]:
    from collections import defaultdict

    def _kp(v: Any) -> Any:
        if missing(v):
            return ""
        return v

    g: Dict[Tuple, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        key = tuple(_kp(r.get(k)) for k in key_names)
        g[key].append(r)
    return dict(g)
