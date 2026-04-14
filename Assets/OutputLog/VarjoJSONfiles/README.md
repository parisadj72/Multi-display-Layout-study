# Varjo condition JSON (behavior + gaze pipelines)

These files map **Unity block order** to Varjo condition labels (e.g. `2by2Stack`, `3by5Flat`) so the behavioral pipeline can attach **`display_count`** (4 vs 15), **`condition_name`**, and **`layout_family`** to trials and blocks.

## Naming (current convention)

Use the **same stem as the Unity session log**, with a `.json` extension:

|`StudyNsubject##ExpM.txt` (main log)|Condition JSON|
|---|---|
|`Study1subject06Exp1.txt`|`Study1subject06Exp1.json`|
|`Study1subject06Exp2.txt`|`Study1subject06Exp2.json`|
|`Study1subject06Exp3.txt`|`Study1subject06Exp3.json` (optional; see fallbacks below)|

- **`N`** — Study 1 or Study 2 (must match the log and the `"study"` field inside the JSON, e.g. `"Study1"`).
- **`##`** — Subject id, **two digits** (participant 6 → `06`). This matches the behavioral parser’s pairing with logs.
- **`M`** — Task / session: **1** selection/search, **2** memory, **3** puzzle (swap).

The JSON object should include a **`conditions`** array; each element is a dict with a **`condition`** string. **Array index `i`** must match **block index `i`** in the Unity log (after sorting blocks by `block_index`). Only the **`condition`** strings are required for behavioral enrichment; `targets` / timing are for gaze/video tooling.

**`"study"` inside the file** should match the **`StudyN`** in the filename (`Study1` vs `Study2`). The behavioral pipeline **opens the file by name** (derived from the Unity log path), not by re-deriving the study from JSON. If Varjo export metadata disagrees with the real session, fix the field so archives stay self-consistent.

## Exp3 (puzzle) without a dedicated JSON

If **`StudyNsubject##Exp3.json`** is missing or has no usable `conditions`, the behavioral pipeline tries, in order:

**`Exp3.json` → `Exp2.json` → `Exp1.json`** for the **same** `StudyN` and subject.

Use this only when block order is the same across those sessions; otherwise add a real **`…Exp3.json`**.

## Raw Varjo exports

Files named like `varjo_capture_*.json` may be kept here for reference; the behavioral pipeline does not load them unless you point another script at them explicitly.
