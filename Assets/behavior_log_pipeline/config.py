"""Paths and thresholds for behavioral log analysis."""

from pathlib import Path
from typing import List

# Package parent = OutputLog
OUTPUT_LOG_DIR = Path(__file__).resolve().parent.parent
# Unity behavioral logs (`Study*subject*Exp*.txt` + `*_overlooked.txt`) live here by default.
SESSION_LOGS_DIR = OUTPUT_LOG_DIR / "session_logs"
VARJO_JSON_DIR = OUTPUT_LOG_DIR / "VarjoJSONfiles"


def default_behavior_log_input_dirs() -> List[Path]:
    """Prefer `session_logs/` when present; otherwise the whole OutputLog tree (legacy layout)."""
    if SESSION_LOGS_DIR.is_dir():
        return [SESSION_LOGS_DIR]
    return [OUTPUT_LOG_DIR]

# Default output root (unique folder for this pipeline)
DEFAULT_OUTPUT_DIR = OUTPUT_LOG_DIR / "behavior_log_analysis_output"

# Optional inferential stats (SciPy); separate from tables/figures output
DEFAULT_STATS_OUTPUT_DIR = OUTPUT_LOG_DIR / "behavior_log_inferential_stats"

# TTFF at or below this is treated as "immediate first look" (report separately from delayed discovery)
TTFF_IMMEDIATE_SEC = 1e-6

# Trials at or above this unity-log TTFF are flagged as delayed discovery (thesis: overlooked / hard-to-find)
DELAYED_TTFF_THRESHOLD_SEC = 0.5

# Figure DPI for publication-style PNGs
FIGURE_DPI = 200
