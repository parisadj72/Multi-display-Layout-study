# Inferential statistics output (optional)

This folder explains **`behavior_log_inferential_stats`** (or your custom `--stats-output-dir`), produced when you run:

```text
python Assets/OutputLog/run_behavior_logs.py --inferential-stats
```

**Folder layout**
- **Root** (`tables/`, `figures/`): **all studies combined** on the session-omnibus heatmaps (Study1 and Study2 columns side by side).
- **`Study1/`** and **`Study2/`**: the **same table and figure names**, but **filtered to that study**—use these chapters for thesis write-ups per experiment.
- **Per-study figures** add **stratified** heatmaps: layout effects **holding display count fixed** (4 vs 15), and **4 vs 15** contrasts **holding layout fixed**.

**Experiment numbering (`experiment_num`, charts, CSV)** — same as **`Study{N}subject{##}Exp{M}`** in `session_logs/` and `VarjoJSONfiles/`:
- **Exp1** — selection / search task  
- **Exp2** — memory task  
- **Exp3** — puzzle (swap) task  

All figures and `study_exp_label` fields use the **`Exp1` … `Exp3`** spelling (not `E1` … `E3`).

**Matplotlib** is used for PNGs; failures are listed under **`inferential_figure_errors`** in `stats_manifest.json`.

---

## Analysis types (`analysis_type` column)

| Value | Meaning | Typical question |
|--------|---------|------------------|
| **`session_omnibus`** | Same as the original pipeline: within each Study×Exp, compare **all layouts** (Kruskal–Wallis) and **4 vs 15 pooled** across layouts (Mann–Whitney). | “Is there **any** layout effect, or **any** set-size effect, in this session?” |
| **`layout_within_display`** | Trials/blocks **restricted to 4 displays** *or* **15 displays** (`subset_display_count`). Compare **layouts** only. | “**Given** 4 (or 15) panels, do **geometry** (flat / curved / stacked / sphere) still matter?” |
| **`display_within_layout`** | Trials/blocks **restricted to one `layout_raw`** (`subset_layout`). Compare **4 vs 15**. | “**Within Flat** (or Cylindrical, …), does **set size** still increase difficulty?” |

These stratified tests better match **factorial** reasoning (isolate layout vs set size) than the omnibus alone. They require JSON-enriched **`display_count`** and multiple layouts in the log slice.

---

## Outcomes (measured metrics + rationale)

| `outcome` key | Source | Rationale |
|---------------|--------|-----------|
| **`time_per_selection`** | `selection_time_sec` | **Task completion** time for the search trial. |
| **`ttff`** | `unity_ttff_sec` | **Discovery** latency (first view on target). |
| **`reengagement_after_overlook`** | `reengagement_after_overlook_sec` | **Recovery** after intermediate views; **subset** of trials only. |
| **`overlooked_view_samples_post_first_hit`** | `overlooked_view_sample_count` | **Process load**: how many high-rate view logs after first target hit until trial end. |
| **`delayed_binary_flag`** | `delayed_discovery_flag` | **Binary** “slow first view” (TTFF ≥ threshold); rank/MW still exploratory on 0/1. |
| **`log_process_density`** | `log_process_density` | Samples-per-second style ratio (`overlooked_view_sample_count / TTFF`); **finite** where TTFF &gt; 0. |
| **`block_error_rate`** | `errors_wrong_selections / 5` | **Accuracy** at Unity’s 5-trial block level. |

**Tests:** **Kruskal–Wallis** for **multi-level layout**; **Mann–Whitney U** for **4 vs 15**.

---

## Distributional assumptions (normality)

**Primary tests (Kruskal–Wallis, Mann–Whitney) are rank-based.** They do **not** require **normality** or **homogeneity of variance** in the same way as ANOVA / *t*-tests. They remain valid as omnibus / two-sample tests on **ordered** outcomes when their standard hypotheses are stated in terms of **distributions** (or stochastic ordering), subject to the usual **independence** caveat (here: trials are **not** independent within participant—see limitations).

**Why we still report Shapiro–Wilk (`inferential_group_descriptives_shapiro.csv`):** for **transparency** and **thesis methods**: reaction times and error rates are often **skewed**; Shapiro on each test group (**3 ≤ n ≤ 5000**) documents whether Gaussian models would be plausible **descriptively**. A small Shapiro *p* supports the **choice of nonparametric** screening instead of parametric ANOVA. The pipeline **does not** switch automatically to *t*-tests when Shapiro is non-significant: repeated trials per participant would still violate the **i.i.d.** assumptions of simple parametric tests; **mixed models** are the appropriate confirmatory framework.

---

## Post-hoc and effect direction (companions)

When **layout** Kruskal–Wallis is **significant at p < 0.05 (uncorrected)**, the pipeline runs **pairwise two-sided Mann–Whitney** between all layout pairs in that **same** analysis context (same Study, Exp, `analysis_type`, outcome, display-count stratum). **Holm’s** stepwise procedure controls **family-wise error** across those pairwise *p*-values **within that post-hoc family only** (not across the whole inferential CSV).

When **4 vs 15** Mann–Whitney is **significant at p < 0.05**, the pipeline adds **medians**, a plain-language **direction** hint (higher latency/error usually “worse”), and **Cliff’s delta** (a robust effect size for two samples: \(P(X\!>\!Y)-P(X\!<\!Y)\) with *X* from the 4-display sample and *Y* from 15).

---

## Dependencies

- **SciPy** — p-values.
- **Matplotlib** — figures.

---

## Tables

| File | Purpose |
|------|---------|
| **`inferential_tests_long.csv`** | All tests; includes **`analysis_type`**, **`subset_display_count`**, **`subset_layout`**. |
| **`inferential_tests_long_enriched.csv`** | Labels, **`neg_log10_p`**, **`fdr_family`**, **`q_value_fdr_within_family`**, interpretation. |
| **`inferential_tests_stratified_enriched.csv`** | Only **`layout_within_display`** and **`display_within_layout`** rows (easier filtering). |
| **`inferential_tests_significant_uncorrected.csv`** | **p &lt; 0.05** (uncorrected). |
| **`inferential_tests_significant_fdr_within_family.csv`** | **q &lt; 0.05** under BH-FDR **within** the row’s **`fdr_family`**. |
| **`inferential_pvalues_wide_session_omnibus.csv`** | Pivot table for **session omnibus only** (outcome × factor × Study×Exp). |
| **`inferential_test_counts_by_study_and_analysis.csv`** | How many test rows per **study** × **`analysis_type`**. |
| **`inferential_group_descriptives_shapiro.csv`** | Per **group** in each analysis stratum: **n**, mean, median, SD, **Shapiro–Wilk** (when *n* in range). |
| **`inferential_posthoc_layout_pairwise_holm.csv`** | After **significant layout K–W** (*p*<0.05): pairwise **M–W**, **Holm** *p*, medians, direction line. |
| **`inferential_effect_sizes_4_vs_15_cliffs_delta.csv`** | After **significant 4 vs 15 M–W** (*p*<0.05): medians, **Cliff’s delta**, direction line. |
| **`inferential_participant_level_tests.csv`** | **Participant-level** complements: **paired Wilcoxon** on per-participant medians for **4 vs 15**; **two layouts** = paired Wilcoxon on layout medians; **three or more layouts** = **Friedman** on subjects with complete medians across all layouts. Same **`analysis_type`** / outcome structure as trial-level tests; **`n_participants`** is the effective sample size. |

**FDR:** Each **family** is keyed by **`(study, experiment_num, analysis_type, subset_display_count, subset_layout)`**. For example, **session omnibus** for Study1 Exp1 pools **14** tests (7 outcomes × 2 factors); **layout at fixed 4 displays** pools **7** tests (6 trial + 1 block); **4 vs 15 within one layout** pools **7** tests. This is **local** multiplicity control—not a single global FDR across every row in the CSV.

---

## Figures (root `figures/`)

| File | Purpose |
|------|---------|
| **`inferential_pvalue_heatmaps_session.png`** | Session omnibus −log10(p); columns = all Study×Exp; **\*** p&lt;0.05. |
| **`inferential_fdr_q_heatmaps_session.png`** | Session omnibus FDR **q**. |
| **`inferential_significant_uncorrected_bars.png`** | Bar chart of all significant tests (both studies). |
| **`inferential_posthoc_layout_median_diffs_holm_005.png`** | **Holm *p*<0.05** layout pairs: horizontal bars = median difference (A−B). |
| **`inferential_cliffs_delta_4_vs_15_significant.png`** | **Significant** 4 vs 15 contrasts: Cliff’s delta per stratum. |
| **`inferential_participant_level_pvalue_heatmaps_session.png`** | **Participant-level** session omnibus: −log10(p) for **layout** (Friedman or paired Wilcoxon) and **4 vs 15** (paired Wilcoxon); same layout as trial-level session heatmaps for comparison. |

## Figures (`Study1/figures/`, `Study2/figures/`)

| File | Purpose |
|------|---------|
| **`inferential_pvalue_heatmaps_session_StudyN.png`** | Session omnibus for **that study only** (columns Exp1–3). |
| **`inferential_fdr_q_heatmaps_session_StudyN.png`** | FDR q for that study. |
| **`inferential_significant_uncorrected_bars_StudyN.png`** | Significant tests in that study only. |
| **`inferential_layout_within_display_StudyN.png`** | Two panels (**4** vs **15** displays): layout K–W, rows=all outcomes, columns=Exp1–3. |
| **`inferential_display_within_layout_StudyN.png`** | One heatmap: **4 vs 15** within each **(Exp, layout)** column that has data. |
| **`inferential_posthoc_layout_median_diffs_holm_005_StudyN_Exp1.png`** … **`_Exp3.png`** | **Holm *p*<0.05** layout pairs (one file per **Exp1–3**) so y-axis labels do not overlap. |
| **`inferential_cliffs_delta_4_vs_15_significant_StudyN_Exp1.png`** … **`_Exp3.png`** | **Significant** 4 vs 15 Cliff’s delta bars, **one experiment per figure**. |
| **`inferential_participant_level_pvalue_heatmaps_session_StudyN.png`** | Participant-level **session** p-value heatmaps (**that study**, Exp1–3). |
| **`inferential_participant_level_layout_within_display_StudyN.png`** | Participant-level **layout** at fixed **4** vs **15** displays (two panels). |
| **`inferential_participant_level_display_within_layout_StudyN.png`** | Participant-level **4 vs 15** (paired Wilcoxon) **within** each layout column. |

---

## Important limitations (thesis)

1. **Non-independence** within participant—use mixed models for confirmatory claims.
2. **Many tests** across the full CSV—interpret **fdr_family** and pre-specify contrasts for the text.
3. **Small n** in stratified cells when JSON or session design limits overlap of layout × display count.
4. **Binary delayed flag** and **re-engagement** are useful descriptively but are **not** full gaze models.

The main behavioral exports remain under **`behavior_log_analysis_output`** (`-o`).
