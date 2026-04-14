"""
Batch-parse Unity Study*subject*Exp*.txt and *_overlooked.txt (default folder: session_logs under OutputLog);
write tables, figures, and manifest.

Does not use pandas (tables are list[dict] + csv module) so broken pandas installs still produce CSVs.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config
from .aggregate import (
    add_derived_trial_flags,
    has_any_condition_name,
    participant_level_table,
    summarize_blocks,
    summarize_by_condition,
    summarize_by_display_count,
)
from .inferential_stats import run_inferential_analysis
from .io_tables import missing, write_csv
from .layout_labels import (
    filter_by_study,
    normalize_trials_and_blocks,
    studies_for_outputs,
)
from .parse_unity_logs import (
    ParseWarning,
    enrich_trials_with_conditions,
    merge_trial_and_overlooked,
    parse_main_session_txt,
    parse_overlooked_txt,
    parse_stem,
    resolve_condition_order,
)
from .visualizations import (
    plot_delayed_discovery_rate,
    plot_errors_by_layout,
    plot_errors_by_layout_block,
    plot_metric_boxplot_by_group,
    plot_process_samples_vs_ttff,
    plot_reengagement_vs_overlook_sample_count,
    plot_ttff_by_group,
    plot_ttff_ecdf_by_study,
    plot_ttff_ecdf_single_study,
)


def _dedupe_paths(paths: List[Path]) -> List[Path]:
    def key(p: Path) -> tuple:
        s = str(p).replace("\\", "/")
        my = 1 if "my data" in s.lower() else 0
        return (my, len(s), s)

    by_name = {}
    for p in sorted(paths, key=key):
        by_name.setdefault(p.name, p)
    return list(by_name.values())


def _discover_main_logs(input_dirs: List[Path], exclude_pilot: bool) -> List[Path]:
    found: List[Path] = []
    for d in input_dirs:
        if not d.is_dir():
            continue
        for p in d.rglob("Study*subject*Exp*.txt"):
            if "_overlooked" in p.stem:
                continue
            if exclude_pilot and "pilot" in str(p).lower():
                continue
            found.append(p.resolve())
    return _dedupe_paths(found)


def _overlooked_for_main(main_path: Path) -> Path:
    return main_path.with_name(main_path.stem + "_overlooked.txt")


def _copy_rationale_template(dest_dir: Path) -> None:
    pkg = Path(__file__).resolve().parent / "report"
    src = pkg / "thesis_rationale_appendix.md"
    if src.is_file():
        dest = dest_dir / "thesis_rationale_appendix.md"
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _copy_user_guide(dest_dir: Path) -> None:
    pkg = Path(__file__).resolve().parent / "USER_GUIDE.md"
    if pkg.is_file():
        dest = dest_dir / "USER_GUIDE.md"
        dest.write_text(pkg.read_text(encoding="utf-8"), encoding="utf-8")


def run(
    input_dirs: Optional[List[Path]] = None,
    output_dir: Optional[Path] = None,
    exclude_pilot: bool = True,
    skip_figures: bool = False,
    condition_json_dir: Optional[Path] = None,
    inferential_stats: bool = False,
    stats_output_dir: Optional[Path] = None,
) -> dict:
    input_dirs = input_dirs or config.default_behavior_log_input_dirs()
    output_dir = Path(output_dir or config.DEFAULT_OUTPUT_DIR)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    main_logs = _discover_main_logs(input_dirs, exclude_pilot=exclude_pilot)
    all_trials: List[Dict[str, Any]] = []
    all_blocks: List[Dict[str, Any]] = []
    all_warnings: List[ParseWarning] = []
    figure_errors: List[str] = []

    for main_p in sorted(main_logs, key=lambda x: str(x).lower()):
        try:
            trials, blocks, w1 = parse_main_session_txt(main_p)
        except ValueError as e:
            all_warnings.append(ParseWarning(str(e), main_p.name))
            continue
        all_warnings.extend(w1)

        study, subject_id, exp_num = parse_stem(main_p)
        order, _json_used, resolve_notes = resolve_condition_order(
            study, subject_id, exp_num, json_dir=condition_json_dir
        )
        for note in resolve_notes:
            all_warnings.append(ParseWarning(note, main_p.name))
        if order is None:
            # resolve_condition_order already appended a summary note when all candidates fail
            pass
        trials, blocks = enrich_trials_with_conditions(trials, blocks, order)

        ov_path = _overlooked_for_main(main_p)
        if exp_num == 3:
            trials = merge_trial_and_overlooked(trials, [])
        elif ov_path.is_file():
            ov_rows, w2 = parse_overlooked_txt(ov_path)
            all_warnings.extend(w2)
            if len(ov_rows) != len(trials):
                all_warnings.append(
                    ParseWarning(
                        f"Overlooked 'first time' count ({len(ov_rows)}) != main log trials ({len(trials)}); "
                        "merge by trial index may misalign.",
                        main_p.name,
                    )
                )
            trials = merge_trial_and_overlooked(trials, ov_rows)
        else:
            trials = merge_trial_and_overlooked(trials, [])
            all_warnings.append(ParseWarning(f"Missing overlooked companion: {ov_path.name}", main_p.name))

        all_trials.extend(trials)
        all_blocks.extend(blocks)

    trials_full = all_trials
    blocks_full = all_blocks

    normalize_trials_and_blocks(trials_full, blocks_full)

    if trials_full:
        trials_full = add_derived_trial_flags(trials_full)

    write_csv(tables_dir / "trials_long.csv", trials_full)
    write_csv(tables_dir / "blocks_summary.csv", blocks_full)

    if trials_full:
        write_csv(tables_dir / "aggregate_by_condition.csv", summarize_by_condition(trials_full))
        write_csv(tables_dir / "aggregate_by_display_count.csv", summarize_by_display_count(trials_full))
        write_csv(tables_dir / "aggregate_by_participant.csv", participant_level_table(trials_full))
    if blocks_full:
        write_csv(tables_dir / "aggregate_errors_by_layout_raw.csv", summarize_blocks(blocks_full))

    if not skip_figures and trials_full:
        try:
            plot_ttff_ecdf_by_study(
                trials_full, figures_dir / "ttff_ecdf_by_study.png", dpi=config.FIGURE_DPI
            )
            for study in studies_for_outputs(trials_full, blocks_full):
                t_sub = filter_by_study(trials_full, study)
                b_sub = filter_by_study(blocks_full, study)
                subdir = figures_dir / study
                plot_ttff_ecdf_single_study(
                    t_sub,
                    subdir / "ttff_ecdf.png",
                    study,
                    dpi=config.FIGURE_DPI,
                )
                plot_process_samples_vs_ttff(
                    t_sub,
                    subdir / "process_samples_vs_ttff.png",
                    dpi=config.FIGURE_DPI,
                )
                if has_any_condition_name(t_sub):
                    plot_ttff_by_group(
                        t_sub,
                        subdir / "ttff_boxplot_by_condition.png",
                        "condition_name",
                        f"{study}: time to first view by condition",
                        dpi=config.FIGURE_DPI,
                    )
                    plot_delayed_discovery_rate(
                        t_sub,
                        subdir / "delayed_discovery_rate_by_condition.png",
                        "condition_name",
                        f"{study}: delayed discovery (TTFF ≥ {config.DELAYED_TTFF_THRESHOLD_SEC} s) by condition",
                        dpi=config.FIGURE_DPI,
                    )
                td = [t for t in t_sub if not missing(t.get("display_count"))]
                if td:
                    plot_ttff_by_group(
                        td,
                        subdir / "ttff_boxplot_by_display_count.png",
                        "display_count",
                        f"{study}: time to first view by display count (4 vs 15)",
                        dpi=config.FIGURE_DPI,
                    )
                    plot_delayed_discovery_rate(
                        td,
                        subdir / "delayed_discovery_rate_by_display_count.png",
                        "display_count",
                        f"{study}: delayed discovery rate by display count",
                        dpi=config.FIGURE_DPI,
                    )
                    plot_metric_boxplot_by_group(
                        td,
                        subdir / "reengagement_boxplot_by_display_count.png",
                        "display_count",
                        "reengagement_after_overlook_sec",
                        f"{study}: re-engagement after intermediate views (4 vs 15 displays)",
                        "Re-engagement time (s)\nselection time − last intermediate view sample",
                        dpi=config.FIGURE_DPI,
                    )
                plot_ttff_by_group(
                    t_sub,
                    subdir / "ttff_boxplot_by_layout.png",
                    "layout_raw",
                    f"{study}: time to first view by layout (Flat / Cylindrical / Stacked or Spherical)",
                    dpi=config.FIGURE_DPI,
                )
                plot_metric_boxplot_by_group(
                    t_sub,
                    subdir / "reengagement_boxplot_by_layout.png",
                    "layout_raw",
                    "reengagement_after_overlook_sec",
                    f"{study}: re-engagement after intermediate views (by layout)",
                    "Re-engagement time (s)\nselection time − last intermediate view sample",
                    dpi=config.FIGURE_DPI,
                )
                plot_reengagement_vs_overlook_sample_count(
                    t_sub,
                    subdir / "reengagement_vs_intermediate_view_count.png",
                    f"{study}: re-engagement vs number of intermediate views",
                    dpi=config.FIGURE_DPI,
                )
        except Exception as e:
            figure_errors.append(f"trials figures: {e}")

    if not skip_figures and blocks_full:
        try:
            plot_errors_by_layout_block(
                blocks_full, figures_dir / "errors_total_by_study_layout.png", dpi=config.FIGURE_DPI
            )
            for study in studies_for_outputs(trials_full, blocks_full):
                b_sub = filter_by_study(blocks_full, study)
                plot_errors_by_layout(
                    b_sub,
                    figures_dir / study / "errors_by_layout.png",
                    f"{study}: total wrong selections by layout",
                    dpi=config.FIGURE_DPI,
                )
        except Exception as e:
            figure_errors.append(f"block figures: {e}")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_directories": [str(p.resolve()) for p in input_dirs],
        "condition_json_dir": str(Path(condition_json_dir).resolve()) if condition_json_dir else None,
        "output_directory": str(output_dir.resolve()),
        "main_log_files_parsed": len(main_logs),
        "trial_rows": len(trials_full),
        "block_rows": len(blocks_full),
        "delayed_ttff_threshold_sec": config.DELAYED_TTFF_THRESHOLD_SEC,
        "warnings": [{"file": w.source_file, "message": w.message} for w in all_warnings],
        "figure_errors": figure_errors,
        "dependencies_note": "Tables use stdlib csv + numpy only; matplotlib optional for figures.",
        "layout_label_normalization": "Curve/Curved→Cylindrical; whole-word Stack→Stacked in exported columns.",
        "figures_per_study_subdirs": ["Study1", "Study2"],
        "inferential_stats_run": inferential_stats,
        "inferential_stats_output_directory": None,
    }

    stats_manifest_summary: Optional[dict] = None
    if inferential_stats and trials_full:
        sdir = Path(stats_output_dir or config.DEFAULT_STATS_OUTPUT_DIR).resolve()
        manifest["inferential_stats_output_directory"] = str(sdir)
        try:
            stats_manifest_summary = run_inferential_analysis(trials_full, blocks_full, sdir)
        except Exception as e:  # pragma: no cover
            manifest["inferential_stats_error"] = str(e)
            stats_manifest_summary = None
    elif inferential_stats:
        manifest["inferential_stats_note"] = "skipped_no_trials"
    if stats_manifest_summary:
        manifest["inferential_stats_n_rows"] = stats_manifest_summary.get("n_result_rows")
        manifest["inferential_stats_scipy_available"] = stats_manifest_summary.get("scipy_available")

    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    _copy_rationale_template(output_dir)
    _copy_user_guide(output_dir)

    readme = output_dir / "README.md"
    readme.write_text(
        """# Behavioral log analysis output

Produced by `behavior_log_pipeline` from Unity `Study*subject*Exp*.txt` and matching `*_overlooked.txt`.

- **`USER_GUIDE.md`** — how to run the tool, CLI options, inputs, and troubleshooting (start here).
- **`thesis_rationale_appendix.md`** — why each output supports the thesis research questions.
- **`run_manifest.json`** — this run’s paths, thresholds, warnings, and any figure errors.

## Figures

- **`figures/ttff_ecdf_by_study.png`** — both studies on one plot (comparison).
- **`figures/Study1/`** and **`figures/Study2/`** — per-study TTFF by **layout** and **display count**, delayed-discovery rates, process scatter, ECDF, errors by layout, and **re-engagement after intermediate views** (boxplot by layout and by **display count**, plus scatter). Legacy Unity label **Curve** is reported as **Cylindrical** in CSV and figures.

## Tables

All-session tables in **`tables/`** include a **`study`** column (filter for Study1 vs Study2 in Excel/R).

## Quick re-run

From the Unity project root:

```text
python Assets/OutputLog/run_behavior_logs.py
```

Full documentation: see **`USER_GUIDE.md`** in this folder (copied from the package on each run).
""",
        encoding="utf-8",
    )

    out = {
        "output_dir": str(output_dir),
        "trials": len(trials_full),
        "warnings": len(all_warnings),
    }
    if inferential_stats and manifest.get("inferential_stats_output_directory"):
        out["inferential_stats_dir"] = manifest["inferential_stats_output_directory"]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse Unity behavioral logs (search / overlooked) into tables and thesis figures."
    )
    parser.add_argument(
        "--input-dir",
        action="append",
        type=Path,
        default=None,
        help=(
            "Directory containing Study*subject*Exp*.txt (repeatable). "
            "Default: session_logs under OutputLog if present, else OutputLog (searched recursively)."
        ),
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output root (default: behavior_log_analysis_output under OutputLog).",
    )
    parser.add_argument(
        "--include-pilot",
        action="store_true",
        help="Include files under paths containing 'Pilot'.",
    )
    parser.add_argument("--skip-figures", action="store_true", help="CSV only, no matplotlib PNGs.")
    parser.add_argument(
        "--condition-json-dir",
        type=Path,
        default=None,
        help=(
            "Folder with StudyNsubject##ExpM.json condition exports (default: VarjoJSONfiles). "
            "See USER_GUIDE / VarjoJSONfiles/README.md."
        ),
    )
    parser.add_argument(
        "--inferential-stats",
        action="store_true",
        help="Run layout / display-count inferential tests (SciPy) into a separate folder (see --stats-output-dir).",
    )
    parser.add_argument(
        "--stats-output-dir",
        type=Path,
        default=None,
        help=(
            "Where to write inferential stats (default: behavior_log_inferential_stats under OutputLog). "
            "Only used with --inferential-stats."
        ),
    )
    args = parser.parse_args()

    dirs = args.input_dir if args.input_dir else config.default_behavior_log_input_dirs()
    result = run(
        input_dirs=dirs,
        output_dir=args.output_dir,
        exclude_pilot=not args.include_pilot,
        skip_figures=args.skip_figures,
        condition_json_dir=args.condition_json_dir,
        inferential_stats=args.inferential_stats,
        stats_output_dir=args.stats_output_dir,
    )
    print("Behavior log analysis complete:", result)


if __name__ == "__main__":
    main()
