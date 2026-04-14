# Behavioral log analysis output

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
