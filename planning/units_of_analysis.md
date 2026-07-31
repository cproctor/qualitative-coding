# Unit of Analysis Features

July 31, 2026

## Prompt

I want to consider extending (and potentially reframing) units of analysis in `qc`. 
This plan will scope and analyze my proposals: read this prompt, and then write your response in 
the Response section below. We use blockquotes for questions, clarifications, counter-proposals, 
and objections. (I will respond inline with blockquotes as well.)

Currently, qc supports three units of analysis: line, paragraph, and document. These play an essential
role in how we count codes, and in analyses based on counting codes. Let's consider a few extensions. 
For each, consider all of the commands supported by qc, and the consequences of these changes for the UI
(how would the user specify changes, in the settings file and in one-off options to commands), for 
data integrity, for methods and measures (e.g. would Krippendorf's alpha be valid under these units of analysis?), 
and for implementation. 

- Currently paragraphs are delimited by a blank line in markdown. I am concerned that this may not
  be well-defined: does a blank line with invislbe characters also count? Do multiple blank lines 
  produce multiple empty paragraphs? What happens if a document consists of just blank lines? 
  What about when line-break characters are different across systems, or have non-printing characters
  such as those which appear in PDF-extracted text? We should ensure that all of these cases are handled in 
  an unsurprising way, and are documented. This isn't a new feature, it's an enhancement for reliability.
- Consider allowing the settings file to specify a paragraph delimiter. (This would need to be at the 
  granularity of a line; lines always need to be contained within a single paragraph.) The main use
  case for this would probably be when a user wants to chunk a document more coarsely than paragraphs, 
  perhaps in sections or talk turns. How would this work? How would changes to the delimiter be processed?
  Keep in mind, I have implemented a more robust notion of a document index; it would be possible to create a
  new index when a new delimiter is specified, and then toggle between delimiters (and their corresponding indices)
  nondestructively. 
- Would a sliding-window-based unit of analysis even make sense? It's attractive because it eliminates the need
  for arbitrary breaks (e.g. in considering inter-coder agreement it would be helpful to say two coders placed the same
  code close enough in a document), but it might be problematic because lines would belong to multiple units of analysis. 
  Would there be a workable way to do this? Would it be methodoligcally sound?
- I am also interested in implementing timestamp-based units of analysis for documents using timestamped formats (e.g. vtt). 
  The unit could be an interval (1 minute), or it could be talk turns, relying on the transcript's native chunking. 


## Discussion

Before getting to the four proposals, one architectural fact ties them all together and should stay
a hard invariant: **coding always happens at the line level.** A `CodedLine` row always records a
single line, for a single coder, for a single code (`database/models.py:83-94`). "Unit of analysis"
today (`unit: line|paragraph|document` in settings, `-n/--unit` on `codes stats/crosstab/find/agreement`)
only changes how already-line-level codes are *aggregated* for counting and reliability — it never
changes the grain at which a human or an autocoder actually places a code. `docs/background.rst:552-558`
states this as a deliberate contrast with selection-based QDA tools ("the fundamental unit of analysis
in `qc` is the line"). I'd treat every proposal below as an extension to the *aggregation* layer, not
a change to that invariant — it keeps data integrity simple (one canonical numbering, everything else
is a view over it) and keeps existing coded data valid under new units without any recoding.
> Agreed, and well-put. This is an extension of the aggregation layer. However, if a coder wants to think
> in terms of paragraphs while coding and later analyzing, they can ignore the fact that coding is fundamentally
> line-based; they just need to code any line within the paragraph.

> > Right — and that's worth stating explicitly in user-facing docs, not just as an implementation note:
> > "code any line in the unit you're thinking in" is the actual UX story for a coder who wants to work at
> > paragraph or section granularity, and it needs zero new mechanism. I'll fold this into whatever docs
> > come out of proposal 2.

That aggregation layer already has more infrastructure than "line/paragraph/document" suggests. There's
a `DocumentIndex` table — `name` (currently only ever `"paragraphs"`), a `time_series` boolean flag
that exists but is **not read anywhere in the codebase**, and per-document `Location(start_line, end_line)`
rows (`database/models.py:33-69`). This was clearly built to support more than one named index per
document from the start; it's just never been given a second one. That's good news for proposal 2.
> Correct. If you don't think this is a wise architecture, say so. But my thinking was that (for aggregation), 
> we might want to distinguish the nature of the index itself (how we measure distance within a document, 
> always at or above the graunuarity of the line) from how we aggregate. 

> > I do think it's wise, and I think the distinction you're drawing is already latent in the code, just
> > not named anywhere. Concretely: **index** = a fixed partition of a document's lines into disjoint
> > ranges (`DocumentIndex`/`Location` — "how distance is measured," as you put it: two lines are "close"
> > if they share a `Location`). **Aggregation** = the rule for folding the line-level codes inside one
> > partition cell into a single per-unit judgment for a given command. Today there's exactly one
> > aggregation rule, implicit and unnamed: "present if any line in the unit is coded" (that's what
> > `get_column_to_count`'s `COUNT(DISTINCT ...)` and the reliability matrix's binary presence check both
> > compute). That rule is a property of the *query* (stats/crosstab/agreement), not of the index — the
> > same `"paragraphs"` index already gets aggregated this identical way regardless of which command asks.
> > So I'd say the architecture already keeps these separate, it's just never been written down as a
> > concept with a name. Two things I'd do about that: (1) document it explicitly (a "Concepts" section:
> > indices partition, aggregation folds), so proposal 2's `delimiters` setting is clearly understood as
> > adding *indices*, not aggregation rules; (2) keep "any line coded ⇒ unit coded" as the only aggregation
> > rule for now rather than making it configurable — I can imagine wanting e.g. "majority of lines" for
> > some future analysis, but that's a hypothetical need, not one either of us has hit yet, and it multiplies
> > the design space (does majority-vote apply to alpha too? to counts?) for no concrete payoff right now.

> One note while developing the concepts: most qualitative researchers will think about unit-of-analysis
> as fundamental to coding, an immutable choice to be made before starting. Modularizing that choice and 
> scoping it to queries (via aggregation) is an innovation in qc, but it's one that is a superset of existing
> practice: you don't have to think about this if you don't want to. 

> > That's the framing I'd lead with in docs, actually — not "qc redefines unit of analysis" but "qc
> > defers the unit-of-analysis choice from coding time to query time, so the traditional workflow (pick
> > one unit, code and analyze at that granularity throughout) is just the special case where every query
> > uses the same `--unit`." Worth a sentence in `docs/background.rst` alongside the existing "coding is
> > fundamentally line-based" framing, since it's the same kind of methodological claim that document
> > already makes about `qc`'s design.

### 1. Paragraph delimiter reliability

I traced `iter_paragraph_lines` (`helpers.py:26-36`), the function that actually walks a document and
decides where paragraphs start/end, and I think your instinct that this is under-specified is correct
— I found four concrete problems, not just hypothetical ones:

- **Empty document is a crash, not an edge case.** The function does `for i, line in enumerate(fh): ...`
  then unconditionally `yield p_start, i + 1` after the loop. If the file has zero lines, `i` is never
  bound and this raises `NameError`. `register_document` (`corpus.py:475-500`) calls this at import
  time with no guard, so importing a genuinely empty file currently crashes `qc corpus import`.
  > I think we should support empty documents (as long as this does not create conflict with the REFI-QDA standard). 
  > The main use case I can think of is a document that's not actually empty but just contains blank lines--
  > if you want to share or publish your codes but cannot release the documents yourself. It might be sensible to 
  > replace the docuemnt with the same number of blank lines (so as not to invalidate the codes)--although that's
  > not a good strategy, because you would lose the paragraph structure. Probably then better to replace the document 
  > with something like X for a line of text and a blank line for paragraph delimiters...After all that, should we 
  > support empty documents? This would also potentially create problems for git--can you save an empty file in git?

  > > Git itself isn't the blocker — a zero-byte file commits and diffs fine, so that concern doesn't rule
  > > anything out. But I'd separate "should `qc` crash on a 0-line file" from "should `qc` support a
  > > workflow built around empty documents," and answer those differently. The crash should just be
  > > fixed regardless (a defensive fix — 0 lines should yield 0 paragraphs, not raise `NameError`; a
  > > document could legitimately end up empty for boring reasons, like an upstream conversion tool
  > > producing an empty file, and `qc corpus import` shouldn't hard-crash on it).
  > >
  > > For the actual use case — sharing codes without the underlying text — I'd steer away from building
  > > "empty document" as a first-class thing, because you already have the right tool for exactly the
  > > transformation you described (replace every line with a placeholder, preserve blank lines so
  > > paragraph structure survives): `corpus anonymize` already does line-preserving text substitution
  > > and routes through `update_document`'s diff-based reindexing (`anonymize.py:53-55`,
  > > `corpus.update_document`), which is precisely the machinery needed to guarantee codes stay valid
  > > across a full-text rewrite. It just doesn't go far enough today — it only swaps out spaCy-detected
  > > named entities, not arbitrary content. A `--redact-all` mode (replace every non-blank line with a
  > > fixed placeholder token, keep blank lines as-is) would give you a shareable, structure-preserving,
  > > fully de-identified corpus using infrastructure that already exists and is already tested, rather
  > > than teaching every code path (import, paragraph indexing, REFI-QDA export, `codes find`) to handle
  > > the zero-content case gracefully. Want me to scope that as a small addition to `corpus anonymize`
  > > separately from this document? On the REFI-QDA question — I haven't checked whether the schema
  > > requires non-empty `PlainTextSource` content, but it's moot if we go the placeholder route instead
  > > of true emptiness.

  > > > Agreed. Won't be building out new features around this right now though.

- **A document of only blank lines yields one phantom paragraph.** Same unconditional trailing `yield`:
  if every line is blank, `in_whitespace` is `True` the whole time and no paragraph boundary is ever
  emitted mid-loop, but the final `yield p_start, i + 1` still fires, producing a single `Location`
  spanning the entire (all-blank) document. That's a paragraph with no content — a unit that can never
  legitimately hold a code but will still show up in the "all units" denominator for Krippendorff's
  alpha (`get_all_paragraphs`, `corpus.py:733-746`), silently deflating alpha for every code.
  > I believe that the blank-line demiting a paragraph is included in either the preceding or the following 
  > paragraph's lines, so that paragraphs fully-cover the docuemnt and no codes are lost. Keeping that consistent, 
  > wouldn't it make sense to have a document full of blank lines constitute a single legitimate paragraph?

  > > You're right, and I should retract calling this a bug. I traced it again: for `"foo\n\nbar"`,
  > > paragraph one is lines `[0, 2)` — "foo" *and* the blank line — then paragraph two starts at line 2
  > > ("bar"). So the blank line is already folded into the *preceding* paragraph, exactly the full-coverage
  > > rule you describe, and it's already true today for any interior blank line, not just a proposed
  > > change. Given that rule, a document of only blank lines has no preceding paragraph to absorb into,
  > > so it's consistent (not a special case) for it to become one paragraph of its own — I agree, that's
  > > the right behavior, not a bug to fix. It's also not even a new situation: a document that merely
  > > *starts* with a blank line already gets an empty leading paragraph today (nothing precedes it either),
  > > so an all-blank document is just the limiting case of something the current rule already produces.
  > > I also overstated the Krippendorff's alpha concern — a unit where every coder shows absence isn't
  > > "silently deflating" alpha, it's a legitimate true-negative agreement data point, which is exactly
  > > what the statistic is supposed to credit. I'll drop both claims; the empty-file `NameError` is the
  > > only genuine bug left in this list.

- **Multiple blank lines correctly collapse to one boundary** — this one you were worried about but
  it's actually fine: `in_whitespace` is a boolean flag, not a counter, so N consecutive blank lines
  only ever produce one paragraph break. No fix needed here.
- **Blank-line detection is `line.strip() == ""`**, i.e. Python's whitespace definition. This
  correctly treats `\xa0` (non-breaking space) and `\x0c` (form feed) as blank, since both satisfy
  `str.isspace()` — but it will *not* treat a zero-width space (`​`) or other invisible-but-non-whitespace
  Unicode as blank, so a "blank" line containing only `​` silently fails to break a paragraph. This
  matches your concern; whether it's worth handling depends on how often that shows up in your real
  PDF-extracted corpora.
  > I think we should stick with Python's definition of whitespace for the default line delimiter. It's not 
  > QC's job to clean up files.

  > > Agreed — noted as a closed question, no change needed.

There's a fifth problem I didn't expect to find, and it's more serious than the four above because
it's a *silent numbering desync*, the same class of bug just fixed in `5be24bb` — just not yet fixed
in this particular path. That commit made `codes find`'s display and `open_editor`'s line-count
validation agree on treating `\x0c` and other splitlines()-only breaks as line boundaries, by
switching both to `text.splitlines(keepends=True)`. But `iter_paragraph_lines` is still called on a
raw file handle (`corpus.py:493-494`, `embedder.py:128-129`), iterated with plain `for i, line in
enumerate(fh)` — Python's universal-newlines mode, which does **not** split on `\x0c` (or `\x0b`,
`\x1c`–`\x1e`, ` `, ` `). So on any corpus document containing a form feed, the paragraph
index's `start_line`/`end_line` will disagree with the canonical line numbers used everywhere else
(the same kind of PDF-extraction artifact the commit's own description says hit 114/115 documents in
a real corpus). This means paragraph-level counts, `codes find` in paragraph mode, and paragraph-unit
agreement can currently be silently wrong on the same class of documents that motivated the last fix.
I'd fix this regardless of whatever else comes out of this discussion — it's a pre-existing bug, not
a consequence of new features. It's also not confined to import-time indexing: `show_agreement`'s
line-unit domain construction (`viewer.py:877`, `sum(1 for _ in open(...))`) and the REFI-QDA exporter's
`line_positions` (`refi_qda/writer.py:161-166`) both still count lines by plain file iteration too —
so a form-feed document can currently desync line-unit Krippendorff's alpha's denominator *and*
REFI-QDA export offsets, not just paragraph boundaries. All of these should move to the same
`splitlines()`-based counting `5be24bb` already established as canonical, ideally through one shared
helper instead of the current pattern of each call site reimplementing "how many lines in this file."
> We should absolutely fix this, and should probably have the line-feeding logic written in one place 
> to avoid inconsistent handling in teh future--as you suggest.

One more landmine, separate from the four bugs above: there's a second, dead paragraph-splitting
function, `prepare_corpus_text` (`helpers.py:57-71`), which splits on a stricter `text.split("\n\n")`
rather than `iter_paragraph_lines`'s "any whitespace-only line." It's unused anywhere else in the
codebase today, but it disagrees with the real paragraph logic, so it's worth deleting (or documenting
clearly as not-the-real-rule) rather than leaving it to be found and assumed authoritative later.
> That should go away.

There's a sixth thing worth flagging even though it's not a "delimiter" question: `update_document`
(`corpus.py:910-946`) reindexes `CodedLine.line` numbers via `reindex_coded_lines` but never rebuilds
the `DocumentIndex`/`Location` rows for the `"paragraphs"` index. So today, editing a corpus document
through `qc corpus update` leaves paragraph boundaries stale relative to the new text. This matters a
lot for proposal 2 below, since a design that adds more named indices needs an answer for "what
reindexes them, and when" — right now the answer for the one index that exists is "nothing does."
> This is a bug and should be fixed. Currently, a user will have a surprising and negative experience 
> when their paragraph-based analysis becomes stale after updating a document. This would raise issues
> when trying to revert an `update corpus`, but we don't support that, correct? The only way would be to 
> revert to a previous commit in version control.

> > Confirmed — I checked `cli/corpus/update.py`; the only option besides `file_path`/`settings`/`new` is
> > `--dryrun` (preview the diff without applying it). There's no undo/rollback command once an update has
> > actually run. So yes, today the only recovery path is external version control — `qc corpus update` is
> > one-directional, and `--dryrun` is the sole safety net before committing to it.

### 2. User-specified delimiters, stored as named indices

This maps cleanly onto the existing `DocumentIndex` model — I don't think it needs new schema, just
code that was never written to use the schema that's already there. Sketch:

```yaml
# settings.yaml
unit: line   # or 'paragraph', 'section', or any name defined below
delimiters:
  paragraph: blank_line     # built-in, current behavior — kept as the default index
  section: "^## "           # a line-anchored regex; matching lines start a new unit
                             # and are themselves included in it (like a section heading)
```
> In this example, would "section" then become a valid unit of analysis when passed to commands? That
> is attractive, because it would allow users to customize the UI's semantics, potentially important when 
> doing interpretive coding. 

> > Yes, exactly — any name under `delimiters:` becomes a legal value for `unit` in settings and for
> > `-n/--unit` on every command that takes it, on equal footing with `line`/`paragraph`/`document`. That's
> > the whole point of routing this through `DocumentIndex.name` rather than a fixed enum: the vocabulary a
> > user codes and queries in becomes theirs to define, which does matter for interpretive coding where
> > "section" or "turn" may be the analytically meaningful unit, not an implementation detail.

> We need to ensure uniqueness of unit labels (e.g. you can't redefine "paragraph") 

> > Agreed — two separate checks, both at settings-load time (fail fast with a clear message, rather
> > than surfacing a `UniqueConstraint` violation from the DB later). First, `line` and `document` are
> > reserved: they're derived directly (`CodedLine.id`, `Document.file_path`), never backed by a
> > `DocumentIndex`, so a `delimiters` entry named `line` or `document` should be a settings-validation
> > error. Second, `delimiters` keys must be unique among themselves (YAML already guarantees this — a
> > duplicate key in the same mapping just silently overwrites in the parser, so nothing extra needed
> > there) and unique against the reserved names. `"paragraph"` itself isn't special beyond being the
> > default entry in the sketch above — it's just a `delimiters` key like any other, so redefining what
> > `paragraph:` points to (e.g. changing it from `blank_line` to something else) is allowed and is
> > exactly how a user would customize the built-in default; what's disallowed is a *second* mapping
> > entry also named `paragraph`, which YAML's own parsing already rules out.

- **Granularity constraint**: you noted a delimiter has to operate "at the granularity of a line" —
  that's already true of `Location(start_line, end_line)`, so any delimiter function's contract is
  just "given lines, yield `(start, end)` ranges," exactly `iter_paragraph_lines`'s existing shape.
  A regex-per-line delimiter is one implementation of that contract; nothing stops adding others later
  (e.g. a fixed line count) behind the same interface.
- **Indices are additive, not a replacement.** On import (and on `qc corpus update`, once that's
  fixed to reindex at all), build a `DocumentIndex` for every delimiter named in settings — `paragraph`
  stays how it is today, plus one more for `section`. Nothing about existing paragraph-unit data
  changes when you add a `section` delimiter; you get a new column of `Location` rows alongside it.
  Removing a named delimiter from settings should probably not delete its `DocumentIndex` rows
  automatically (a coder-safety default: don't destroy indexing data unprompted) — reindex on demand,
  or deliberately with a `qc corpus reindex` command, and require confirmation to actually drop one.
  > I think it's probably better to just reindex on `qc corpus update`, so that users don't need to keep 
  > the ontology of indices in their minds. 
  > Also, is there any way for indices to survive exporting to REFI-QDA and then re-importing? I think this
  > is an important property of consistency; we encourage users to use this as a format for packaging their
  > projects.

  > > Agreed on always reindexing at update time rather than on-demand — it's not expensive (rebuilding
  > > every declared index is just re-running some line-partitioning functions over the new text, all
  > > in-process, no I/O beyond the file already being read) and it removes an entire category of "did I
  > > remember to reindex" user error. That also folds in as the fix for the sixth bug above — `qc corpus
  > > update` should rebuild every `DocumentIndex` a project declares, not just leave `"paragraphs"` stale.
  > >
  > > On REFI-QDA round-tripping: I checked both `refi_qda/writer.py` and `refi_qda/reader.py`, and the
  > > honest answer is **no, not currently — and not even for the one index that already exists.**
  > > `sources_to_xml` (`writer.py:120-151`) only ever emits `PlainTextSelection` elements at `line:N`
  > > granularity, one per coded line; there is nothing in REFI-QDA's data model (I checked `schema.xsd`)
  > > corresponding to `qc`'s `DocumentIndex`/`Location` concept at all — REFI-QDA doesn't have a notion of
  > > a named line-partition, only character-offset selections. On reimport, `unpack_sources`
  > > (`reader.py:106-125`) calls `self.corpus.import_media(importable_path, importer="verbatim")`, which
  > > is the same `register_document` path as any fresh import — it rebuilds a brand-new `"paragraphs"`
  > > index from scratch via the standard blank-line rule. So today, exporting and reimporting already
  > > silently drops paragraph structure as *qc-specific* metadata (it happens to often come back looking
  > > right only because blank-line paragraphing is deterministic and the underlying text is unchanged);
  > > it would *not* come back right for a custom `section` or timestamp index, since nothing about those
  > > is derivable from the plain text alone. `qc`'s own `settings.yaml` also isn't packaged into the
  > > `.qdpx` at all — the writer never touches `Description`, and the reader's `unpack_unsupported(root,
  > > "Description")` (`reader.py:63`) explicitly discards whatever's there rather than reading it back.
  > >
  > > If exact round-tripping matters for the "package projects as `.qdpx`" story, I see two options, and
  > > I'd like your read on which fidelity you actually want: (a) accept that REFI-QDA export is
  > > necessarily lossy for anything beyond line-level codes — document that plainly, since `qc` supports
  > > richer structure than the REFI-QDA standard has a place for — or (b) treat `.qdpx` as a `qc`-specific
  > > packaging format in practice, and stash `qc`'s `settings.yaml` (delimiters, unit, etc.) verbatim in
  > > the top-level `Description` field (or a `Notes` entry) on export, and have the reader restore it and
  > > re-run indexing from it rather than discarding it. (b) is a real, if fairly small, feature — do you
  > > want it in scope here, or is "REFI-QDA round-trip is lossy beyond line-level codes" an acceptable,
  > > documented limitation for now?

  > Yes, I do want this feature. REFI-QDA does not specify feature-completeness, so its contract is 
  > inherently potentially-lossy. But we can do better for the specific use case of qc-roundtripping, 
  > and it's worth doing because (especially with the AI features) I am moving toward specifying hyperparameters
  > like unit-of-analysis and embedding lines-before and lines-after so that analyses can be reproduced. 
  > If we have a way of encoding settings, we don't need to do anything else to precisely recreate the document
  > indices, though: they are fully-declarative. We should specify another invariant: indices are generated only from a 
  > document's text. A VTT importer which generates the index from timestamps which are then discarded is invalid; 
  > you can't recreate the index (either on `qc corpus update` or on a roundtrip to qpdx). 
  >
  > This raises a question which is slightly out-of-scope, but which I would also like to treat since 
  > we are adding a commitment to qpdx round-trip support: what to do about embeddings? Is there a way 
  > to package them with qpdx (qc export --with-embeddings), or would it be better to package them in some
  > kind of auxiliary file which we can read on import, or should we just fully-specify the model params
  > to generate the embeddings (e.g. model name, temperature, seed, other params, etc. -- maybe this is unreliable, 
  > since embeddings could be generated from cloud models which are inherently stochastic, or users might not have
  > the technical expertise to fully-specify. I think it is probably desirable to support a packaging where
  > you know the analysis will work for the end user.

  > > Option (b) it is — noted for the plan. And I'll adopt "indices are generated only from a document's
  > > text" as a hard invariant alongside the other two; it's the right call, and it's a stronger, cleaner
  > > requirement than what I'd proposed. It directly invalidates my `vtt` design above, which put
  > > timestamps only in the DB and stripped them from the visible text — that design fails exactly the
  > > test you're describing, since `qc corpus update` or a `.qdpx` reimport would have no way to
  > > regenerate the `"turns"` index from the text alone. I'll revise that below in proposal 4 rather than
  > > here, since it's specifically a proposal-4 design, but the invariant itself belongs at the top of
  > > this document with the other two.
  > >
  > > On embeddings packaging: I'd rule out "fully-specify the model params and regenerate" as the
  > > primary mechanism, for exactly the reason you flagged — a hosted/cloud model isn't guaranteed
  > > deterministic even with the same params (and some providers don't expose a seed at all), so
  > > "recreate on demand" can silently produce different vectors than the ones an analysis was actually
  > > run against. That's disqualifying for a packaging format whose whole point is "the analysis will
  > > work for the end user" — recorded params should be *metadata for provenance/debugging*, not the
  > > mechanism of reproduction. Between packaging embeddings inside the `.qdpx` versus a separate
  > > auxiliary file: I'd package them inside the `.qdpx`, as an `internal://` asset alongside
  > > `sources/`, the same pattern the format already uses for source text — a `.qdpx` that "just works"
  > > for the recipient shouldn't require a second file to travel alongside it. Embeddings are cached as
  > > `.npy` files today (`embedder.py`'s `cache_path`); those plus their sidecar JSON (model, unit,
  > > window, hash — `embedder.py:100-106`) could be zipped in directly, keyed by document hash so a
  > > reimporter can detect staleness the same way the existing cache does. Downside worth naming: this
  > > can make `.qdpx` files large for big corpora (embeddings scale with corpus size, unlike text), so
  > > I'd make it opt-in (`qc export --with-embeddings`, as you suggested) rather than default.

- **CLI surface**: `-n/--unit` is currently `click.Choice(['line', 'paragraph', 'document'])`
  (`cli/codes/stats.py:24-25`, and identically in `crosstab.py`/`find.py`/`agreement.py`) — hardcoded,
  so it can't accept a user-defined name today. That Choice constraint would need to become dynamic
  (built from `settings['delimiters'].keys() | {'line', 'document'}` at CLI-construction time) or
  loosened to a plain string validated against settings inside the command. I'd lean toward the
  latter — Click choices built from a settings file read at decorator-evaluation time is awkward
  because Click decorators run at import time, before a settings path is known.
- **Krippendorff's Alpha stays valid** under a named-delimiter unit for the same reason it's valid
  for paragraphs today: each unit is still a disjoint, well-defined bucket, and the reliability matrix
  (`viewer.py:929-943`) only needs "is this code present in this unit, for this coder" as a binary
  judgment per (coder, unit) cell. Nothing in that computation assumes paragraphs specifically; it
  assumes *non-overlapping* units, which any line-partitioning delimiter still gives you. That
  assumption is exactly what breaks in proposal 3.

### 3. Sliding-window units of analysis

I'd separate two things you're bundling together, because the codebase already draws this line for a
different reason: a *window used for embedding context* already exists (`embedder.py`'s
`window_before`/`window_after` in `_chunks_line`, `corpus.py:112-122`) — but that window only enriches
what text gets embedded for a line; the unit being predicted and stored is still that one line. Nobody
double-counts a line because its neighbors were included in its embedding context. A sliding-window
*unit of analysis* is a different proposal: making the countable/comparable unit itself a window, so
"line 40" and "line 42" partially overlap as units.
> I was also thinking about the relationship between the sliding window proposal and the embedding window. 
> This raises an interesting question: embeddings are unit-of-analysis based, so we should be able to support
> arbitrary units (e.g. sections, from above). Can you please confirm that the lines-before and lines-after settings for embeddings
> will be compatible with these new units?

> > I can't confirm compatibility as-is, because `window_before`/`window_after` today isn't really a
> > "unit-of-analysis" setting — it's specific to the `line` case. Looking at all three `_chunks_*`
> > methods (`embedder.py:112-141`): `_chunks_line` is the only one that adds surrounding context; a line
> > by itself is usually too little text to embed meaningfully, so the window pads it out. `_chunks_paragraph`
> > and `_chunks_document` just embed the unit's own full text, no padding — because a paragraph or a whole
> > document is already enough context on its own. A new named unit (`section`) would naturally fall into
> > that second bucket by default: embed the section's own text, no added window, since `window_before`/
> > `window_after` is defined in *lines*, and there's no existing notion of "one section of padding" for it
> > to mean.

> OK, so we specify that for embeddings the window_{before|after} only applies when the unit of analysis is 
> the line.

> > > Settled — noted for the plan.

That said, I think there's a real, generalizable version of what you're after: redefine the window in
terms of *neighboring units of whatever index is active*, not raw line counts — e.g. `window: [1, 1]`
would mean "include the previous and next paragraph" when `unit: paragraph`, or "the previous and next
section" when `unit: section`, falling back to today's exact line-count behavior when `unit: line`
(since a line's "neighboring unit" *is* the line before/after it). That's a small, clean generalization
of the existing mechanism, not something that already works today. Want me to scope that alongside
proposal 2, or keep windowing as a line-only feature for now and treat this as deferred?
> No, this will be more likely to confuse users. As you note, the non-line units of analysis can be 
> presumed to have enough context on their own to produce meaningful embeddings.

> > Agreed, dropped — `window` stays a line-only setting, no generalization.

That second thing runs into a real problem, not just an implementation headache: every current
agreement metric (`viewer.py:920-976`) treats units as **independent, disjoint Bernoulli trials** —
that's what Krippendorff's Alpha, Cohen's Kappa, and F1 all assume as their basic input shape (one
judgment per unit per rater, units don't share information). Overlapping windows violate independence
directly: a single code placed once by both coders at line 41 would register as agreement on the
windows centered at 39, 40, 41, 42, and 43 (or however wide the window is) — one true instance of
agreement gets counted five times, mechanically inflating alpha/kappa without any real change in
reliability. This isn't a data-integrity problem you can paper over with better bookkeeping; it's the
statistic itself losing its meaning. So I'd say: sliding windows are not sound as a drop-in unit for
`alpha`/`kappa`/`f1` as currently computed.
> I am persuaded. Just as "coding always happens at the line level" is a hard invariant, we will also 
> say that "units are disjoint subsets which competely cover a document."

What you're actually after — "these two coders placed the same code close enough together" — is a
real and useful question, but I think it wants a different measure, not a redefinition of "unit":
something like a **tolerance-window match** for proximity-based agreement (a location-based, not
category-based, agreement metric — closer to how NER span-matching or diarization scoring handles
"close enough" alignment: match each coder-A instance to the nearest coder-B instance of the same code
within N lines, greedily or via optimal bipartite matching, then report matched/unmatched counts as
precision/recall rather than alpha). That's a legitimately new metric (`--metric proximity`?, taking a
`--window N` line-count parameter) rather than a new `--unit`, and it sidesteps the independence
problem because it's not built on a reliability-data matrix at all — it's a matching/counting exercise
per code, closer methodologically to how `f1` already treats one coder as reference. I'd want to
name it something that doesn't say "Krippendorff" or "Cohen" anywhere in its output, precisely so it
doesn't get quoted as if it were a validated chance-corrected agreement coefficient — it isn't one.
> I like this framing. Not going to pursue that feature right now though.

### 4. Timestamp-based units for transcripts (VTT etc.)

This is the one proposal that can't be built as a pure aggregation layer over today's data, because
today's data throws the information away before it ever reaches the database. I read `VTTImporter`
(`media_importers/vtt.py`) closely: it parses `webvtt`, merges consecutive same-speaker captions into
talk turns, and writes out plain text with **the timestamps discarded entirely** — `caption.text` is
kept, `caption.start`/`caption.end` are not. By the time `register_document` sees the file, it's
indistinguishable from any other `.txt` corpus document; there is no timing information left anywhere
to index against. Two consequences:
> This analysis makes me think the VTT importer is unsound. It's destructive and idiosyncratic--it met
> my needs for a project, but it's not the main way we should be handling VTT, especially once we have
> a logical representation of time-series index. As part of adding a time-series index, let's redefine 
> VTT importer to preserve file content, and create both a time-series and a paragraph-based index. 
> We could preserve the current functionality in a new importer, perhaps vtt-to-text, for when you 
> want to discard time information to make a transcript more readable. 

> > Agreed, and splitting the importer in two is the right call — keep `vtt` as the name for the sound
> > version, add `vtt-to-text` (or similar) as an explicit opt-in for today's lossy, readability-first
> > behavior, rather than quietly changing what the default `vtt` importer does out from under existing
> > users. Concretely, I'd design the new `vtt` importer as: parse every caption's `(speaker, text, start,
> > end)` — same as today — but instead of discarding timing, build *two* `DocumentIndex` rows per
> > document from that same parse: a `"turns"` index (one `Location` per caption/turn, `time_series=True`,
> > carrying its start/end timestamp) and a `"paragraphs"` index built by the ordinary blank-line rule over
> > the same written text (so paragraph-unit behavior is unaffected, and — per your point below about not
> > leaking timestamps into the visible document — the written `.txt` still looks exactly like today's
> > `"Speaker: text"`-per-turn output, no raw VTT timing cruft inline). The `"turns"` index is the
> > *native*, finest-grained time-series data; coarser buckets (1-minute, 5-minute) would then be **derived
> > groupings of `"turns"` locations by timestamp**, computed once at import time (or lazily), never by
> > re-parsing the source `.vtt` again. That also directly answers your later question about not
> > re-consuming timestamps to build the index while stripping them from the document: the document body
> > stays clean prose; the timing lives only in `Location.start_time`/`end_time` on the time-series
> > indices, never inline in the text.

> No, I think we need to keep the timestamps in the text--see my comment above about the declarative nature
> of indices and the need for them to be reproducible from the document's text. The vtt-to-text importer
> will produce a document stripped of timestamps and without a time series index.

> > > Right, that follows directly from the invariant you set above, and it's a real correction to what
> > > I sketched — my design put timing only in the DB precisely to keep it out of the visible text, which
> > > is exactly the thing that breaks reproducibility. Revised design: the `vtt` importer writes each
> > > turn with its timestamp inline, e.g.
> > >
> > > ```
> > > [00:00:01.200 --> 00:00:04.500] Alice: Hello there.
> > >
> > > [00:00:04.600 --> 00:00:09.000] Bob: Hi Alice.
> > > ```
> > >
> > > and the `"turns"` time-series index is then built by a delimiter that both splits *and* extracts a
> > > timestamp from a line matching `^\[(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\]`, populating
> > > `Location.start_time`/`end_time` from the match. That makes a time-series index just another
> > > `delimiters` entry (proposal 2's mechanism, generalized to optionally capture a timestamp instead
> > > of only marking a boundary), not a separate import-time-only mechanism — and it satisfies the
> > > invariant exactly: re-running the same regex over the same text on `qc corpus update` or a `.qdpx`
> > > reimport reconstructs the identical index, no out-of-band caption data required. `"paragraphs"`
> > > would then need its default blank-line rule to treat these timestamp-bracket lines as content
> > > (not blank), which it already does — they're non-blank text — so turns still group into paragraphs
> > > exactly as today. `vtt-to-text` becomes the one place that actually discards the brackets, producing
> > > today's clean, timestamp-free reading copy with no time-series index at all, as you said.

- **Talk-turn units** (your second option) are actually already half-built: a talk turn *is* what
  `VTTImporter` currently collapses into one paragraph (blank-line-separated). If proposal 2 ships,
  "talk turn as unit of analysis" falls out for free for VTT-imported documents — it's just the
  `paragraph` (or a renamed `turn`) index, no new mechanism needed. That's a very small feature once
  named delimiters exist.
  > Agreed. 
- **Interval-based units** (1-minute buckets) are not free — they need actual clock time attached to
  lines, which means changing the importer to *keep* timestamps rather than discard them, and
  changing the schema to store them. That `time_series: Mapped[bool]` flag already sitting unused on
  `DocumentIndex` (`database/models.py:43`) strongly suggests you'd already sketched this: a
  `DocumentIndex(name="1min", time_series=True)` whose `Location` rows carry start/end *timestamps*
  instead of (or alongside) line numbers. The cleanest version I can see: extend `Location` with
  nullable `start_time`/`end_time` columns, populated only for time-series indices; line-based indices
  leave them null. The VTT importer would need to preserve per-caption `(start_line, end_line,
  start_time, end_time)` alongside the text it writes, then `register_document` builds the time-series
  index from that instead of from a delimiter function.
  > This works. As noted above, we will preserve the data in VTT files. I don't think it's a good idea
  > to consume time data in a doc to make its index, but strip its visibility from the document itself. 
  > Since we will need to understand the file format anyway, we might choose to present content 
  > (e.g. in `qc codes find`) with the time data stripped, and present the index in a cleaner format. 
  > We will need to consider how we expose these new indices for downstream consumtion in CSV files.

  > > For CSV exposure: right now `codes find --json` (`get_coded_text_json`) is the one place that already
  > > reports unit boundaries at all — for `unit: paragraph` it includes the paragraph's line range
  > > alongside the text; the tabular commands (`stats`/`crosstab`/`agreement`) only ever report *counts*
  > > per unit, never the units' own boundaries, so there's no existing precedent there to disturb. The
  > > natural extension: when the active unit is time-series, `codes find`'s JSON/CSV output gains
  > > `start_time`/`end_time` fields (formatted `HH:MM:SS.mmm`) alongside whatever `start_line`/`end_line`
  > > it already reports, rather than replacing them — a researcher exporting for further analysis likely
  > > wants both the timestamp (for aligning against audio/video) and the line numbers (for referencing
  > > back into the `qc` corpus text). I'd leave `stats`/`crosstab`/`agreement`'s CSV shape untouched
  > > otherwise, since they don't expose per-unit boundaries for line/paragraph/document today either.

  > So we make the CSV export commitment a bit more abstract: the goal is still to pass the fundamental
  > information to the downstream consumer, but now we say we'll pass the bounding index values; 
  > those could be line numbers, time stamps, or something more exotic in the future (e.g. run sentiment
  > analysis on a document, annotate with sentiment tags, create a SentimentIndex, and the bounds reported
  > would include the qualitative annotation of how the sentiment is shifting at the boundaries).

  > > > Agreed — that's the better commitment to make, and it generalizes the "index" concept itself, not
  > > > just its CSV rendering: an index's `Location` can carry whatever boundary-describing payload is
  > > > meaningful for how it was built (line range always; a time range for time-series indices; your
  > > > sentiment example would presumably attach a value or tag pair at each boundary). I'd implement this
  > > > as each index type owning its own boundary-serialization, rather than a fixed CSV schema — `codes
  > > > find` asks the active `DocumentIndex` "describe this `Location`" and gets back whatever fields are
  > > > meaningful for that index type, with `start_line`/`end_line` as the one field every index always has
  > > > (since every index is still a line partition underneath, per the invariant above) and everything
  > > > else additive. That keeps line/paragraph/document CSV output exactly as it is today.

- This is a bigger lift than it looks, though, for a reason unrelated to timestamps specifically:
  `qc`'s existing migration system (`migrations/migration_1_4_1.py` etc.) only ever rewrites
  `settings.yaml`. The sqlite schema itself is created exactly once, via `Base.metadata.create_all()`
  at `qc init` (`corpus.py:124-125`), and nothing currently alters an *existing* project's tables —
  there is no schema-migration mechanism in `qc` at all yet, for anything. Adding `start_time`/`end_time`
  columns to `Location` means building that mechanism for the first time (even a minimal hand-rolled
  `ALTER TABLE ... ADD COLUMN` runner keyed off `qc_version`, the same version already used to gate
  settings migrations), not just adding two columns to `models.py` and calling it done — existing
  users' project databases won't pick up new columns on their own. Worth sizing proposal 2 (no new
  columns needed, `DocumentIndex.name` already free-text) as the smaller, schema-migration-free step,
  and treating "qc's first real DB schema migration" as its own piece of infrastructure work that
  interval-based timestamp units happen to be the first feature to need.
  > Agreed. That said, we have not yet published major-version 2, so this migration could come with v2.

  > > Good news then, but one wrinkle: `migration_2_0_0.py` already exists and is already spoken for — it
  > > nests the flat `autocode_*` settings keys into an `autocode` table, unrelated to any of this. So
  > > `2.0.0` itself isn't a free slot; this would need its own version after it (`2.1.0`, say), still
  > > pre-1.0-adjacent enough that "no real installed base to worry about yet" mostly holds, but not quite
  > > "bundle it into the v2 cutover" — it'd be the *next* migration after v2 ships. Either way, I'd use
  > > this as the occasion to add "a migration can also touch the DB schema" as a generalized capability of
  > > `QCMigration` (right now `apply`/`revert` only ever call `set_setting`/`delete_setting`), rather than
  > > a one-off special case just for this column — the next schema need (and there will be one) shouldn't
  > > require re-deriving this from scratch.

  > That's fine--the public release can jump right to 2.1.0, with separate migrations for the convenience
  > of internal developers and testers.

  > > > Noted for the plan: ship `2.0.0` (autocode settings nesting) and `2.1.0` (DB schema migration
  > > > mechanism + `Location.start_time`/`end_time`) as sequential internal migrations; the public release
  > > > can jump straight to `2.1.0` without anyone seeing `2.0.0` as an intermediate state.

- One real design question this raises: what does "1-minute bucket" even mean when talk turns don't
  align to minute boundaries — does a turn spanning 0:58–1:04 belong to bucket 0 or bucket 1, or both?
  If "both," you're back into proposal 3's overlapping-unit problem for agreement statistics. I'd
  default to assigning a turn (or the lines within it) to the bucket containing its *start* time —
  simple, deterministic, and every other unit type in `qc` already uses a "starts here" convention
  (`Location.start_line` is what's compared for agreement, e.g. `viewer.py:900-901`).
  > Agreed, we need to respect the non-overlapping units invariant above 
- Krippendorff's Alpha stays valid under fixed, non-overlapping intervals for the same reason as
  proposal 2 — disjoint buckets, binary presence/absence per bucket. It stops being valid the moment
  buckets overlap or a unit can belong to two buckets, same as proposal 3.

> Also needs consideration: How would time-series indices be declared in settings? Presumably it's an error
> if you try to add a time-series index when any documents in the corpus don't have timestamps?
> If you already have a time-series index (even one which you previously declared but don't curently
> declare, but which persists in the db), does this prohibit ever importing a non-timestamped document?

> > I'd answer both "no" — a time-series index should behave like any other index in the additive model:
> > per-document, not corpus-wide. Declaring `delimiters: minute: {type: interval, size: 60}` in settings
> > just says "this name is a legal unit to ask for"; it says nothing about which documents can produce it.
> > A document only gets `Location` rows under `"minute"` if *its* importer produced timestamped captions
> > (i.e., it has a `"turns"` base index to derive buckets from) — a plain-text document imported via
> > `pandoc`/`verbatim` simply never gets one, the same way it never gets a hypothetical `"speaker"` index
> > either. So: not an error to declare it in a mixed corpus, and importing a future non-timestamped
> > document afterward doesn't need to be prohibited or even warned about — it just won't have that index,
> > exactly like every other document-specific capability already works.
> >
> > Where I *would* want a check is at query time, not declaration time: if someone runs `--unit minute`
> > and every document in the filtered set lacks a `"minute"` index, that's worth distinguishing from "ran
> > fine, zero units" — `show_agreement` already has a similar guard ("No documents found for the given
> > filters," `viewer.py:907-909`); I'd add a sibling message ("No documents have a 'minute' index") so a
> > typo'd or premature `--unit` reads as a mistake to investigate, not a silent empty result.

> Agreed. Also maybe we should add a -v/--verbose flag on all queries, which would report which documents 
> (and which coders and which codes) were included in the query). 

> > > That's a natural extension of the same guard, actually — once a command is already computing "which
> > > documents/coders/codes matched the filters" to check for the empty case, `--verbose` is just
> > > choosing to print that resolved set unconditionally instead of only when it's empty. I'd add it as a
> > > shared option (one decorator, alongside `-n/--unit`'s repeated-but-identical definition across
> > > `stats`/`crosstab`/`find`/`agreement`) that prints, before the normal output: matched document paths,
> > > coder names, and code names (post-`--recursive-codes` expansion, since that's often the surprising
> > > part — which child codes actually got pulled in). Small, general, and worth doing alongside the
> > > `-n/--unit` CLI work in proposal 2 rather than as its own effort, since it touches the same set of
> > > commands.

Net: I'd treat this as two separable pieces of work — talk-turn units (cheap, rides on proposal 2) and
timestamp-interval units (a real schema + importer change, worth doing but scoped as its own follow-up
rather than folded into the paragraph-delimiter work).

## Plan

### Invariants

- Coding always happens at the line level. Unit of analysis is a query-time aggregation choice, not a
  coding-time one — the traditional "pick one unit up front" workflow is the special case where every
  query uses the same `--unit`.
- Units are disjoint subsets that completely cover a document. No overlapping units.
- Indices are generated only from a document's text. Nothing that isn't recoverable by re-scanning the
  text may back an index — required for both `qc corpus update` reindexing and REFI-QDA round-tripping.

### Bug fixes (unconditional)

- `iter_paragraph_lines`: fix `NameError` on a 0-line file — should yield 0 paragraphs, not crash.
- Fix the form-feed (`\x0c`) line-counting desync in `show_agreement`'s line-unit domain
  (`viewer.py:877`) and `refi_qda/writer.py`'s `line_positions`, bringing them in line with the
  `splitlines()`-based counting `5be24bb` already established elsewhere — via one shared helper, not
  another independent reimplementation.
- Delete the dead, inconsistent `prepare_corpus_text` (`helpers.py`).
- `qc corpus update` rebuilds every declared `DocumentIndex` automatically, not just leaving
  `"paragraphs"` (or any other index) stale relative to the new text.
- No change to: all-blank-line documents forming one legitimate paragraph, or blank-line detection
  using Python's `str.isspace()` definition — both already correct/settled.

### Named delimiters (settings-defined indices)

- `settings.yaml` gains a `delimiters` mapping; `unit` may be set to any key in it, in addition to the
  built-in `line`/`document`. `line` and `document` are reserved names — validation rejects a
  `delimiters` entry using either.
- Delimiters start as line-anchored regexes (a matching line opens a new unit); the interface is
  generic (`(start, end)` ranges over lines) so other strategies (e.g. fixed line count) can be added
  later without changing the model.
- Indices are additive: adding or removing a `delimiters` entry never destroys other indices.
  `qc corpus update` reindexes every declared index every time, automatically — no separate reindex
  command, no user bookkeeping.
- `-n/--unit` becomes a plain string validated against settings at runtime (not a fixed
  `click.Choice`), consistently across `stats`/`crosstab`/`find`/`agreement`.
- Embedding `window_before`/`window_after` remains a line-only setting; it does not generalize to
  paragraph/section/other units, which are assumed to carry enough context on their own.

### Time-series indices (VTT)

- New `vtt` importer preserves timestamps **inline in the visible text** per turn (e.g.
  `[00:00:01.200 --> 00:00:04.500] Alice: Hello there.`) — never discarded, never DB-only.
- The `"turns"` time-series index is built by a delimiter that extracts the timestamp from that same
  inline marker, satisfying "indices generated only from text." `Location` gains nullable
  `start_time`/`end_time` columns, populated only for time-series indices.
- `"paragraphs"` is built exactly as today (blank-line rule) over the same text, unaffected by the
  inline timestamp markers.
- Coarser interval buckets (e.g. 1-minute) are derived groupings of `"turns"` locations by timestamp;
  a unit spanning a bucket boundary is assigned by its *start* time (no overlap, per the invariant).
- `vtt-to-text` is a new, separate importer preserving today's lossy, timestamp-free, readable-prose
  behavior — no time-series index, explicit opt-in, default `vtt` behavior is not silently changed.
- Declaring a time-series delimiter in settings is never an error for a mixed corpus — a document only
  gets `Location` rows for indices its own importer actually produced. At query time, if `--unit`
  matches zero documents' indices, report that explicitly rather than silently returning an empty
  result (extending the existing "no documents found" guard in `show_agreement`).

### REFI-QDA round-trip

- Package `qc`'s `settings.yaml` (delimiters, unit, embedding params, etc.) into the `.qdpx`'s
  `Description` field on export; the reader restores it and re-runs indexing from it, rather than
  discarding it as it does today.
- Embeddings: package inside `.qdpx` as an explicit opt-in (`qc export --with-embeddings`), not
  regenerated from recorded model parameters — cloud/hosted models aren't guaranteed deterministic even
  with identical params, so recorded params are provenance metadata, not a reproduction mechanism.

### Structured export (CSV/JSON)

- Generalize the "unit boundary" concept: each index type owns its own boundary serialization —
  `start_line`/`end_line` always present (every index is still a line partition underneath);
  `start_time`/`end_time` additionally present for time-series indices; open to further index-specific
  fields later (e.g. a sentiment-tagged index). `codes find`'s JSON/CSV output reflects whatever fields
  are meaningful for the active index.
- `stats`/`crosstab`/`agreement` CSV shape is unchanged — they don't expose per-unit boundaries for any
  unit type today.

### DB schema migration infrastructure

- Generalize `QCMigration` so `apply`/`revert` can alter the DB schema, not only `settings.yaml`.
- `migration_2_0_0` (autocode settings nesting) ships as already written. `Location.start_time`/
  `end_time` plus the schema-migration mechanism itself ship as `migration_2_1_0`. The public release
  can jump straight to `2.1.0`.

### Query UX

- Add `-v/--verbose` to `stats`/`crosstab`/`find`/`agreement`: prints the resolved document, coder, and
  code set (post `--recursive-codes` expansion) before normal output, sharing its filter-resolution
  logic with the "no matching documents/index" guards above.

### Explicitly deferred or rejected

- Sliding-window unit of analysis — rejected: violates the disjoint-units invariant and breaks the
  independence assumption behind alpha/kappa/F1.
- A separate proximity/tolerance-window agreement metric (the real need behind the sliding-window ask)
  — good idea, not being built now.
- Generalizing the embedding window to non-line units — rejected as likely to confuse users.
- `corpus anonymize --redact-all` (full-text redaction for sharing codes without source text) — good
  idea, not being built now.
- Configurable aggregation rules (e.g. majority-vote instead of "any line coded") — not pursued; no
  concrete need yet, and it multiplies the design space for every metric.
