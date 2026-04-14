# Rationale for behavioral and “overlooked” analyses

This appendix explains **why** each output from the behavioral log pipeline is relevant to evaluating **layout geometry** (Study 1: flat, cylindrical, stacked; Study 2: cylindrical vs spherical) and **display set size** (4 vs 15) on **search efficiency** and, when linked to memory measures elsewhere, **memory efficiency**. Unity historically logged the cylindrical layout as **Curve**; exported tables and figures use **Cylindrical** instead. Wording is suitable to adapt into a thesis methods or results introduction.

---

## Research questions addressed

1. **Search efficiency:** Do layout and number of displays change how quickly participants **find** the correct view (time to first recorded view on the target) and how long **selection** takes?
2. **Failure modes (“overlooked” targets):** Beyond average reaction time, do some layouts produce more **delayed discovery** (long time-to-first-view) or more **wrong selections**, consistent with targets being visually overlooked or confused?
3. **Process evidence:** Does high-frequency logging in the `*_overlooked.txt` companion file show **more sampling** after the first-view milestone—**intermediate views** (often non-targets) before the participant returns and confirms—and does **re-engagement time** (main-log selection time minus last intermediate sample time) differ by layout or set size?
4. **Recovery after wandering:** When participants **do** sample away from the target before selecting it, how **quickly** do they **come back** and complete the trial? That latency links **spatial sampling** in the overlooked log to **final motor confirmation** in the main log.

---

## Outputs and justification

### `tables/trials_long.csv`

- **What it is:** One row per search episode with Unity-derived **time to first view (TTFF)**, **selection time** (`Time per selection` from the main log), optional **Varjo JSON–mapped condition** (e.g. `2by2Stack` vs `3by5Flat` for 4 vs 15 displays), and **process metrics** from the overlooked log: TTFF from the same **`for the first time`** milestone (either log line format), **count of intermediate `View looked at in … sec!` samples** after that milestone, **timestamp of the last** such sample, and **re-engagement after overlook** (selection time minus that last sample when defined)—a behavioral estimate of time from the last logged off-target glance back to confirming the target.
- **Why needed:** Trial-level data support **mixed-effects modeling** (random intercepts for participants) and linking to **eye-tracking metrics** from the separate Varjo pipeline using the same condition windows.
- **Thesis fit:** Directly operationalizes **search performance** as a function of **layout** and **set size**.

### `tables/blocks_summary.csv`

- **What it is:** For each block of five selections: **total time**, **wrong-selection count**, and the **short layout label** (Unity may log **Curve**; exports use **Cylindrical**).
- **Why needed:** Matches the **experimental block structure** and exposes **accuracy** at the same granularity as the logged summaries.
- **Thesis fit:** Connects **speed** (block duration) and **accuracy** (errors) to layout, addressing whether layouts trade off correctness for speed.

### `tables/aggregate_by_condition.csv`

- **What it is:** Means/medians/quantiles of TTFF and selection time, **delayed discovery rate**, mean process sample counts, and **re-engagement after overlook** (mean/median over trials where that metric is defined) **by full condition name** when JSON mapping is available.
- **Why needed:** This is the primary **results-ready** table for comparing **named experimental cells** (including 4 vs 15 when encoded in the condition string).
- **Thesis fit:** Supports formal comparison of **layout × set size** on search difficulty and overlooked-related outcomes.

### `tables/aggregate_by_display_count.csv`

- **What it is:** Aggregates **only** where `display_count` is known from the condition name (4 vs 15).
- **Why needed:** Isolates the **set-size** factor even when figure captions emphasize display cardinality rather than full condition labels.
- **Thesis fit:** Directly answers whether **more displays** increase **TTFF** and **delayed discovery**, as predicted by visual search and spatial memory load.

### `tables/aggregate_by_participant.csv`

- **What it is:** Per-participant medians/rates for TTFF, delayed discovery, mean process samples, and **median re-engagement after overlook** where available.
- **Why needed:** Supports **heterogeneity** reporting and choice of **robust** summaries; feeds **by-subject** plots in supplementary material.
- **Thesis fit:** Shows that layout effects are not driven by a few outliers without revealing raw identifiers beyond subject index.

### `tables/aggregate_errors_by_layout_raw.csv`

- **What it is:** Error totals grouped by **Unity’s short layout label** and study.
- **Why needed:** When JSON mapping is missing, this still supports **exploratory** comparison; with mapping, use condition-level aggregates instead.
- **Thesis fit:** **Wrong selections** are a behavioral correlate of **search confusion** and potential **memory–search** failures.

### `figures/ttff_ecdf_by_study.png`

- **What it is:** Empirical cumulative distribution of TTFF pooled within **Study1** vs **Study2** (and any other study labels in the filenames).
- **Why needed:** Means hide **tail behavior**; **delayed discovery** often lives in the upper tail—ECDFs are standard in HCI and vision reporting.
- **Thesis fit:** Demonstrates whether one study’s search is **stochastically faster** than another’s, beyond a single \(p\)-value on means.

### `figures/Study1/` and `figures/Study2/` (per-study figures)

Figures are **split by study** so Study 1 (flat, cylindrical, stacked) and Study 2 (cylindrical, spherical) are not pooled on the same layout or display-count plots.

| File (under each `StudyN/` folder) | Role |
|------------------------------------|------|
| `ttff_boxplot_by_condition.png` | TTFF by mapped condition (e.g. `2by2Cylindrical`, `3by5Stack`) when JSON is present. |
| `ttff_boxplot_by_display_count.png` | TTFF by **4 vs 15** displays for that study only. |
| `delayed_discovery_rate_by_condition.png` | Delayed-discovery rate by condition (that study). |
| `delayed_discovery_rate_by_display_count.png` | Same by display count (that study). |
| `ttff_boxplot_by_layout.png` | TTFF by short layout (**Flat / Cylindrical / Stack** vs **Cylindrical / Sphere** as applicable). |
| `ttff_ecdf.png` | ECDF of TTFF for that study (all participants in the batch). |
| `process_samples_vs_ttff.png` | Process density scatter for that study. |
| `reengagement_boxplot_by_layout.png` | **Re-engagement after intermediate views** (selection time − last intermediate overlooked sample), by short layout. |
| `reengagement_boxplot_by_display_count.png` | Same metric **by display count (4 vs 15)** when `display_count` is present from condition JSON (same trials subset as TTFF-by-display-count). |
| `reengagement_vs_intermediate_view_count.png` | Scatter: number of intermediate overlooked samples vs re-engagement (trials with at least one intermediate sample). |
| `errors_by_layout.png` | Total wrong selections by layout for that study. |

- **Why needed:** Avoids **confounding** two experiments when the same word (e.g. cylindrical) refers to different surrounding layouts; supports **study-specific** results sections.
- **Thesis fit:** Clear **Study 1** vs **Study 2** reporting for layout and set size.

### `figures/errors_total_by_study_layout.png`

- **What it is:** Total wrong selections summed by **study** and **short layout label**.
- **Why needed:** Quick **accuracy** overview across the dataset.
- **Thesis fit:** Links **layout** to **error-type** search failure, complementing TTFF-focused “overlooked” measures.

### `run_manifest.json`

- **What it is:** Run timestamp, input directories, **thresholds**, list of **parse warnings** (e.g. missing JSON or missing overlooked file).
- **Why needed:** **Provenance** and **reproducibility** for the thesis appendix or open materials.
- **Thesis fit:** Supports claims that analyses were **auditable** and **re-run** identically.

---

## Operational definition of “delayed discovery”

**Delayed discovery** is flagged when Unity’s trial-level **time to first view** is **≥ `DELAYED_TTFF_THRESHOLD_SEC`** (see `behavior_log_pipeline/config.py` and the manifest). This is a **pragmatic** proxy for targets that were **temporarily overlooked** or required extended search. The threshold should be stated explicitly in the thesis; it can be adjusted and the pipeline re-run.

---

## Re-engagement after intermediate views (thesis wording)

**Re-engagement after overlook** combines the **main** session log and the **`_overlooked`** companion log. For each trial, Unity logs **time to first target view** and, in the overlooked file, a stream of **`View looked at in … sec!`** timestamps **after** first hitting the target and **before** the next trial’s **first view** marker. The **last** such timestamp indexes how late the participant was still sampling **other** views (in the log’s sense) before the trial ended; the main log’s **`Time per selection`** records total time until **confirmation**. Their **difference** estimates the interval from that last intermediate sample to **selection**—a concise **behavioral** measure of **returning to and confirming** the target after wandering. **Caveats:** (1) it is only defined when at least one intermediate sample exists; (2) it assumes both logs share a consistent trial timeline; (3) “view” is whatever Unity logged, not raw gaze. Report how many trials contributed and consider layout × set-size contrasts **in addition to** TTFF and error rates.

---

## Optional folder: inferential statistics (`behavior_log_inferential_stats`)

### What this folder contains

A **separate** output tree (**root**, plus **`Study1/`** and **`Study2/`** copies) with **rank-based inferential screening**, **exploratory distributional diagnostics**, **post-hoc contrasts** when omnibus tests are significant, and **thesis-ready companion** tables and bar figures. Three **`analysis_type`** values isolate effects: (**1**) **session omnibus**—layout across all layouts and **4 vs 15** pooled across layouts in that session; (**2**) **layout within display**—compare layouts **only at 4** or **only at 15** displays; (**3**) **display within layout**—compare **4 vs 15** **within** each `layout_raw`. Outcomes include **selection time**, **TTFF**, **re-engagement**, **intermediate view samples**, **delayed-discovery flag**, **log process density**, and **block error rate**, per **Study × Exp1–3**.

### Distributional assumptions and normality

**The primary tests do not require normally distributed data.** **Kruskal–Wallis** and the **Mann–Whitney U** test operate on **ranks**; they are standard choices for **reaction times** and other **right-skewed** behavioral measures without assuming Gaussian residuals.

The pipeline nonetheless exports **`inferential_group_descriptives_shapiro.csv`**, which includes **Shapiro–Wilk** statistics for each group (when **3 ≤ n ≤ 5000**) **alongside** means, medians, and SDs. **Thesis use:** (i) show reviewers you **checked** distributional shape; (ii) justify **nonparametric** screening when Shapiro is often rejected; (iii) avoid over-claiming that **ANOVA** would be justified even when a group passes Shapiro—**nested repeated measures** still call for **mixed models**, not ordinary one-way ANOVA on pooled trials.

The tool **does not** automatically switch to **t-tests / ANOVA** when normality appears plausible; that would **change the hypothesis framework**, ignore **non-independence**, and fragment comparison with the rank-based **FDR families** already documented in the enriched tables.

### Why Kruskal–Wallis for layout (three or more groups)

Layout is a **categorical** factor with **several** geometry labels (e.g. flat, cylindrical, stacked). **Kruskal–Wallis** is the standard **omnibus** extension of the rank-sum idea to **k ≥ 2** independent samples **under the usual idealization** (here: still exploratory because trials repeat within participants). It answers whether **at least one** layout’s distribution **differs** on the outcome.

### Why Mann–Whitney for 4 vs 15

After JSON mapping, **set size** is **binary** (4 vs 15) within a stratum. **Mann–Whitney** compares two samples on a **continuous or ordinal** outcome without normality. (For **binary** outcomes such as **delayed flag**, ranks remain a mechanical test; interpret alongside **rates** and consider **mixed logistic** models for confirmation.)

### Post-hoc procedures after significant omnibus tests (which group is better or worse?)

**Layout (after Kruskal–Wallis *p* < 0.05, uncorrected):** the average-rank omnibus does **not** say **which** pair of layouts differs. The pipeline runs **all pairwise two-sided Mann–Whitney** tests between layouts in **that same** analysis context and adjusts pairwise *p*-values with **Holm’s** step-down method **within that pairwise family**. **Why Holm:** it **controls family-wise error** for multiple pairwise comparisons **without** assuming equal variances, and pairs naturally with nonparametric pairwise tests. **Thesis wording:** report **which pairs** survive Holm, then use **medians** (and optional plots from your descriptive pipeline) to state **direction** (e.g. longer TTFF = worse search latency).

**4 vs 15 (after Mann–Whitney *p* < 0.05):** only **two** groups, so **no** pairwise post-hoc is needed. The companion table adds **medians** per set size, a short **direction** line (assuming **higher** latency/error is **worse** for the timed and error outcomes), and **Cliff’s delta** as a **robust effect size** bounded in \([-1,1]\).

### Companion figures for the thesis

See **`STATS_README.md`** for filenames. Briefly: **horizontal bar charts** of **median differences** for **Holm-significant** layout pairs, and **Cliff’s delta** bars for **significant** 4 vs 15 contrasts—suitable as **supplementary** figures next to heatmaps. Per-study outputs split those bar charts **by Exp1–3** (separate PNGs) for readable y-axis labels.

### Participant-level inferential complements (non-independence)

Trial-level **Kruskal–Wallis** / **Mann–Whitney** treat each trial as a unit and are **exploratory** when trials repeat within participants. The pipeline also writes **`inferential_participant_level_tests.csv`**: for each stratum, **one summary per participant** (median of trials or blocks in that cell), then **paired Wilcoxon** for **4 vs 15** (paired per-participant medians), **paired Wilcoxon** for **two layouts**, or **Friedman** for **three or more layouts** on participants with **complete** medians. These address **non-independence** more directly than pooled trials but are still **not** a substitute for **mixed-effects models** if you need a full confirmatory framework. **Figures:** **`inferential_participant_level_pvalue_heatmaps_session*.png`** (session omnibus, parallel to trial-level heatmaps), plus **`inferential_participant_level_layout_within_display_StudyN.png`** and **`inferential_participant_level_display_within_layout_StudyN.png`** for stratified scopes—see **`STATS_README.md`**.

### Stratification, FDR, and caveats

**Layout within display** and **display within layout** reduce confounding compared with the session omnibus. **BH-FDR** in the enriched tables is **within** explicit **`fdr_family`** keys, not global across the entire spreadsheet.

**Caveats:** trials are **non-independent** within participant; **mixed models** should back **confirmatory** claims. Use **`fdr_family`** and pre-specified contrasts in the thesis text. See **`STATS_README.md`** for column definitions, Shapiro caveats, and figure filenames.

---

## Integration with the Varjo eye-tracking pipeline

Behavioral logs answer **what** the task timing and errors were; the **eye-tracking pipeline** (`eye_tracking_pipeline`) answers **where** gaze went. Together they support claims that specific layouts **increase search time and errors** and **change gaze paths**—a stronger **evaluation of layout impact** than either modality alone.
