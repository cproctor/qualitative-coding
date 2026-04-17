# Autocode: Implementation Plan v2 (revised)

## User Story: Full Autocoding Workflow

You are a researcher with 40 interview transcripts imported into a `qc` project. You have completed open coding on 10 of them as `human.v1`, producing ~80 codes organized in a tree. You want to extend this coding to the remaining transcripts more efficiently.

### Phase 1: Establish a baseline

Code manually until you have a reasonable number of examples per code. There is no fixed rule, but 10–20 examples per code you care about is a reasonable target.

```bash
qc code human.v1 --first   # repeat until you've coded enough documents
qc codes stats -ra          # review the code tree and counts
```

### Phase 2: Check autocoding readiness

Before committing to embedding the corpus, check whether you have enough coded examples per code to train useful classifiers. `qc codes stats -ra` shows example counts; `autocode_min_examples` (default 5) is the floor, but 10–20 per code gives meaningfully better classifiers. This check costs nothing — no API calls needed.

```bash
qc codes stats -ra -c human.v1   # check example counts per code
```

Once you're satisfied, embed the corpus. This is the one real upfront cost — commit to this before any autocoding work.

```bash
qc autocode embed
# Embedded 12,840 lines across 40 documents. Cache saved to embeddings/.
```

### Phase 3: Cross-validate (optional)

With embeddings in hand, run cross-validation to get a per-code quality estimate before writing any predictions to the database:

```bash
qc codes agreement -c human.v1 --metric cv
```

Output:

```
Code                      Examples    Precision    Recall    F1
----------------------  ----------  -----------  --------  ----
equity                          14         0.82      0.78  0.80
participation                   11         0.71      0.65  0.68
identity_categories              8         0.60      0.55  0.57
scratch                          4        (skipped — too few examples)
```

Codes with low F1 or skipped codes need more hand-coded examples before autocoding will be reliable. Continue manual coding and re-run as needed.

### Phase 4: Bulk apply predictions to new documents

Apply trained classifiers to documents not yet coded by any human coder. `--auto --no-edit` writes predictions directly without opening an editor; `-p` scopes to matching documents.

```bash
qc code auto.v1 --auto --no-edit -c human.v1 -p round2
# Wrote 1,240 predictions across 22 codes for 30 documents.
```

Because `auto.v1` is a separate coder, all existing `qc codes` commands can filter by coder:

```bash
qc codes stats -ra --coders auto.v1            # see what was predicted
qc codes find equity -r --coders auto.v1       # inspect predictions for a code
qc codes stats -ra --coders human.v1 auto.v1  # combined view
```

To discard all autocode predictions and start over:

```bash
# Drop the coder (a new command, qc coders delete):
qc coders delete auto.v1
# Or, if using git, simply revert the database:
git checkout -- qualitative_coding.sqlite3
```

### Phase 5: Interactive active learning

The model now knows what it's uncertain about. Use the active learning loop to code the lines where the model is most confused. You code as `human.v2`; training uses all prior human and auto coding.

```bash
qc autocode human.v2 --train-coders human.v1 auto.v1
```

The terminal shows the most uncertain line in context (with surrounding lines for readability), a ranked list of candidate codes and their confidence scores, and a prompt:

```
─────────────────────────────────────────────────────────────────
Document: round2/teacher_3.txt  [Lines 42–48]
─────────────────────────────────────────────────────────────────
  42  they started coming to me and asking questions about
  43  whether their kids could learn to program, and I thought
→ 44  every student deserves that opportunity, regardless of  
  45  whether they come from a wealthy family or not. I kept
  46  saying, this is for everyone.
─────────────────────────────────────────────────────────────────
Candidate codes (by confidence):
  equity                  0.58  ← most uncertain
  every_student           0.41
  participation           0.38
  rationales              0.72

Enter codes (comma-separated), or press Enter to skip: equity, every_student
```

After each response, the model is retrained and moves to the next most uncertain line. Press Ctrl-C or type `quit` to end the session. The session continues until all remaining uncertainty falls below a threshold.

Each annotation is written to the database immediately — quitting at any point loses no work.

### Phase 6: Second-generation predictions

After several active learning sessions, run another bulk pass:

```bash
qc code auto.v2 --auto --no-edit -c human.v1 auto.v1 human.v2
```

### Phase 7: Evaluate final quality

Compare predictions against a held-out set of manually coded documents using `qc codes agreement`:

```bash
qc codes agreement \
  -c human.v2 auto.v2 \
  --metric f1 \
  --codes equity participation identity \
  --recursive-codes \
  --pattern round2
```

### Versioning strategy

The coder naming convention (`human.v1`, `auto.v1`, etc.) is a recommendation, not enforced. Autocode predictions can be written to any coder name, including one already used for human coding. In fact, online learning (where autocode's own predictions are included in subsequent training) naturally uses a single coder name throughout — git provides the rollback mechanism. The distinct-name convention is recommended when you want to be able to drop a round of predictions cleanly with `qc coders delete`, but it is not required.

### Additional embedding analytics

The cached embeddings enable several diagnostic commands that don't require any new API calls:

- **`qc autocode outliers [CODES]`**: for each code, find coded lines whose embeddings are far from the centroid of that code — flagging likely miscodes for human review.
- **`qc autocode density [CODES]`**: report per-code cohesion (mean pairwise distance or intra-cluster variance). Dense clusters indicate well-defined codes; scattered distributions suggest a vague or over-broad code that may benefit from splitting.
- **`qc autocode similar`**: find pairs of codes whose centroids are close in embedding space — candidates for merging.

These are lower-priority than the core workflow but naturally fit in the `qc autocode` command group.

---

## Architecture Overview

The autocode system has four concerns:

1. **Embedding**: call an external API to embed windowed corpus lines; cache results on disk.
2. **Training**: fit per-code classifiers on hand-coded lines' embeddings.
3. **Inference**: apply classifiers to corpus lines, with tree-descent post-processing.
4. **Active learning**: rank all lines by per-code uncertainty; present highest-uncertainty items interactively.

The main entry point for a coding session is `qc autocode CODER` (analogous to `qc code CODER`). Supporting utilities are subcommands: `qc autocode embed`, `qc autocode describe`, and the analytics commands `qc autocode outliers`, `qc autocode density`, `qc autocode similar`. Quality evaluation lives in `qc codes agreement`. Bulk prediction and human-reviewed prediction both use `qc code --auto`, distinguished by `--no-edit`.

No trained model is persisted to disk. Classifiers are rebuilt on demand from the embeddings cache and the current state of the database — training takes milliseconds on cached embeddings, so this is always fast. The full description of the latent model (hyperparameters + per-code training statistics) is available via `qc autocode describe` and is logged to `qc.log` whenever predictions are written. Embeddings are cached in a project-level `embeddings/` directory, excluded from version control. All predictions are written as `CodedLine` records under a configurable coder name, making them visible to all existing `qc codes` commands.

---

## New Settings Keys

```yaml
# settings.yaml additions (all optional, with defaults shown)
autocode_embeddings_dir: embeddings           # cache directory (add to .gitignore)
autocode_window: [2, 2]                        # [lines_before, lines_after]
autocode_min_examples: 5                       # skip codes with fewer examples
autocode_confidence_threshold: 0.6             # minimum confidence to predict
autocode_child_threshold: 0.4                  # minimum confidence to prefer child over parent

# Embedding API (OpenAI-compatible)
autocode_api_base: http://localhost:1234/v1    # LMStudio, Ollama, or OpenAI
autocode_api_key: ""                           # empty string for local servers
autocode_api_model: text-embedding-nomic-embed-text-v1.5  # model name on the server
```

No `autocode_model_file` setting: classifiers are always built fresh from the embeddings cache and coded lines. `qc autocode describe` documents the exact configuration that determines the classifier.

The API key can alternatively be set via the `QC_AUTOCODE_API_KEY` environment variable (following the pattern of `QC_SETTINGS`).

---

## No Database Migration Required

Embeddings are stored on disk, not in SQLite. No `confidence` column is added to `CodedLine` for now — confidence values are not persisted, since the classifier is always rebuilt on demand and scores can be recomputed. This keeps the migration surface small.

If confidence storage in the database is desired later (e.g., for `qc codes stats --by-confidence`), it can be added in a future migration without affecting the autocode MVP.

A new `qc coders delete CODER` command is needed to support discarding autocode predictions. This operates on the existing `Coder` and `CodedLine` tables using the existing `QCCorpus.delete_coder` method (already implemented in `corpus.py:325`).

---

## New Module: `qualitative_coding/autocode/`

```
qualitative_coding/autocode/
├── __init__.py
├── embedder.py      # CorpusEmbedder: calls API, manages disk cache
├── trainer.py       # AutocodeTrainer: fits classifiers, saves/loads model pickle
├── predictor.py     # AutocodePredictor: tree-descent inference, writes CodedLines
└── active.py        # UncertaintySampler: margin sampling across all codes and lines
```

### `embedder.py`

```python
class CorpusEmbedder:
    def __init__(self, corpus: QCCorpus):
        # reads autocode_* settings; initializes openai.OpenAI(base_url=..., api_key=...)
        ...

    def embed_corpus(self, force=False, pattern=None, file_list=None):
        """
        For each corpus document (filtered by pattern/file_list):
          - check cache validity: compare Document.file_hash with sidecar hash
          - if valid and not force: skip
          - otherwise: read document lines, build windowed text per line,
            call API in batches (e.g., 100 texts per request), write .npy + sidecar .json
        Shows tqdm progress bar over documents.
        """
        ...

    def get_embeddings(self, document_id) -> tuple[np.ndarray, list[int]]:
        """
        Loads cached embeddings for a document.
        Returns (matrix of shape [n_lines, n_dims], list of line numbers).
        Raises if cache is missing or stale.
        """
        ...

    def cache_path(self, document_id) -> Path:
        """Returns path to .npy file for a document."""
        ...

    def sidecar_path(self, document_id) -> Path:
        """Returns path to .json sidecar for a document."""
        ...

    def is_cache_valid(self, document_id) -> bool:
        """
        Returns True if sidecar exists AND sidecar hash matches Document.file_hash.
        Cache entries are always whole-document: a document is either fully cached
        or absent. There is no partial state. This means the check is binary —
        no need to verify which lines are present.
        """
        ...
```

Cache file layout:
```
embeddings/
  round1_admin.npy            # float32 matrix, shape [n_lines, n_dims]
  round1_admin.json           # {"model": "...", "window": [2,2], "hash": "abc123", "lines": [0,1,2,...]}
  round2_teacher_3.npy
  round2_teacher_3.json
```

The `lines` field in the sidecar maps matrix rows to corpus line numbers (needed because blank lines produce no embedding — they are skipped).

### `trainer.py`

```python
class AutocodeTrainer:
    def __init__(self, corpus: QCCorpus, embedder: CorpusEmbedder):
        ...

    def train(self, codes=None, coders=None, min_examples=5,
              pattern=None, file_list=None) -> dict:
        """
        For each qualifying code:
          positives = embeddings of lines coded with this code (by specified coders)
          negatives = random sample of 2x positives from all other coded lines
          fit CalibratedClassifierCV(LinearSVC()) to get predict_proba()
        Returns {code_name: fitted_classifier}.
        Skips and warns for codes with < min_examples positives.
        """
        ...

    def describe(self, codes=None, coders=None, min_examples=5,
                 pattern=None, file_list=None) -> dict:
        """
        Returns a dict of training statistics without fitting any classifier:
          {code_name: {"positive_examples": N, "negative_examples": N, "status": "trained"|"skipped"}}
        Used by qc autocode describe.
        """
        ...
```

No `save`/`load` methods: classifiers are never persisted. `CalibratedClassifierCV` wraps `LinearSVC` (which has no native `predict_proba`) using Platt scaling. This is necessary for both confidence thresholding and margin-sampling uncertainty.

### `predictor.py`

```python
class AutocodePredictor:
    def __init__(self, corpus: QCCorpus, embedder: CorpusEmbedder, classifiers: dict):
        ...

    def predict_line(self, embedding: np.ndarray) -> dict[str, float]:
        """Returns {code: confidence} for all trained codes."""
        ...

    def apply_tree_descent(self, raw_predictions: dict[str, float]) -> list[str]:
        """
        Post-processing: walk the code tree top-down.
        At each node: if confidence > autocode_confidence_threshold,
          check children. If no child exceeds autocode_child_threshold,
          predict this node and stop descending.
        Returns list of predicted code names.
        Can be disabled with apply_hierarchy=False.
        """
        ...

    def apply(self, coder, pattern=None, file_list=None,
              codes=None, only_uncoded=True, apply_hierarchy=True):
        """
        For each corpus line (filtered):
          - skip if only_uncoded and line already has a CodedLine from any coder
          - get embedding, predict, apply tree descent, write CodedLines
        Reports counts per code written.
        """
        ...

    def score_all_lines(self, pattern=None, file_list=None) -> list[tuple]:
        """
        Returns [(document_id, line, code, confidence), ...] for all
        trained codes and all lines, without writing to DB.
        Used by UncertaintySampler.
        """
        ...
```

### `active.py`

```python
class UncertaintySampler:
    def __init__(self, corpus: QCCorpus, predictor: AutocodePredictor):
        ...

    def rank_by_margin(self, codes=None, pattern=None, file_list=None,
                       exclude_coded_by=None) -> list[tuple]:
        """
        For each uncoded line, computes per-code margin scores
        (margin = P(top code) - P(second code); lower = more uncertain).
        Aggregates to a line-level uncertainty score (minimum margin across codes).
        Returns [(document_id, line, margin), ...] sorted ascending.
        exclude_coded_by: skip lines already coded by any of these coders.
        """
        ...

    def get_context(self, document_id, line, context_lines=3) -> list[str]:
        """Returns lines surrounding the target line for display."""
        ...
```

---

## New CLI: `qualitative_coding/cli/autocode/`

```
qualitative_coding/cli/autocode/
├── __init__.py     # autocode_group, aliases=['ac']
├── embed.py        # qc autocode embed
├── describe.py     # qc autocode describe
├── outliers.py     # qc autocode outliers
├── density.py      # qc autocode density
├── similar.py      # qc autocode similar
└── interactive.py  # qc autocode CODER (the main active learning command)
```

Register in `qualitative_coding/cli/__init__.py`:
```python
from qualitative_coding.cli.autocode import autocode_group
cli.add_command(autocode_group, aliases=["ac"])
```

### `qc autocode embed`

```
qc autocode embed [--force] [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

Embeds all corpus lines using the configured API. Skips documents whose cache is already valid (unless `--force`). Prints a progress bar over documents. Warns if `embeddings/` is not in `.gitignore`.

### `qc autocode describe`

```
qc autocode describe [CODES]... [-c TRAIN_CODERS]... [-r]
                     [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

Prints a full description of the latent model without fitting it: all hyperparameters from settings, plus per-code training statistics (positive example count, negative example count, trained/skipped status). No classifiers are built; this is purely a read from settings and the database. Output format follows tabulate conventions (`--format`, `--outfile`). This is the canonical way to document the configuration that produced a batch of autocode predictions.

### `qc autocode CODER` (interactive active learning)

```
qc autocode CODER [CODES]... [-c TRAIN_CODERS]... [--retrain]
                  [--context N] [--uncertainty-threshold FLOAT]
                  [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

This is the main command. Its invocation is analogous to `qc code CODER`:

1. Load or retrain classifiers (using `--train-coders`).
2. Score all uncoded lines by margin uncertainty.
3. Display the most uncertain line in context (default ±3 lines, configurable with `--context`).
4. Show ranked candidate codes with confidence scores.
5. Prompt for codes (comma-separated); Enter to skip; `q` to quit.
6. Write coded lines to DB under `CODER`.
7. Retrain classifiers with new data; repeat from step 2.

When `CODES` positional args are given, only codes in that subtree are considered for uncertainty ranking and display. This allows focused sessions on a region of the codebook.

When uncertainty of all remaining lines falls below `--uncertainty-threshold`, the session ends with a summary message ("No more uncertain lines for these codes. Consider running `qc code CODER --auto --no-edit` to write high-confidence predictions.").

The `CODER` argument accepts any coder name — it need not be distinct from training coders. Using the same name as a prior coder integrates new annotations into the training set immediately (online learning). Using a fresh name keeps the round separable and deletable via `qc coders delete`.

### `qc autocode outliers`

```
qc autocode outliers [CODES]... [-c CODERS]... [-r] [-n N]
                     [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

For each code, computes the centroid of its coded lines' embeddings and reports the `N` most distant coded lines — likely miscodes. Displays each outlier line in context, similar to `qc codes find`.

### `qc autocode density`

```
qc autocode density [CODES]... [-c CODERS]... [-r]
                    [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

Reports per-code cohesion as mean pairwise cosine distance among coded lines' embeddings. Low distance = tight, well-defined code. High distance = scattered, potentially over-broad code. Output is a tabulate table: Code, Examples, Mean Distance, Suggestion.

### `qc autocode similar`

```
qc autocode similar [CODES]... [-c CODERS]... [--threshold FLOAT]
                    [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

Computes pairwise cosine similarity between code centroids and reports pairs above `--threshold`. High similarity suggests the codes may be candidates for merging. Output lists code pairs with their similarity score.

---

## New `qc codes` Command: `qc codes agreement`

```
qc codes agreement [CODES]... [-c CODERS]... [--metric METRIC] [--folds N]
                   [-r] [-p PATTERN] [-f FILENAMES] [-s SETTINGS]
```

Alias: `qc codes irr` (for users who search by the older term).

General inter-rater agreement command, living under `qc codes` alongside `stats`, `find`, and `crosstab`. All quality evaluation — human-human, human-autocode, and classifier cross-validation — lives here. Reads `CodedLine` records from the database; the `cv` metric additionally requires embeddings to be generated first.

`--metric` options:

- **`alpha`** (default): Krippendorff's Alpha. Handles multiple coders, missing data, and is the current methodological recommendation for reporting IRR in qualitative research. Appropriate when all coders are on equal footing.
- **`kappa`**: Cohen's Kappa. Pairwise, chance-corrected agreement. Requires exactly two coders. Familiar and widely reported.
- **`f1`**: Precision, Recall, and F1. Appropriate when one coder is treated as authoritative ground truth (e.g., evaluating autocode predictions against a human coder). Requires exactly two coders; the first `-c` coder is treated as ground truth.
- **`cv`**: k-fold cross-validation (default `--folds 5`). Trains a classifier on each fold and reports estimated Precision, Recall, and F1. Requires embeddings. Used to assess classifier quality before writing any predictions. Meaningful with a single coder (self-consistency) or multiple coders pooled.

For each per-code calculation, each corpus line is treated as a binary judgment unit: coded/not-coded with this code for each rater.

Output (example with `--metric alpha`):

```
Code                  Alpha    Coders    Units
------------------  -------  --------  -------
equity                 0.82         2      312
participation          0.71         2      312
identity               0.68         2      312
scratch                0.41         2      312
```

This command handles the full range of IRR use cases: human-human (two researchers coding the same documents), human-autocode (evaluating prediction quality), and cross-round reliability (comparing `human.v1` against `human.v2` on re-coded documents).

Depends on the `krippendorff` package (small, no heavy dependencies) for Alpha. Cohen's Kappa uses `sklearn.metrics.cohen_kappa_score` (already a dependency).

---

## New Command: `qc coders delete`

```
qc coders delete CODER
```

Drops all `CodedLine` records for the given coder and removes the `Coder` record. This is the primary mechanism for reverting autocode predictions. It already has a backend implementation in `QCCorpus.delete_coder` (`corpus.py:325`); it just needs a CLI command.

---

## Extension to `qc code`: `--auto` and `--no-edit` flags

```
qc code CODER --auto [-c TRAIN_CODERS]... [--no-edit] [--threshold FLOAT]
              [--no-hierarchy] [--from-coder AUTOCODE_CODER]
              [-p PATTERN] [-f FILENAMES] [-1] [-r] [-s SETTINGS]
```

`--auto` subsumes the former `qc autocode apply`. The two modes are:

- **With editor** (`--auto` alone): pre-populates `codes.txt` with predictions before opening the editor. The human reviews, corrects, and extends, then saves as usual. Requires a small change to `QCCorpusViewer.open_editor` to accept a `suggest_from` parameter.
- **Without editor** (`--auto --no-edit`): writes predictions directly to the database without opening an editor. Equivalent to the former bulk `apply`. All existing corpus filter flags (`-p`, `-f`, `-1`, `-r`) apply normally.

`-c TRAIN_CODERS` specifies which coders' existing coding to use for training the classifier. `--from-coder` specifies which coder's already-written predictions to pre-populate from (default: `autocode_coder` from settings); only relevant when predictions have been pre-generated rather than computed on the fly.

`--threshold` and `--no-hierarchy` mirror the predictor options. Logs the full describe output to `qc.log` whenever `--no-edit` is used.

---

## Dependencies to Add

- `openai` — for the OpenAI-compatible embedding API client. Lightweight and already widely installed.
- `scikit-learn` — explicit dependency (currently possibly transitive via spacy, but should be declared).
- `krippendorff` — small package for Krippendorff's Alpha. No heavy dependencies.

No new dependency for sentence-transformers (API replaces local model). Spacy remains a dependency for now; optionalization is a separate refactor.

---

## Implementation Order

1. **`qc coders delete` CLI command** — thin wrapper over existing `delete_coder`. Write tests.
2. **`qc codes agreement`** — `alpha`/`kappa`/`f1` metrics are pure database reads (no embeddings); `cv` metric requires embeddings and the trainer. Implement the first three metrics early as a standalone deliverable; add `cv` after the embedder and trainer are built.
3. **`autocode/embedder.py`** — API client, windowed text construction, on-demand cache read/write. Write tests against a mock API.
4. **`cli/autocode/embed.py`** — explicit pre-warming CLI wrapper.
5. **`autocode/trainer.py`** — loads embeddings, fits classifiers, `describe()` method. Write tests with synthetic embeddings.
6. **`cli/autocode/describe.py`** — verifies trainer before writing predictions.
7. **`autocode/predictor.py`** — inference + tree descent. Write tests.
8. **Extend `qc code` with `--auto` and `--no-edit`** — both modes share the predictor; `--no-edit` replaces the former `apply`. Write integration tests for both modes.
9. **`autocode/active.py`** — uncertainty sampling. Write tests.
10. **`cli/autocode/interactive.py`** — the main active learning loop. Most complex CLI component.
11. **`cli/autocode/outliers.py`**, **`density.py`**, **`similar.py`** — embedding analytics.
12. **Update `qc init`** to add `embeddings/` to project `.gitignore`.
13. **Docs**: update `docs/manuscript.rst` with user story, new commands, and settings.

---

## Notes and Risks

- **Cache invalidation on corpus update**: `QCCorpus.update_document` should delete the embeddings cache file for the updated document. Add a `CorpusEmbedder.invalidate(document_id)` call there (but only if the embeddings directory exists — don't error on projects without autocode).
- **Cold start**: before the corpus is embedded, `qc code --auto` and the interactive loop cannot run. Both check for the embeddings cache and print a clear message if absent, directing the user to run `qc autocode embed` first.
- **API rate limits and cost**: the embed command batches requests and shows progress. For large corpora against paid APIs, a dry-run `--count-only` flag is worth adding to report total tokens before committing.
- **Settings changes**: if `autocode_window` or `autocode_api_model` change, the embedding cache becomes stale (sidecar mismatch will catch this). The classifier is always rebuilt fresh, so no separate staleness check is needed for it.
- **Spacy optionalization** (follow-on): make spacy an optional dependency group (`poetry add --optional spacy`; add an `[nlp]` extra), raise a clear `QCError` if `corpus anonymize` is called without it, and add an LLM API-based NER backend as an alternative. This is independent of autocode.
