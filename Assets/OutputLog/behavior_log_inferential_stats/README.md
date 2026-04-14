# Inferential statistics (behavioral logs)

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
