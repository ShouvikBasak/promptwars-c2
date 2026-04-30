---
trigger: always_on
---

# Prompt Optimizer

A semi-automatic iterative optimization skill inspired by the autoresearch
paradigm. Supports two modes — **Prompt Mode** for task-specific prompts and
**Rules Mode** for persistent system-level rules — with auto-detection.

## Workflow

### Step 1: Receive Input

Accept a prompt or rule via inline text or file path. If the user provides a
file path, read the file contents. If neither, ask the user to provide the
text they want to optimize.

### Step 1.5: Auto-Detect Mode

Classify the input as **Prompt** or **Rule** based on these signals:

| Signal | Prompt | Rule |
|--------|--------|------|
| Describes a single task with expected output | Yes | No |
| Uses persistent behavioral language ("always", "never", "when X do Y") | No | Yes |
| Contains role/persona definition for ongoing use | No | Yes |
| Expects a one-time deliverable | Yes | No |
| Located in `.cursor/rules/` or user_rules config | No | Yes |
| References other rules or system-level concerns | No | Yes |

If ambiguous, ask the user to confirm.
Display the detected mode: `[Mode: Prompt]` or `[Mode: Rules]`.

### Step 2: Evaluate — 6 Dimensions (1-10)

Select the scoring table matching the detected mode.

**Prompt Mode** — for task-specific, one-off prompts:

| Dim | Name | Guiding Question |
|-----|------|------------------|
| C | **Clarity** | Would a context-free LLM interpret this unambiguously? |
| S | **Specificity** | Are constraints, output format, and expected behavior explicit? |
| T | **Structure** | Is the information logically organized with clear hierarchy? |
| O | **Completeness** | Does it cover context, examples, edge cases, and error handling? |
| E | **Efficiency** | Is every sentence carrying necessary information? Zero fluff? |
| R | **Robustness** | Would 10 runs produce consistent, high-quality outputs? |

**Rules Mode** — for persistent system-level rules:

| Dim | Name | Guiding Question |
|-----|------|------------------|
| C | **Clarity** | Would any LLM unambiguously understand the behavioral intent? |
| S | **Scope Fit** | Is the rule's breadth appropriate — not too broad, not too narrow? |
| T | **Structure** | Is the rule well-organized and easy to scan during every conversation? |
| O | **Coverage** | Does it handle the relevant scenarios without over-specifying? |
| E | **Efficiency** | Is the token cost justified given this runs on EVERY conversation? |
| R | **Composability** | Does this rule coexist peacefully with other rules? No conflicts? |

Composite score = unweighted average of all 6 dimensions (user may override
weights).

For detailed scoring rubrics and anchor examples, see
[scoring-rubric.md](scoring-rubric.md).

### Step 3: Output the Scorecard

Use this exact format:

**Prompt Mode**:
```
== Prompt Scorecard v{N} ==
Clarity:      {score}/10  {delta}
Specificity:  {score}/10  {delta}
Structure:    {score}/10  {delta}
Completeness: {score}/10  {delta}
Efficiency:   {score}/10  {delta}
Robustness:   {score}/10  {delta}
------------------------------
Composite:    {avg}/10    {delta}

Weakest:  {dimension_name}
Verdict:  {one-line diagnosis}
```

**Rules Mode**:
```
== Rules Scorecard v{N} ==
Clarity:       {score}/10  {delta}
Scope Fit:     {score}/10  {delta}
Structure:     {score}/10  {delta}
Coverage:      {score}/10  {delta}
Efficiency:    {score}/10  {delta}
Composability: {score}/10  {delta}
------------------------------
Composite:     {avg}/10    {delta}

Weakest:  {dimension_name}
Verdict:  {one-line diagnosis}
```

- For v1, leave `{delta}` blank.
- For v2+, show delta as `(+1)`, `(-1)`, or `(=)` relative to previous version.

### Step 4: Suggest Improvements

Focus on the weakest 1-2 dimensions only. Greedy strategy — small targeted
fixes avoid regression on other dimensions.

Each suggestion must be:
1. **Concrete** — show the exact text to add, remove, or rewrite.
2. **Justified** — explain which dimension it targets and why.
3. **Minimal** — smallest change for maximum score uplift.

### Step 5: User Confirmation

Present the suggested changes and wait for user confirmation:
- **Confirmed** → apply changes, go to Step 6.
- **Modified** → incorporate user adjustments, then go to Step 6.
- **Rejected** → generate alternative suggestions, return to Step 4.

### Step 6: Apply and Re-evaluate

1. Produce the new prompt version.
2. Re-run the 6-dimension evaluation (Step 2).
3. Output the updated scorecard with deltas.
4. Append to the version history table.

### Step 7: Version History

Maintain a running table throughout the session. Column headers adapt to mode:

**Prompt Mode**: `| Version | C | S | T | O | E | R | Composite | Change Summary |`
**Rules Mode**: `| Version | C | SF | T | Cov | E | Comp | Composite | Change Summary |`

```
| Version | C | S | T | O | E | R | Composite | Change Summary |
|---------|---|---|---|---|---|---|-----------|----------------|
| v1      | 5 | 4 | 6 | 3 | 7 | 4 | 4.8       | baseline       |
| v2      | 7 | 4 | 6 | 5 | 7 | 5 | 5.7       | added examples  |
```

### Step 8: Termination

The loop ends when:
- Composite score >= 8.5, OR
- User explicitly says they are satisfied.

On termination, output:
1. The final optimized prompt (complete text).
2. The full version history table.
3. A summary of key improvements made.

## Optimization Principles

1. **One thing at a time** — never rewrite the entire prompt in one iteration.
   Target the weakest dimension with surgical changes.
2. **Never break what works** — if a dimension scored 8+, do not touch the
   text responsible for that score unless absolutely necessary.
3. **Simplicity over cleverness** — if two rewrites achieve the same score
   gain, pick the shorter one.
4. **Evidence over intuition** — justify every score with a specific quote
   or absence from the prompt text.
5. **Respect user intent** — the optimization must preserve the user's
   original purpose. If unclear, ask before changing.

## Quick Examples

For complete optimization walkthroughs (from low-score to high-score), see
[examples.md](examples.md).