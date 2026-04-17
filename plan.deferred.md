
# Tasks to complete later

**Q1. Embedding model strategy**

> I want to support users with a range of hardware. For me, the 700gb machine is an external server hosting LMStudio. So an API approach will be best; users can provide API params to a local or remote service. I agree spacy is not the best tool for creating embeddings. Would it be possible to do away with the spacy dependency altogether, and use a LLM API for named entity recognition needed for anonymization?

**Response**: Agreed on API-based embeddings. The embedding backend will use an OpenAI-compatible REST API (`/v1/embeddings`), configured via settings. This works with LMStudio, Ollama, OpenAI, and any compatible host — users just provide `base_url`, `api_key`, and `model`. The `openai` Python package (already widely installed) handles the HTTP.

On removing spacy: spacy is currently a hard dependency, used only by `corpus anonymize`. The docs already describe it as an optional requirement (install a language model separately). The right approach is a two-step refactor: (1) make spacy an optional dependency group in `pyproject.toml`, raising a clear error if it's absent when `corpus anonymize` is called; (2) add an LLM API-based NER backend as an alternative (send document chunks to the API, ask it to identify named entities). This is worth doing but is a separate refactor from autocode. For now: add `openai` as a dependency for autocode; separately plan spacy optionalization.

> OK, I agree. We'll handle this refactor separately later.


# Complex concepts that need to be explained in the docs

**Q4. Classifier scope and hierarchy**

> I'm inclined toward one-vs-rest. But a follow-up question: Is there a classification strategy which recognizes nested relationships — which could penalize misclassifications into sibling codes less heavily, or choose a parent code when uncertainty is too high about the child code?

**Response**: One-vs-rest flat classifiers are the right training strategy (simple, interpretable, no dependency on code tree during training). Hierarchy is respected in a **post-processing tree descent** step:

1. Run all per-code classifiers on a line, producing a `{code: confidence}` dict.
2. Walk the code tree from root to leaves. At each node: if the node's confidence exceeds `autocode_confidence_threshold`, consider its children. If no child exceeds `autocode_child_threshold` (a second, lower threshold for child codes), predict the parent and stop descending.
3. Only write predictions that survive this descent.

This implements "when uncertain about which child, predict the parent instead." In practice this means that early in the project — when child codes have few examples — the system tends to predict at a higher level of abstraction and becomes more specific as training data grows. The two thresholds are configurable:

```yaml
autocode_confidence_threshold: 0.6    # minimum confidence to predict any code
autocode_child_threshold: 0.4         # minimum confidence to prefer child over parent
```

This is a post-processing step in `predictor.py`, not a change to training. It can be disabled with `--no-hierarchy` for users who want flat predictions.
