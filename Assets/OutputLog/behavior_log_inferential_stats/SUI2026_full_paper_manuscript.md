# Multi-Panel Layout and Set Size in VR: A Two-Phase Evaluation (SUI 2026 manuscript draft)

Working title—replace with your final title before submission.

This document implements the project plan: research questions, unified methods (with Study 1 vs Study 2 differences), results extracted from `inferential_participant_level_tests.csv` plus trial-level post-hoc context, two-phase discussion, and submission compliance notes. **Fill bracketed placeholders** (demographics, apparatus details, ethics) before submission.

---

## 1. Research questions and outcome hierarchy

### 1.1 Research questions

- **RQ1 (layout geometry):** For multi-panel virtual layouts in VR, do **alternative spatial arrangements** (Study 1: Flat, Cylindrical, Stacked; Study 2: Cylindrical vs Sphere) affect **performance and gaze-derived process measures** when participants perform the same task battery?
- **RQ2 (set size):** Does increasing the number of virtual panels from **4 to 15** worsen outcomes **overall** and **within each layout**, independent of geometry?
- **RQ3 (task moderation):** Do layout and set-size effects **differ** across **Exp1 (selection / search)**, **Exp2 (memory)**, and **Exp3 (puzzle / swap)**?

### 1.2 Primary outcomes (pre-specified for reporting priority)

Aligned with `outcome` keys in [`STATS_README.md`](STATS_README.md):

1. **`time_per_selection`** — task completion time for selection-oriented trials (search, memory trial duration where applicable, puzzle trial time as logged).
2. **`ttff`** (time to first fixation on target) — discovery latency from `unity_ttff_sec`.
3. **`block_error_rate`** — accuracy at the block level (errors per five selection trials in Exp1; analogous block structure in other experiments where computed).

### 1.3 Secondary / exploratory outcomes

Report after primaries, with clear **exploratory** labeling where appropriate:

- **`reengagement_after_overlook_sec`** — subset of trials; interpret cautiously.
- **`overlooked_view_samples_post_first_hit`** — process load after first target hit.
- **`delayed_binary_flag`** — binary “slow first view”; nonparametrics on 0/1 are exploratory.
- **`log_process_density`** — ratio-style measure when TTFF &gt; 0.

---

## 2. Abstract (draft; revise last)

**Background:** Spatial arrangement of multiple virtual displays in VR may interact with **set size** (number of panels) to affect search, memory, and manipulation performance. **Objective:** We report two within-subjects studies using the same task battery and analysis pipeline: Study 1 compares **three** layouts (Flat, Cylindrical, Stacked); Study 2 compares **two** curved layouts (**Cylindrical vs Sphere**). **Methods:** N ≈ 17 per study (participant-level inferential exports). For each session, we summarized each participant’s **per-cell median** across trials (or blocks for error rate), then tested **layout** (Friedman with three levels; Wilcoxon signed-rank for two layouts) and **4 vs 15 displays** (paired Wilcoxon). **Results:** **Set size** consistently affected **selection time** and **TTFF** in Exp1 in both studies; layout effects were **stronger in Study 1** (three-way geometry) than in Study 2 (cylinder vs sphere), where differences emerged mainly in **stratified** analyses (e.g., layout at fixed display count). **Memory (Exp2)** and **puzzle (Exp3)** showed fewer stable layout effects but repeated **4 vs 15** costs on time. **Conclusions:** **Panel count** is a dominant factor; **layout geometry** matters in a three-layout comparison and in specific cylinder–sphere contrasts—supporting a **two-phase** program: screen geometries broadly, then refine curved alternatives. **Limitations:** Trials are nested within participants; confirmatory inference should use **mixed models** in future work.

---

## 3. Introduction (outline for prose expansion)

- Multi-window and multi-panel UIs in VR must balance **visibility**, **head motion**, and **search cost** as panel count grows.
- Separate **layout** (how panels are arranged in 3D) from **set size** (how many panels).
- Contributions (fill with your voice):
  1. Empirical comparison of **three** and **two** layout families with **identical** tasks and metrics.
  2. **Gaze-derived** measures (TTFF, re-engagement, overlooked samples) alongside timing and errors.
  3. **Transparent** nonparametric analysis with **multiplicity** documented (Holm for layout post-hocs on trial-level pipeline; FDR families per `STATS_README.md`).

---

## 4. Methods

### 4.1 Apparatus and software

- **VR application:** Unity project with OpenXR (project name `layout_study01_openxr`). Layouts are instantiated as in [`TaskManagement.cs`](../../Scripts/TaskManagement.cs): `LayoutName` enum **Flat**, **Curve** (labeled **Cylindrical** in analysis exports), **Stack**, **Sphere**.
- **Hardware:** [Fill: HMD model, eye-tracking sampling rate, IPD, seated/standing, physical room.]
- **Interaction:** [Fill: controller vs gaze selection; dwell time if any.]

### 4.2 Layout conditions

| Study | Layouts compared | Rationale (two-phase narrative) |
|--------|------------------|-----------------------------------|
| **Study 1** | **Flat**, **Cylindrical**, **Stacked** | Screen **three** distinct geometries. |
| **Study 2** | **Cylindrical**, **Sphere** | Follow-up on **curved / surround** arrangements after Study 1. |

### 4.3 Set size

- **4** vs **15** virtual panels (`display_count` in enriched logs), crossed with layout within each study.

### 4.4 Tasks (Exp1–Exp3)

Consistent with [`STATS_README.md`](STATS_README.md) and [`Experiments.cs`](../../Scripts/Experiments.cs):

| Experiment | Code | Description (implementation-based) |
|------------|------|--------------------------------------|
| **Exp1** | Selection / search | [`SelectionTaskExperiment1.cs`](../../Scripts/Experiment1/SelectionTaskExperiment1.cs): layouts presented in randomized order; **five selection trials** per layout block (`numberOfTrials = 5`), **three** repeats per layout (`numberOfRepeatPerLayout = 3`). |
| **Exp2** | Memory | [`MemoryTaskExperiment2.cs`](../../Scripts/Experiment2/MemoryTaskExperiment2.cs): memory paradigm with views turned on/off per design; **three** repeats per layout. |
| **Exp3** | Puzzle / swap | [`TaskManagement.cs`](../../Scripts/TaskManagement.cs) puzzle/swap coroutine; trial time logged as swap-based completion (`NumberOfSwaps`). |

[Add: participant instructions verbatim, stimuli (icon sets), and any practice blocks.]

### 4.5 Design summary

- **Within-subjects** factorial structure: **layout** × **display count** × **experiment** (Exp1–3), with presentation order controlled in Unity [fill: counterbalancing scheme].
- **Study 1:** three layouts × two display counts × three experiments.
- **Study 2:** two layouts × two display counts × three experiments.

### 4.6 Participants

- **Study 1:** **n = 17** participants in participant-level tests (effective sample for complete median profiles; some strata have smaller **n**—see Results).
- **Study 2:** **n = 17** for most paired layout and 4-vs-15 tests; re-engagement and some Exp2 cells have smaller **n** (CSV `detail` column).

[Fill: recruitment source, age, vision criteria, ethics approval ID, compensation.]

### 4.7 Measures

Behavioral and gaze-derived outcomes match the pipeline (`STATS_README.md`):

- **time_per_selection**, **ttff**, **block_error_rate**, **reengagement_after_overlook**, **overlooked_view_samples_post_first_hit**, **delayed_binary_flag**, **log_process_density**.

### 4.8 Statistical analysis

- **Participant-level primary tests** (file: `StudyN/tables/inferential_participant_level_tests.csv`): each participant contributes **one median per stratum cell** (or block error rate as appropriate). **Friedman** test when **three layouts** (Study 1); **Wilcoxon signed-rank** for **paired 4 vs 15** and for **two layouts** (Study 2).
- **Trial-level pipeline** (session omnibus, Kruskal–Wallis / Mann–Whitney): exploratory; when layout Kruskal–Wallis was significant, **pairwise Mann–Whitney** with **Holm** correction (`inferential_posthoc_layout_pairwise_holm.csv`).
- **Multiplicity:** interpret **FDR** within **`fdr_family`** for uncorrected screening; pre-specify highlights in the paper narrative (`STATS_README.md`).
- **Limitation:** repeated trials violate independence; **linear mixed models** are recommended for confirmatory analyses.

---

## 5. Results (from participant-level CSVs; α = 0.05)

Report **medians** and **direction** in camera-ready tables using `inferential_group_descriptives_shapiro.csv` and effect files; below is a **test-level** summary for drafting.

### 5.1 Study 1 — Exp1 (selection / search)

**Session omnibus (participant medians, n = 17):**

| Factor | Outcome | Test | p | Significant |
|--------|---------|------|---|-------------|
| Layout | time_per_selection | Friedman | 0.011 | Yes |
| Layout | ttff | Friedman | 0.193 | No |
| 4 vs 15 | time_per_selection | Wilcoxon | 0.0021 | Yes |
| 4 vs 15 | ttff | Wilcoxon | 0.00134 | Yes |

**Layout within display count:**

- **4 displays:** layout → **time_per_selection** *p* = 0.00164 (Friedman).
- **15 displays:** layout → **time_per_selection** *p* = 0.0284; **ttff** *p* = 0.00630; **delayed_binary_flag** *p* = 0.0498 (Friedman).

**Display count within layout (4 vs 15):**

- **Cylindrical:** time *p* = 0.00038; ttff *p* = 0.00107.
- **Flat:** time *p* = 0.00269.
- **Stacked:** no significant participant-level 4 vs 15 on time or ttff in this export.

**Trial-level post-hoc (Holm) for context — Study 1 Exp1 session omnibus `time_per_selection`:** Cylindrical vs Flat Holm *p* = 0.028; Flat vs Stacked Holm *p* = 0.0038 (higher time for Stacked vs Flat); Cylindrical vs Stacked not significant. For **ttff** omnibus layout n.s. at participant level, but trial-level Holm showed Cylindrical vs Stacked and related pairs—treat as **supporting / exploratory** relative to participant-level primaries.

### 5.2 Study 1 — Exp2 (memory)

**Session omnibus:**

- **4 vs 15:** **time_per_selection** *p* = 0.00464; **ttff** *p* = 0.03125 (Wilcoxon, note small **n** = 6 for ttff paired stratum); **delayed_binary_flag** *p* = 0.0196.
- **Layout:** **block_error_rate** Friedman *p* = 0.00606.

**Layout within 15 displays:** **block_error_rate** *p* = 0.000335 (Friedman).

**Trial-level post-hoc — block_error_rate:** Cylindrical vs Stacked and Flat vs Stacked significant (Holm); interpret together with **median ties at zero** in exported descriptives.

### 5.3 Study 1 — Exp3 (puzzle / swap)

**Session omnibus:** **4 vs 15** on **time_per_selection** *p* = 0.0129.

**Display within layout:** **Flat** *p* = 0.000305; **Stacked** *p* = 0.0395 for 4 vs 15 on time.

### 5.4 Study 2 — Exp1 (selection / search)

**Session omnibus:**

- **Layout** (Cylindrical vs Sphere): **not** significant for time or ttff (*p* &gt; 0.22).
- **4 vs 15:** **time_per_selection** *p* = 0.00790; **ttff** *p* = 0.00665; **reengagement_after_overlook** *p* = 0.0353 (n = 14 pairs).

**Layout within display:**

- **4 displays:** **time_per_selection** *p* = 0.0395 (Wilcoxon).
- **15 displays:** **ttff** *p* = 0.0232 (Wilcoxon).

**Display within layout (4 vs 15):** **Cylindrical** and **Sphere** both show significant **time** and **ttff** (*p* &lt; 0.05 for listed tests).

### 5.5 Study 2 — Exp2 (memory)

**Session omnibus:** **4 vs 15** **time_per_selection** *p* = 0.00209; **ttff** *p* = 0.03125 (n = 6); **delayed_binary_flag** *p* = 0.0339.

**Display within layout:** **Cylindrical** time *p* = 0.00385; **delayed_binary_flag** *p* = 0.0339.

### 5.6 Study 2 — Exp3 (puzzle / swap)

**Session omnibus:** **layout** **time_per_selection** *p* = 0.0267; **4 vs 15** *p* = 0.00557.

**Display within layout — Sphere:** **time_per_selection** *p* = 0.0110 for 4 vs 15.

### 5.7 Cross-study synthesis (short bullets for Discussion)

- **Set size (4 vs 15)** repeatedly affects **time** and **TTFF** in **Exp1** and **Exp2** in both studies—strongest cross-cutting finding.
- **Study 1** shows **broader layout effects** (three layouts) on **time** in Exp1 and **errors** in Exp2 (block rate).
- **Study 2** shows **fewer omnibus layout** differences on time/TTFF, but **significant** layout contrasts in **some strata** (e.g., Exp1 at 4 or 15 panels; Exp3 session omnibus on time)—consistent with a **narrower** geometric comparison (cylinder vs sphere) being more subtle than three-way Flat/Cylinder/Stacked differences.

---

## 6. Figures and tables to include

Paths relative to `Assets/OutputLog/behavior_log_inferential_stats/` (see [`STATS_README.md`](STATS_README.md)):

| Purpose | Study 1 | Study 2 |
|---------|---------|---------|
| Session omnibus p-values | `Study1/figures/inferential_pvalue_heatmaps_session_Study1.png` | `Study2/figures/inferential_pvalue_heatmaps_session_Study2.png` |
| FDR q heatmaps | `Study1/figures/inferential_fdr_q_heatmaps_session_Study1.png` | `Study2/figures/inferential_fdr_q_heatmaps_session_Study2.png` |
| Layout × display stratification | `Study1/figures/inferential_layout_within_display_Study1.png` | `Study2/figures/inferential_layout_within_display_Study2.png` |
| 4 vs 15 within layout | `Study1/figures/inferential_display_within_layout_Study1.png` | `Study2/figures/inferential_display_within_layout_Study2.png` |
| Participant-level session comparison | `Study1/figures/inferential_participant_level_pvalue_heatmaps_session_Study1.png` | `Study2/figures/inferential_participant_level_pvalue_heatmaps_session_Study2.png` |
| Post-hoc layout pairs (Holm) | `Study1/figures/inferential_posthoc_layout_median_diffs_holm_005_Study1_Exp1.png` … **Exp3** | As generated for Study 2 if present |
| Cliff’s delta (4 vs 15) | `Study1/figures/inferential_cliffs_delta_4_vs_15_significant_Study1_Exp1.png` … | Study 2 counterparts |

**Tables:** merge from `inferential_tests_long_enriched.csv`, `inferential_participant_level_tests.csv`, and `inferential_posthoc_layout_pairwise_holm.csv` for supplementary material.

---

## 7. Discussion: two-phase program

**Motivation for Study 2:** Study 1 establishes that **geometry and set size jointly** matter for multi-panel VR UIs, with **Flat vs Stacked** and **Cylindrical** roles visible in **three-layout** tests and Holm post-hocs. Study 2 holds tasks and metrics constant but **restricts layout** to **two curved** arrangements—**Cylindrical** vs **Sphere**—to isolate **surround** curvature without conflating with flat or stacked baselines.

**What replicated across phases:** **Increasing from 4 to 15 panels** degrades performance on **time** and **TTFF** in search (Exp1) and often in memory (Exp2)—supporting **set size** as a **first-order** design knob.

**What differs:** **Three-layout** Study 1 yields **clearer omnibus layout** signals for **time** (Exp1) and **error** (Exp2) than **two-layout** Study 2, where **layout** effects are **weaker at session level** but appear **in stratified** analyses—appropriate for a **follow-up** that tests **finer** geometric differences.

**Design guidance (tentative):** Prefer **fewer panels** when possible; when **panel count is high**, **layout** choice still modulates **selection time** and (in Study 1) **errors** in memory—exact ranking depends on stratum; tie to **post-hoc medians** in tables.

**Future work:** **Mixed-effects models** with random intercepts per participant; **power** analysis for 2-layout vs 3-layout designs; **qualitative** workload (e.g., NASA-TLX) if collected.

---

## 8. Limitations

1. **Non-independence** of trials within participants.
2. **Multiple tests**—use **fdr_family** and pre-declared highlights.
3. **Small n** in some cells (e.g., Exp2 ttff **n* = 6**, re-engagement subsets).
4. **Binary / rank** tests on **delayed flag** are exploratory.
5. **Terminology:** Unity `Curve` ≡ **Cylindrical** in CSVs—keep consistent in all figures.

---

## 9. SUI 2026 submission compliance checklist

**Verify on the official conference site before submitting** ([ACM SUI 2026](https://sui.acm.org/2026/)):

| Item | Status | Notes |
|------|--------|--------|
| **Deadline** | Confirm | Third-party listings cite **May 22, 2026** for full papers—**verify** on official CFP. |
| **Conference dates / location** | Oct 10–11, 2026, Bari, Italy (per public site) | Confirm in CFP. |
| **Page / word limit** | Confirm | ACM **Primary Article Template** (single-column) is standard for SIGCHI venues—**use the template linked from the Call for Papers**. |
| **Anonymization** | Required for review | Remove author names, institution identifiers, and non-anonymized repo links from the submission PDF; use blind supplementary if required. |
| **Supplementary material** | Confirm allowance | Archive **analysis scripts** (`behavior_log_pipeline/`) and **de-identified** data per ethics. |
| **Video** | Confirm | Many SUI tracks expect a **30–60 s** preview or figure video—check CFP. |
| **ACM rights / copyright** | Follow PCS instructions | Use official ACM template and `rights` workflow at acceptance. |

**Action:** When the **official CFP PDF/HTML** is final, replace this section with **exact** page counts, optional sections, and PCS upload steps.

---

## Document history

- Generated to implement the internal plan *SUI 2026 full paper: two-phase layout × set-size studies*; **do not** treat as camera-ready until placeholders are filled and co-authors edit.
