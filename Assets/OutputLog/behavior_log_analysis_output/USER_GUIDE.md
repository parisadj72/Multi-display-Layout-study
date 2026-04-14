# Behavioral log analysis — user guide

This pipeline reads Unity text logs (`Study*subject*Exp*.txt` and matching `*_overlooked.txt`; by default under **`Assets/OutputLog/session_logs/`**), merges Varjo condition JSON when available, writes **CSV tables** and optional **PNG figures**, and records a **run manifest** for reproducibility.

---

## What you need installed

| Component | Required? | Role |
|-----------|-----------|------|
| **Python 3.10+** | Yes | Interpreter |
| **NumPy** | Yes | Parsing helpers, some aggregates |
| **Matplotlib** | Only for figures | Skip with `--skip-figures` if missing or broken |
| **SciPy** | Only for `--inferential-stats` | Nonparametric p-values; `pip install scipy` |

**Pandas is not used.** Tables are built with the standard library `csv` module so a broken or “empty” `pandas` install (common when multiple Python installations share or shadow `site-packages`) does not stop CSV output.

Install minimal dependencies:

```text
pip install numpy matplotlib
```

Or use the project file:

```text
pip install -r Assets/OutputLog/requirements_behavior_logs.txt
```

---

## How to run

### From the Unity project root (recommended)

```text
python Assets/OutputLog/run_behavior_logs.py
```

With custom output folder:

```text
python Assets/OutputLog/run_behavior_logs.py -o Assets/OutputLog/behavior_log_analysis_output
```

### From `Assets/OutputLog`

```text
cd Assets/OutputLog
python run_behavior_logs.py
```

### As a module (same as above, different path)

```text
cd Assets/OutputLog
python -m behavior_log_pipeline.run_analysis
```

---

## Command-line options

| Option | Meaning |
|--------|---------|
| `--input-dir PATH` | Folder to scan for `Study*subject*Exp*.txt` (**recursive**). **Repeat** to add more folders. Default: **`session_logs`** under `OutputLog` if that folder exists, otherwise all of `OutputLog`. |
| `-o` / `--output-dir PATH` | Where to write results. Default: `Assets/OutputLog/behavior_log_analysis_output`. |
| `--include-pilot` | By default, paths containing `Pilot` (case-insensitive) are **skipped**. This flag includes them. |
| `--skip-figures` | Write **only CSV + JSON + copied docs**; no matplotlib PNGs (faster; works without matplotlib). |
| `--inferential-stats` | Run **layout** (Kruskal–Wallis) and **4 vs 15 display** (Mann–Whitney U) tests on selection time, TTFF, re-engagement, and block error rate—**per study and per Exp1–3**—into a **separate output folder** (default `behavior_log_inferential_stats`). Requires **SciPy** (`pip install scipy`). Inferential heatmaps use **Exp1–Exp3** labels (same numbering as **`StudyNsubject##ExpM`** logs/JSON). See **`behavior_log_pipeline/report/STATS_README.md`**. |
| `--stats-output-dir PATH` | Folder for inferential statistics (only with `--inferential-stats`). |
| `--condition-json-dir PATH` | Where to find **`StudyNsubject##ExpM.json`** files for block→condition mapping. Default: `Assets/OutputLog/VarjoJSONfiles`. See **`VarjoJSONfiles/README.md`**. |

### Examples

```text
python Assets/OutputLog/run_behavior_logs.py --skip-figures
```

```text
python Assets/OutputLog/run_behavior_logs.py --input-dir Assets/OutputLog --input-dir "D:/backup/logs"
```

```text
python Assets/OutputLog/run_behavior_logs.py --condition-json-dir Assets/OutputLog/VarjoJSONfiles --include-pilot
```

```text
python Assets/OutputLog/run_behavior_logs.py --inferential-stats --skip-figures
```

```text
python Assets/OutputLog/run_behavior_logs.py --inferential-stats --stats-output-dir Assets/OutputLog/my_stats_run
```

---

## Input files

### Where logs live

- **Recommended:** `Assets/OutputLog/session_logs/` — all `Study*subject*Exp*.txt` and `*_overlooked.txt` session files together.
- **Legacy:** logs may still live directly under `Assets/OutputLog/`; if `session_logs/` does not exist, the default input directory is the whole `OutputLog` tree (searched recursively).

### Main session log

- **Pattern:** `Study{1|2}subject{N}Exp{M}.txt` (subject id may be one or two digits in the filename; the pipeline parses the integer and pairs JSON using **two-digit** stems, e.g. subject 6 → `06`).  
  Examples: `Study1subject1Exp1.txt`, `Study2subject12Exp2.txt`
- **Must not** contain `_overlooked` in the name.

### Overlooked companion log

- **Pattern:** same stem + `_overlooked.txt`  
  Example: `Study1subject1Exp1_overlooked.txt`
- **Trial markers:** Each trial is anchored on a line containing **`for the first time`**. Unity may log either a short form (`View looked at in … seconds for the first time!`) or a long banner (`… was looked at in … seconds for the first time!`). The parser accepts both, so overlooked-derived columns are filled whenever those markers align with the main log’s trials.
- If the companion file is **missing**, the run continues; trials still appear but **overlooked process columns** are empty and a **warning** is added to `run_manifest.json`. If the count of **`for the first time`** markers in the overlooked file **does not** match the number of trials parsed from the main log, the manifest includes a **misalignment warning** (merge is still by trial index).

### Duplicate logs

If the same filename exists under **`My Data`** and elsewhere under `OutputLog`, the pipeline keeps the copy **outside** `My Data` (shorter canonical path wins) so sessions are not double-counted. With logs in **`session_logs/`**, keep only one copy of each stem per study tree.

### Condition JSON (optional but recommended)

- **Naming:** Same stem as the Unity main log, with `.json`: **`Study{N}subject{##}Exp{M}.json`**  
  Examples:  
  - `Study1subject06Exp1.txt` → `Study1subject06Exp1.json` (selection / session 1)  
  - `Study1subject06Exp2.txt` → `Study1subject06Exp2.json` (memory)  
  - `Study1subject06Exp3.txt` → `Study1subject06Exp3.json` (puzzle; optional if Exp2/Exp1 order matches—see **`VarjoJSONfiles/README.md`**)
- **Study and subject** in the filename must match the log. The JSON should also include `"study": "Study1"` or `"Study2"` (and optional `"participant_id"`) for your own records; the pipeline **selects the file by log stem**, not by rewriting names from metadata.
- **Role:** The `conditions` array order must match the **order of blocks** in the `.txt` file (selection: multi-trial blocks; memory/puzzle: one trial per block as parsed). That adds columns such as `condition_name` (e.g. `2by2Stack`, `3by5Flat`), **display count (4 vs 15)**, and layout family for aggregation and inferential strata.

If JSON is missing, you still get Unity layout labels (`Stack`, `Flat`, …) and warnings in the manifest.

### Layout naming (Curve → Cylindrical)

Unity and older Varjo JSON use **Curve** for the cylindrical layout. In this pipeline’s **CSV and figures**, **Curve** / **Curved** / **curve** / **curved** are rewritten to **Cylindrical** / **cylindrical**. The whole word **Stack** becomes **Stacked** (e.g. `2by2Stack` → `2by2Stacked`, block label `Stack` → `Stacked`). **Varjo condition JSON files on disk are not modified** by this step; they may still contain `2by2Curve` while `trials_long.csv` shows `2by2Cylindrical`. When merging behavioral data to gaze by condition string, align merge keys with either the JSON spelling or these normalized columns intentionally.

If a JSON file is **present but invalid** (syntax error, truncated file), enrichment is skipped for that session and the manifest warns that the file **could not be parsed**—the run still completes.

---

## Output folder layout

Everything is written under the chosen **`--output-dir`** (default `behavior_log_analysis_output`).

| Path | Description |
|------|-------------|
| **`USER_GUIDE.md`** | This guide (copied on each run). |
| **`thesis_rationale_appendix.md`** | Thesis-oriented rationale per output. |
| **`README.md`** | Short pointer to the guide and manifest. |
| **`run_manifest.json`** | UTC timestamp, input dirs, JSON dir, row counts, **`delayed_ttff_threshold_sec`**, all parse warnings, **`figure_errors`** if plotting failed. |
| **`tables/trials_long.csv`** | One row per search trial: TTFF, selection time, block/layout, optional condition + display count, overlooked metrics, derived flags. |
| **`tables/blocks_summary.csv`** | One row per 5-selection block: times, errors, layout label. |
| **`tables/aggregate_by_condition.csv`** | Summaries by `condition_name` (if JSON matched) else by `layout_raw`. |
| **`tables/aggregate_by_display_count.csv`** | By study and **4 vs 15** (only if `display_count` was filled from JSON). |
| **`tables/aggregate_by_participant.csv`** | Per participant × experiment. |
| **`tables/aggregate_errors_by_layout_raw.csv`** | Error totals by study and Unity layout label. |
| **`figures/ttff_ecdf_by_study.png`** | ECDF of TTFF: **Study1 vs Study2** on one plot. |
| **`figures/Study1/*.png`** | **Study 1 only:** TTFF by layout (Flat / Cylindrical / Stacked), by display count (4 vs 15), by mapped condition, delayed-discovery plots, process vs TTFF, single-study ECDF, errors by layout, **re-engagement after intermediate views** (boxplot by layout and **by display count**; scatter vs intermediate view count). |
| **`figures/Study2/*.png`** | **Study 2 only:** same set for cylindrical vs spherical layouts and display count, including **re-engagement** boxplots by layout and **by display count**, plus scatter. |
| **`figures/errors_total_by_study_layout.png`** | Pooled error totals with `study / layout` labels (overview). |

### Inferential statistics folder (separate default path)

When you use **`--inferential-stats`**, outputs go to **`behavior_log_inferential_stats`** by default (or **`--stats-output-dir`**). **`Study1/`** and **`Study2/`** each contain **`tables/`** and **`figures/`** for that study only; the **root** holds the **combined** session omnibus figures.

| Path (under stats root) | Description |
|-------------------------|---------------|
| **`STATS_README.md`** | Analysis types, all outcomes, **`fdr_family`** / FDR, figure filenames. |
| **`tables/inferential_tests_long.csv`** | All tests: **`analysis_type`**, **`subset_display_count`**, **`subset_layout`**. |
| **`tables/inferential_tests_long_enriched.csv`** | **`fdr_family`**, **`q_value_fdr_within_family`**, interpretation. |
| **`tables/inferential_tests_stratified_enriched.csv`** | Layout-at-fixed-display and 4-vs-15-within-layout only. |
| **`tables/inferential_tests_significant_uncorrected.csv`** | **p < 0.05**. |
| **`tables/inferential_tests_significant_fdr_within_family.csv`** | **q < 0.05** within **`fdr_family`**. |
| **`tables/inferential_pvalues_wide_session_omnibus.csv`** | Pivot: session omnibus **p** / **q** by Study×Exp. |
| **`tables/inferential_test_counts_by_study_and_analysis.csv`** | Counts per study × analysis type. |
| **`figures/inferential_*session*.png`** | Heatmaps (**root** = both studies; per-study copies under **`StudyN/figures/`**). |
| **`StudyN/figures/inferential_layout_within_display_StudyN.png`** | Layout K–W at **4** vs **15** displays. |
| **`StudyN/figures/inferential_display_within_layout_StudyN.png`** | **4 vs 15** M–W within each layout. |
| **`stats_manifest.json`** | SciPy; **`inferential_figure_errors`**. |

**Important:** Exploratory screening; use **mixed models** for confirmatory claims. **`STATS_README.md`** and **`thesis_rationale_appendix.md`** give full rationale.

### Derived columns (trials)

- **`delayed_discovery_flag`:** `1` if `unity_ttff_sec` ≥ **`DELAYED_TTFF_THRESHOLD_SEC`** in `behavior_log_pipeline/config.py` (default **0.5 s**). Adjust there and re-run to match your thesis definition of “overlooked” / delayed first view.
- **`ttff_immediate_flag`:** `1` if TTFF is effectively zero (immediate first view in the log).
- **`ttff_main_vs_overlooked_abs_diff`:** Absolute difference between main log and overlooked log TTFF when both exist (sanity check).
- **`unity_ttff_sec_overlooked_file`:** From the overlooked log: seconds until **`for the first time`** (first logged acquisition of the target view), using the same dual-format detection as above.
- **`overlooked_view_sample_count`:** After that milestone, the count of **`View looked at in … sec!`** lines until the **next** trial’s **`for the first time`** line—i.e. intermediate views (typically non-targets sampled before the participant looks back and completes selection in the main log).
- **`overlooked_last_view_sample_sec`:** Timestamp (seconds in the overlooked log’s timeline) of the **last** such **`View looked at in … sec!`** sample in that same between-milestone window, or empty if there were none.
- **`reengagement_after_overlook_sec`:** When both are available and ordering is consistent (**`Time per selection =`** from the **main** log minus **`overlooked_last_view_sample_sec`**), this estimates how long it took to **return from the last intermediate view sample to confirming the target** (selection). It is empty if there were no intermediate samples, if the overlooked file is missing, or if timestamps disagree. It is most interpretable when **`overlooked_view_sample_count` ≥ 1** (participant left the target and sampled at least one other view before finishing). Aggregates (`reengagement_after_overlook_mean` / `_median`, etc.) summarize only trials with a finite value.

---

## Troubleshooting

### `AttributeError: module 'pandas' has no attribute 'DataFrame'`

This pipeline **does not import pandas** for tables. If you still see pandas in a traceback, another script or environment is involved. For **this** tool, upgrade/reinstall is not required for CSV output.

### Figure step fails (matplotlib)

- Use **`--skip-figures`** to get all tables and the manifest.
- Check **`figure_errors`** in **`run_manifest.json`** (the run still **exits successfully**; only PNGs are missing).
- Common Windows error: `cannot import name '_c_internal_utils' from partially initialized module 'matplotlib'` — usually a **corrupted or mixed** install. Try:
  - `python -m pip install --force-reinstall "matplotlib>=3.8"`
  - Or run the script with another interpreter (e.g. a **venv** or **conda env** where `python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt"` works).

### Mixed Python / conda paths

If `python -c "import pandas; print(pandas.__file__)"` prints `None` or errors, you may have conflicting **PYTHONPATH** or multiple Pythons. Use **`py -3.10`** or a **venv** where you `pip install numpy matplotlib` and run the same interpreter consistently.

### No `condition_name` / empty `aggregate_by_display_count.csv`

Either there is no **`StudyNsubject##ExpM.json`** for that session, or the filename does not match the log (e.g. `Study1subject6Exp1` needs **`Study1subject06Exp1.json`**). Fix naming or pass **`--condition-json-dir`** to the folder that contains the JSON files. Confirm the `conditions` array is non-empty and index-aligned with Unity blocks.

---

## Relation to the Varjo eye-tracking pipeline

- **This pipeline:** Unity **behavioral** logs (TTFF, selection RT, errors, overlooked sampling).
- **`eye_tracking_pipeline` / `run_analysis.py`:** Varjo **gaze** CSV + condition JSON + AOIs.

Run behavioral batch **before or after** gaze analysis; outputs are separate. The thesis rationale appendix describes how to combine them in writing.

---

## Changing thresholds

Edit **`behavior_log_pipeline/config.py`**:

- `DELAYED_TTFF_THRESHOLD_SEC` — delayed discovery / “overlooked” proxy  
- `TTFF_IMMEDIATE_SEC` — what counts as instantaneous first view  
- `FIGURE_DPI` — PNG resolution  

Re-run the CLI; **`run_manifest.json`** records the threshold used.
