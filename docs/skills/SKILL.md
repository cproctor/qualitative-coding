---
name: qc
description: Use qc (qualitative-coding), a CLI for qualitative data analysis (QDA) — coding text corpora, querying codes/statistics, inter-rater agreement, and AI-assisted autocoding. Use when the user asks about a qc project (a directory with settings.yaml/corpus/codebook.yaml/a .sqlite3 db), wants code frequencies, coded excerpts, co-occurrence, agreement/F1 between coders, or to run/evaluate autocode classifiers.
---

# qc: qualitative-coding CLI

`qc` manages a QDA project: a corpus of text files, a hierarchical codebook,
and a sqlite3 database recording which lines each coder tagged with which
codes. Treat the CLI as the only supported interface — don't read/write the
sqlite3 db, corpus files, or codebook.yaml directly except via `qc` commands
(exception: reading corpus/codebook files is fine; *modifying* them outside
`qc corpus update` / `qc codebook` will desync line numbers).

Run `qc --help` or `qc <command> --help` for exhaustive/current options — this
file covers the common surface. Every command accepts `--settings PATH` (`-s`)
or the `QC_SETTINGS` env var if not run from the project root.

## Getting oriented in a project

- `qc check` — verifies project assets exist (settings.yaml, corpus dir, db).
- `qc version` — prints installed version.
- `qc coders` — lists coder names that have contributed codes.
- `qc corpus list` (`ls`) — one corpus file path per line.
- `qc codes list` (`ls`) [`--expanded`] — one code per line (`--expanded` shows
  full `parent:child` paths).

These all print plain, line-oriented text — trivial to parse without JSON.

## Getting structured output

Most reporting commands (`codes stats`, `codes crosstab`, `codes agreement`,
`autocode describe`, `autocode similar`) produce **tabular** data: use
`--format tsv` (`-m tsv`) to print it as parseable tab-separated values, or
`--outfile FILE.csv` (`-o`) to write CSV directly. `--format` accepts any
[tabulate](https://pypi.org/project/tabulate/) style (`github`, `html`,
`latex`, `plain`, ...); `tsv`/`--outfile` are the ones to reach for when you
need to parse the result rather than display it.

`qc codes find` is the exception — its results (coded excerpts with
surrounding context) aren't tabular, so instead of `--format` it has
**`--json` (`-j`)**: prints a single JSON array to stdout, one record per
(code, line-or-paragraph-or-document) match:

```json
[
  {"document": "corpus/interview.txt", "line": 42, "code": "equity",
   "text_lines": [40, 45], "text": "...surrounding lines including line 42..."}
]
```

- `--unit line` (default) records: `document`, `line` (0-indexed), `code`,
  `text_lines` (`[start, end)` slice used for context), `text`.
- `--unit paragraph` records: `document`, `paragraph` (`[start, end)` line
  range), `code`, `text`.
- `--unit document` records: `code` and the document path **under the key
  `"docuement"` (sic — known typo in this field name, not `"document"`)**.
  Handle both spellings defensively if unit may vary.
- `--json` is incompatible with `--no-codes` and `--no-line-numbers`.

## Common query filters

Available on most `codes`/`corpus` reporting commands:

- **Corpus filter**: `--pattern SUBSTR` (`-p`) matches file paths;
  `--filenames FILE` (`-f`) restricts to paths listed one-per-line in `FILE`.
- **Code filter**: positional `CODES...`; `--coder NAME` (`-c`, repeatable);
  `--recursive-codes` (`-r`) includes child codes; `--depth N` (`-d`) caps
  tree depth; `--recursive-counts` (`-a`) sums child-code counts into parent
  counts (independent of `-r`, which controls *which* codes are reported).
- **Unit of analysis**: `--unit line|paragraph|document` (`-n`); falls back to
  the `unit` key in settings.yaml (default `line`). Paragraphs are
  blank-line-delimited.
- **Display**: `--expanded` (`-e`) shows full code paths; `--format` (`-m`)
  tabulate style; `--outfile` (`-o`) CSV export.

## Command reference

### Project / corpus

- `qc init` — create/initialize a project in the cwd.
- `qc corpus import PATH [--recursive -r] [--importer -i {pandoc,vtt,verbatim}] [--corpus-root -c DIR]`
  — copy files into the corpus and register them.
- `qc corpus move OLD NEW` (`mv`), `qc corpus remove PATH` (`rm`, `--recursive`)
  — keep the db in sync; never `mv`/`rm` corpus files directly.
- `qc corpus update PATH [--new FILE | (git-tracked edit)] [--dryrun -d]` —
  re-syncs code line-numbers after a document changes.
- `qc corpus anonymize [--key -k FILE] [--out-dir -o DIR] [--update -u] [--reverse]`
  — NER-based PII scrubbing (needs `ai` extra).
- `qc codebook` (`cb`) — reconcile codebook.yaml with codes actually in use.
- `qc export` — bundle project as `.qpdx`.
- `qc upgrade [--version -v X]`.

### Coding

- `qc code CODER [--first -1 | --random -r] [--recover | --abandon]` — opens
  editor to hand-code a document.
- `qc code CODER --auto -c TRAIN_CODER [-1|-r]` — pre-populate suggestions
  (from a trained classifier) before opening the editor for review.
- `qc code CODER --auto --no-edit [--threshold F] [--no-hierarchy]` — bulk
  predict without an editor: writes predictions for every corpus doc with no
  existing human coding, under coder name `CODER`.
- `qc coders delete CODER` — deletes all of a coder's codes (e.g. to discard a
  bad autocode run).
- `qc memo CODER [-m "title"] [--list -l]`.

### Querying codes

- `qc codes stats [CODES...] [--by-coder -C] [--by-document] [--max N] [--min N] [--zeros] [--total-only]`
  — usage counts (pivoted by coder/document if requested).
- `qc codes find [CODES...] [-B before] [-C after] [--no-codes] [--no-line-numbers] [--json -j]`
  — coded excerpts in context; see JSON section above.
- `qc codes crosstab [CODES...] [--probs -0] [--compact -z] [--tidy]` (`ct`)
  — co-occurrence within the unit of analysis, as counts or probabilities.
- `qc codes rename OLD NEW...` — merge/rename codes across all code files.
- `qc codes agreement -c CODER1 -c CODER2 [--metric alpha|kappa|f1|cv] [--folds N]`
  — see Agreement metrics below (needs `ai` extra).

### Autocode (needs the `ai` extra; requires `qc autocode embed` first)

- `qc autocode init` — interactive setup of embedding API + hyperparameters.
- `qc autocode embed [--force] [-p pattern] [-f filenames]` — embed corpus
  (cached; `--force` re-embeds).
- `qc autocode describe -c CODER [--recursive-codes] [--outfile]` — shows
  current classifier config + per-code training-data summary without training.
- `qc autocode CODER --train-coders C1 C2 [--context N] [--uncertainty-threshold F]`
  (alias `ac`) — active-learning loop: shows the most-uncertain line + ranked
  candidate codes, retrains after each answer.
- `qc autocode outliers -c CODER [--recursive-codes] [-n N]` — per code, the
  N lowest-confidence coded lines (likely miscodes / edge cases).
- `qc autocode cohesion -c CODER` — per-code semantic tightness (fraction of
  embedding variance on first principal component; low = maybe split the code).
- `qc autocode similar -c CODER [--threshold F]` — code pairs whose
  classifiers generalize to each other's examples (merge/subset candidates).

### Agreement metrics (`qc codes agreement`)

- `alpha` (default): Krippendorff's Alpha, multi-coder, handles missing data.
- `kappa`: Cohen's Kappa, exactly 2 coders.
- `f1`: Precision/Recall/F1, exactly 2 coders, **first `-c` coder = ground
  truth** (e.g. `-c human -c auto.v1` evaluates `auto.v1` against `human`).
- `cv`: k-fold cross-validation (`--folds N`, default 5) estimating
  precision/recall/F1 on unseen data, *before* writing bulk predictions.
  Needs embeddings. Meaningful once a code has ~10-20+ positive examples;
  `autocode.min_examples` (default 5) is the hard floor for training at all.
- Rule of thumb for alpha/kappa: >0.80 excellent, >0.60 acceptable, <0.40
  substantial disagreement.

## Kinds of questions this lets you answer

- "What codes exist, and how are they used?" → `qc codes list --expanded`,
  `qc codes stats --recursive-codes --depth N`.
- "Show me every place code X (and its children) was applied." →
  `qc codes find X --recursive-codes --json`, then read the JSON records.
- "How often do codes X and Y co-occur?" → `qc codes crosstab X Y --probs`.
- "Do coders chris and anna agree?" → `qc codes agreement -c chris -c anna --metric alpha`.
- "How good are the autocode predictions vs. human coding?" →
  `qc codes agreement -c human -c auto.v1 --metric f1`, or `--metric cv`
  before predicting at all.
- "Which coded examples look like mistakes?" → `qc autocode outliers -c CODER -n N`.
- "Is code X coherent, or should it be split?" → `qc autocode cohesion -c CODER`.
- "Should codes X and Y be merged?" → `qc autocode similar -c CODER`.
- "Apply predicted codes to everything not yet coded." →
  `qc code auto.vN --auto --no-edit -c TRAIN_CODER`, then inspect with
  `qc codes agreement` / `qc autocode outliers` before trusting it.
- "Filter all of the above to a subset of documents / a round of coding." →
  add `--pattern SUBSTR` and/or `-c CODER` to any query command.

## Gotchas

- Commands needing `agreement`, `autocode *`, or `corpus anonymize` require
  the optional `ai` extra (`pip install "qualitative-coding[ai]"` /
  `uv tool install "qualitative-coding[ai]"`) plus, for `anonymize`, a spaCy
  language model.
- `qc autocode *` commands require `qc autocode embed` to have already run.
- Line numbers in `codes find --json` output are relative to the unit of
  analysis in effect (`--unit`/`unit` setting), not always raw file lines.
- Never move/delete/edit corpus files outside `qc corpus move|remove|update` —
  codes are indexed by line number and will desync.
