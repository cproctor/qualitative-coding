Background
==========

Theoretical framework
---------------------

Qualitative data analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

``qc`` is designed to support the application of computational thinking
(CT) to the process of qualitative data analysis (QDA). In the social
sciences, QDA is a process of applying codes to text, images, video, and
other artifacts, then analyzing the resulting patterns of codes and
using the codes to more deeply understand the text. The adjective
"qualitative" applies to the data being analyzed (that is, the data
represents or describes something that happened) and potentially also to
the research design.

When QDA is used in quantitative or mixed-methods research, it is
typically used as a means of transforming loosely-structured data such
as an interview transcript into categories or codes which can then be
used in downstream quantitative analysis. Within this paradigm, the data
resulting from QDA are typically treated as observable variables
standing in for latent representing latent constructs of interest. The
researcher will prioritize reliability in QDA. Reliability means that if
another researcher were to repeat the QDA process, they should expect
similar results. If the QDA is not reliable, then there is no
justification for claiming that the results of downstream analysis
applies to the situation represented by the qualitative data. (Concern
for validity often goes hand in hand with concern for reliability, but I
do not address validity here because it is more related to how QDA
supports a research argument than the process of QDA, and therefore less
germane for the design rationale for a QDA tool.) Strategies for
improving reliability vary according to methodology, but generally
include the use of standardized codebooks, processes for training
coders, and using measures of inter-rater agreement to confirm that
different coders tend to arrrive at similar results.

In contrast, the goal of qualitative research is to interpret, explain,
or "make the world visible" (Denzin and Lincoln 2011), often with
central interest in how the researcher's subjectivity (their sense of
who they are) or positionality (their relationship to what is being
studied) shapes the results. Reliability is often irrelevant to a
qualitative research design; the reality under study is understood to be
produced through the research, so the researcher's subjectivity and
positionality are essential traces of that process. Nevertheless, making
the QDA process transparent by documenting and sharing the researcher's
iterative process of coding texts and developing interpretations would
make qualitative research more persuasive, and could help other
researchers understand the specific process which led to the results.

Commercial QDA software packages such as NVivo, Dedoose, Atlas.TI, and
MaxQDA, are widespread and well-known; they are commonly taught in
qualitative methods courses, and are a core part of many research
groups' methodologies. That said, my own observations suggest that there
is quite a bit of heterogeneity in whether and how such tools are used
in practice; collaborators' preferences or budget pressure sometimes
leads to a "lowest common denominator" of coding texts manually, or
using ad-hoc tools such as word processors or spreadsheets. These can
get the job done, but they have significant limitations with respect to
interpretability and documentation of process. As the corpus or the
research team grows, ad hoc tools become increasingly unwieldy.

Within the qualitative research community, there is a long-running
thread of skepticism toward QDA software (Jackson, Paulus, and Woolf
2018), focused on four main concerns: that digital tools create distance
between the researcher and the data; that if particular digital tools
become dominant they may homogenize and standardize qualitative
research; that digital tools mechanize and dehumanize qualitative
research; and that digital tools decontextualize qualitative data by
privileging quantification. The design rationale of ``qc`` takes these
concerns seriously, but argues that for users who are able to
conceptualize the QDA process in computational terms, a tighter
partnership with the computer may yield more intimate, situated,
humanized insights grounded in the researcher's subjectivity.

Computational thinking
~~~~~~~~~~~~~~~~~~~~~~

The central design hypothesis of ``qc`` is that a closer partnership
between the researcher and the computational tool can enhance the
quality of QDA. The kind of close partnership I have in mind depends on
the researcher's ability to conceptualize the data and the process in
computational terms, becoming immersed in the matrices, trees, and other
computational structures inherent to QDA rather than remaining "outside"
at the level of user interface. This practice, called *computational
thinking*, has been defined as "the thought processes involved in
formulating problems and their solutions so that the solutions are
represented in a form that can effectively be carried out by an
information-processing agent" (Wing 2011, 33). The application of CT to
QDA would mean conceptualizing the goal and the process of QDA in
computational terms, keeping a mental model of the work the computer is
doing for you.

All QDA software will be a "leaky abstraction" (Spolsky 2002), a
simplification which aims to let the user get their work done without
needing to worry about the complexity of how the work is
accomplished–and which only partially succeeds at this goal. Therefore,
actively thinking about how one's tools are modeling the problem is
necessary, or at least has the potential to improve the tool's
effectiveness. As an analogy, statistical software can be a powerful
tool which improves the efficiency and quality of research, but only
when the user has a clear conceptualization of what they are trying to
achieve and what the software is going to do for them. This requires a
certain amount of expertise on the part of the user as well as a greater
commitment to learning the tool, but asking such a commitment from the
user is justifiable. There are many fields in which experts invest in
learning specialized domains of computing. Examples include
computer-aided design in architecture, expert use of Excel in finance,
and even word-processing for users who choose to invest in learning vim
or emacs. In all of these cases, the user has to get involved at least
to some extent in the work the tool is doing for them.

In my own experience with QDA, several computational structures are
often salient; thinking about them has been helpful in improving both
the efficiency and the quality of my QDA practice. The codebook's nested
tree of codes is the structure within which themes emerge from codes.
Open coding produces a flat list of codes; an iterative process of
grouping related codes together under parent codes gradually produces a
hierarchy of increasingly-grauluar meanings, often with several
top-level themes. ``qc``\ 's affordances for showing code statistics and
finding coded excerpts of codes and their children helps guide this
process. I often conceptualize the process of querying for statistics
and coded examples in terms of a relational database, scoping queries by
code, coder, and document. Finally, I draw on concepts and practices
from version control systems such as git in managing research progress.
Tracking changes to the project makes it easier to document the process,
step back to previous versions, and to maintain multiple versions in
parallel.

Design rationale
----------------

This section explains how several design decisions support ``qc``\ 's
goal of engaging CT in the QDA process.

Command-line interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most surprising decision in the design of ``qc`` may be its
implementation as a command-line utility rather than a graphical user
interface such as a web application. Users who are not already persuaded
of the value of a text-based user interface (CLI) are unlikely to choose
this tool. While a graphical user interface (GUI) provides stronger
affordances (disclosing the actions available to the user), a CLI
requires the user to make a cognitive reach for what they are looking
for. In my own experience, however, a CLI invites a more active stance
than a GUI, requiring the user to reach "into" the sensemaking process,
maintaining an internal model of the emerging qualitative analysis.

A CLI is particularly strong where the underlying model is too complex
to present in its entirety in a single view. QDA is an example of such a
situation. Even in a moderately-sized corpus, there is too much text to
be able to engage it directly and there are too many codes to hold in
mind at once (never mind their emergent tree structure). If a GUI were
to support such complex queries, it would likely be tucked away in a
menu and would require a complex form–losing the GUI's advantages in
discoverability.

Rich query interface
~~~~~~~~~~~~~~~~~~~~

Many of ``qc``\ 's commands can be thought of as views onto the model;
in my QDA process I am constantly moving between coding, viewing
examples of previosuly-applied codes, revising the structure of the
codebook, running analyses, and writing memos. From time to time I am
also interested in comparing my coding with that of other team members.
``qc``\ 's queries offer a powerful array of options. Consider the
following query, whose complexity is not atypical in normal usage:

.. code-block:: console

   % qc codes stats equity participation --recursive-codes --recursive-counts \
   --pattern round1 --min 5 --depth 2 --unit paragraph --format latex

This query reports counts for the codes "equity," "participation," and
all their subcodes, showing usage for the code itself as well as a sum
of counts for all subcodes, restricting the count to documents whose
names match "round1" and using the paragraph as a unit of analysis. The
query only reports codes which were used at least five times, and only
goes two levels deep in the hierarchy. Finally, the output is formatted
as latex.

The specifics of these options are covered in the following sections;
what is important from a design perspective is how a query can be built
up from multiple options similar to query-builder libraries in
high-level programming languages which offer idiomatic interfaces for
constructing SQL queries. This design is also informed by the UNIX
philosophy (McIlroy, PInson, and Tague 1978), that programs should do
one thing but do it well.

.. _textfiles:

Storing data in text files
~~~~~~~~~~~~~~~~~~~~~~~~~~

All files related to a ``qc`` project are contained within a directory:

::

   project
   ├── codebook.yaml
   ├── corpus
   │   ├── admin.txt
   │   ├── board_member.txt
   │   └── teacher.txt
   ├── memos
   ├── qualitative_coding.log
   ├── qualitative_coding.sqlite3
   └── settings.yaml

At first glance, it may be surprising that project data is stored in
three different locations and formats (plain text files within the
corpus directory, the codebook in a ``yaml`` file, and other data in a
``sqlite3`` relational database), but there are practical benefits.
Corpus files are plain text, so they can be integrated into pipelines as
part of a broader research workflow. ``yaml`` is a structured data
format designed for human reading and writing, well-suited for editing
the tree of codes. Other project data, including relationships between
codes and document lines, is stored in a standard relational database in
a straightforward schema which could be integrated into other
applications. (The initial version of ``qc`` stored all data in text
files; the database was added to improve performance.) In almost all of
our existing ``qc`` projects, QDA is part of an analytical pipeline. The
prior and subsequent processes operate on these standard interfaces,
supporting flexible and creative uses of qualitative coding.

.. _principled-llms:

Principled use of LLMs
~~~~~~~~~~~~~~~~~~~~~~

The argument for CT in QDA cuts in two directions. It supports the case
for tools like ``qc``: a researcher who can hold computational structures
in mind will be a more effective analyst. But it also generates an
obligation: such a researcher should apply the same critical,
transparent thinking to AI tools that they apply to their other
methods. The emergence of large language models (LLMs) in qualitative
research warrants exactly this kind of scrutiny.

Most major QDA software packages now offer AI-assisted coding, typically
implemented by sending excerpts to an LLM along with a prompt. The LLM
reads the text and returns suggested codes. This approach is efficient,
but it raises all four of the concerns Seidel originally directed at QDA
software—with greater force. An LLM "just coding" a transcript is
opaque: it is not clear what the model is responding to, whether its
judgments are consistent, or how those judgments relate to the
researcher's own evolving interpretations. It is difficult to reproduce:
LLM outputs may vary across API versions, prompt changes, or random
seeds. And it risks being dehumanizing not only for the researcher
(reducing their role to prompt engineer) but also for the research
participants, whose words are processed by a system optimized to produce
plausible-sounding text.

``qc``\ 's approach to AI-assisted coding is shaped by three principles.
First, AI should *augment* the researcher's efficiency and quality, not
replace the researcher's judgment. The autocode system trains on the
researcher's own prior coding, so predictions are grounded in and
calibrated against the analyst's interpretive framework. The model
identifies its own uncertainty and asks the researcher to resolve it,
keeping the researcher's judgment at the center of the process. Second,
AI use should be *transparent and reproducible*. Every autocode session
logs the exact hyperparameters (embedding model, unit of analysis,
classifier settings) and training-data provenance that produced
predictions. Because classifiers are always rebuilt from cached embeddings
and the current database, any later point in the project's git history
is exactly reproducible. Third, the relationship between researcher and
AI tool should be *humanizing*. The active-learning loop makes the
researcher's categories and uncertainty visible to them, supporting
reflection on what the codes mean rather than simply affirming the
researcher's existing judgments. The human reviews, corrects, and
extends predictions; the AI handles scale and surfaces its own
limitations honestly.

These principles are not merely rhetorical. They have direct
architectural consequences: no trained model is persisted to disk (the
classifier is always rebuilt fresh from data the researcher controls);
predictions are written as a named coder and can be compared against
human coding with inter-rater agreement statistics; and the researcher
can discard an entire round of predictions with a single command if the
quality is unsatisfactory.

Technical background
--------------------

This section provides a conceptual and technical introduction to the
structures and methods underlying ``qc``. It is intended to be
accessible to researchers without a machine-learning background, while
also justifying specific design choices to readers who are familiar with
these methods.

.. _autocode:

Qualitative coding
~~~~~~~~~~~~~~~~~~

The codebook is the researcher's vocabulary for the analysis. Codes are
short labels—a word or phrase—applied to lines of a corpus document to
mark that the content of that line is an instance of the concept the
code names.

**Open coding** treats the codebook as emergent: codes are invented by
the researcher on the fly as they read the data, without a predefined
list. This approach is common in grounded theory and other inductive
methodologies where the goal is to let categories arise from the data
rather than imposing a prior framework. An initial round of open coding
typically produces a large, flat list of codes; subsequent passes refine
and consolidate them. ``qc``\ 's codebook is a ``yaml`` file that the
researcher edits directly; running ``qc codebook`` ensures that all
codes applied in the corpus are represented in the file.

**Closed coding** starts from a predefined codebook derived from theory,
prior literature, or a specific instrument. The researcher applies only
those codes, making their analytical framework explicit from the outset.
In practice, many projects use a hybrid approach: a core theoretical
codebook supplemented by new codes that emerge during analysis.

**Hierarchical code trees** organize codes into a parent-child structure
that captures conceptual relationships. A code such as ``equity`` might
have children ``access``, ``representation``, and ``outcomes``. This
nesting serves two related purposes. First, it organizes the codebook
conceptually, grouping related codes and making the analytical framework
legible. Second, it enables flexible querying: ``qc codes stats equity
--recursive-codes`` reports counts for ``equity`` and all its
descendants, while ``qc codes stats equity`` reports only direct
applications of the parent code. Researchers often begin with a flat
list and impose structure as themes emerge.

**Unit of analysis** determines what a code is applied *to*. In ``qc``,
codes are always applied to individual lines of a corpus document—this
is the fundamental unit of storage. However, ``qc`` supports reporting
at coarser units: the ``--unit`` option (or the ``unit`` setting in
``settings.yaml``) controls whether counts and co-occurrence statistics
are computed at the line, paragraph (blank-line delimited), or document
level. A code is considered to apply to a paragraph if it appears on any
line within that paragraph, and to a document if it appears anywhere in
the document. For the autocode system, the unit of analysis additionally
controls how corpus text is chunked for embedding: a ``line`` embedding
uses a small window of surrounding lines for context; a ``paragraph``
embedding uses the full paragraph; a ``document`` embedding uses the
entire document.

Evaluation
~~~~~~~~~~

Evaluating the quality of coding—whether human or machine—is important
for establishing the credibility of an analysis. ``qc`` supports several
complementary approaches via ``qc codes agreement``.

**Inter-rater agreement** quantifies the agreement between two or more
coders' judgments about the same documents. *Krippendorff's alpha* is
appropriate when multiple coders have coded the same material on equal
footing; it handles unequal numbers of ratings and missing data
gracefully, which is common in qualitative research. *Cohen's kappa* is
a pairwise, chance-corrected agreement coefficient appropriate when
exactly two coders are being compared. Both metrics treat each text unit
(line, paragraph, or document) as a binary judgment for each code: is
this code present or absent? Values above 0.80 are generally considered
excellent; above 0.60 is acceptable; below 0.40 suggests substantial
disagreement. *F1 score* is appropriate when one coder is treated as the
authoritative reference (e.g., evaluating autocode predictions against a
gold-standard human coder): *precision* measures what fraction of the
model's predictions are correct; *recall* measures what fraction of the
true positive cases the model identified.

**Cross-validation** (``qc codes agreement --metric cv``) provides an
estimate of how well the autocode model will perform on *new, unseen*
examples, before any new predictions are written to the database. The
procedure divides the existing human-coded examples into groups
(*folds*), repeatedly training on all but one fold and evaluating on the
held-out fold. The resulting precision, recall, and F1 scores estimate
the model's likely quality on the unreviewed documents. Because this
evaluation is entirely internal to the human-coded portion of the
corpus, it costs nothing in terms of new coding effort or API calls
(embeddings are already cached). Cross-validation is most informative
when each code has at least ten to twenty coded examples; the minimum
required for training is set by ``autocode_min_examples`` (default: 5).

**A note on what these numbers mean**: a cross-validated F1 of 0.75
for a code does not mean that 25% of predictions will be wrong—it is
an estimate under the distributional assumptions of the training data.
Codes whose examples are semantically coherent (few near-synonyms in
the embedding space, clear contrast with other codes) tend to achieve
higher scores. Scattered codes, or codes that are conceptually very
close to one another, tend to score lower. This diagnostic information
helps the researcher decide which codes to trust for bulk prediction
and which require more human-in-the-loop review.

Embeddings
~~~~~~~~~~

The core challenge in automating any part of text analysis is that
computers do not understand language. What they can do is perform
arithmetic on numbers. The first step in autocode is therefore to
convert each piece of text—a line, paragraph, or document—into a list
of numbers that represents its meaning. This conversion is called
*embedding*.

An embedding is a list of typically hundreds or thousands of numbers
(a *vector*) that places a piece of text in a high-dimensional
space. The key property is that texts with similar meanings end up
close together in this space. "Every student deserves a chance" and
"All kids should have access to CS" would have similar embeddings;
"The budget meeting is at 3 pm" would be far from both. This
proximity relation is meaningful enough to support a surprisingly
wide range of analytical tasks.

``qc`` obtains embeddings by sending text to an OpenAI-compatible
embedding API—either a locally-hosted model (such as `Ollama
<https://ollama.com>`__ or `LM Studio <https://lmstudio.ai>`__) or a
cloud-based service. The ``autocode_api_base`` and
``autocode_api_model`` settings configure which service is used. Using
a local model keeps all data on the researcher's own machine, which is
important for research involving sensitive or confidential data.

For the *line* unit of analysis, ``qc`` embeds each line together with
a small window of surrounding lines (configurable with
``autocode_window``), providing the classifier with context. For the
*paragraph* unit, the full paragraph text is embedded; for the
*document* unit, the full document. Embeddings are cached on disk, so
the API is only called once per document; subsequent retraining,
prediction, and analysis draw on the cached values.

Beyond classification, embeddings support several diagnostic analyses
that do not require any new API calls once the cache is populated. The
*centroid* of a code's embeddings is the average position of all
coded lines in embedding space; this geometric summary enables three
analytical commands. ``qc autocode outliers`` identifies coded lines
whose embeddings are far from their code's centroid—these are likely
miscodes or edge cases worth reviewing. ``qc autocode density`` reports
per-code cohesion as mean pairwise cosine distance among a code's
embeddings; a tight cluster indicates a well-defined code, while a
scattered distribution suggests a vague or over-broad code that may
benefit from splitting. ``qc autocode similar`` computes pairwise
distances between code centroids and surfaces pairs of codes that are
close in embedding space—candidates for merging or for scrutiny of how
the researcher has drawn conceptual boundaries.

Classification
~~~~~~~~~~~~~~

With embeddings in hand, the question becomes: given a new piece of
text, does it belong to a particular code? This is a *binary
classification* problem—for each code, every piece of text is either
an instance of the code or it is not.

``qc`` trains one classifier per code, using the researcher's existing
human coding as training data. Lines coded with, say, ``equity`` are
*positive examples*; a random sample of other coded lines serves as
*negative examples*. The classifier learns a boundary in the embedding
space that separates the two groups.

The specific classifier used is a *Support Vector Machine* (SVM) with
a linear kernel. SVMs are a well-established method for high-dimensional
classification problems. Conceptually, an SVM finds the hyperplane in
the embedding space that maximally separates positive from negative
examples—maximizing the *margin* between the boundary and the nearest
examples on each side. This maximum-margin property tends to produce
classifiers that generalize well to new examples without requiring large
amounts of training data, which suits the typical scale of a QDA
project (tens to hundreds of coded examples per code rather than
thousands).

Because the raw SVM does not produce probability estimates, ``qc`` wraps
it in a calibration layer (Platt scaling) that converts the model's
output to a confidence score between 0 and 1. This score represents the
model's estimated probability that a given piece of text belongs to the
code. Confidence scores are used to threshold predictions
(``autocode_confidence_threshold``), to navigate the code tree
(``autocode_child_threshold``), and to identify uncertain cases during
active learning.

No trained model is ever written to disk. Classifiers are rebuilt
on-demand from the cached embeddings and the current state of the
database. Rebuilding takes milliseconds, so there is no practical cost
to this approach, and it ensures that the researcher always knows
exactly what data produced the predictions currently in their database.

Active learning
~~~~~~~~~~~~~~~

Uncertainty is not a limitation of the model to be minimized; it is
information about where the researcher's attention would be most
valuable. *Active learning* operationalizes this insight: rather than
applying the classifier blindly to all unreviewed documents, ``qc``
identifies the specific pieces of text where the model is most confused
and presents them to the researcher for review.

``qc`` uses *margin sampling* to rank text units by uncertainty. For
each unreviewed piece of text, the model produces confidence scores for
all trained codes. The *margin* is the difference between the highest
and second-highest confidence score. A small margin means the model
cannot decide between two competing codes—exactly the kind of ambiguous
case that most benefits from human judgment.

After the researcher codes a high-uncertainty unit, the classifiers are
retrained with the new annotation and the uncertainty ranking is
recomputed. Each annotation propagates immediately to future
uncertainty estimates—the system is always learning. The session
continues until the researcher stops or until all remaining uncertainty
falls below a configurable threshold, at which point bulk prediction
can proceed with greater confidence.

This loop—embedding, training, uncertainty-driven human review,
retraining—implements a form of *online learning*, where the model
and the researcher are continuously in dialogue. Unlike a static
classifier trained once and deployed, the system's predictions become
progressively better-aligned with the researcher's specific
interpretive framework as the project develops.

.. _interop:

Interoperability with other QDA software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A working group representing the major QDA software vendors published
the REFI-QDA standard (van Blommestein 2019) specifying a standard data
format for moving QDA projects between software platforms. ``qc``
supports the REFI-QDA standard, allowing projects to be imported and
exported.

However, the REFI-QDA standard recognizes that designs of QDA software
will vary, and the standard does not require that compliant products
import or export with complete fidelity. As noted in the REFI-QDA
standard 1.5, data loss is likely when a project is exported from one
QDA software package into another and back (roundtripping), as neither
package is obliged to implement the full specification. ``qc``\ 's user
interface and data model are quite different from well-known GUI-based
alternatives. Specifically:

-  Whereas most QDA software allows users to code highlighted
   *selections* in text documents (identified by start and end character
   positions), the fundamental unit of analysis in ``qc`` is the line.
   Exported ``qc`` projects represent coded lines as selections ranging
   from the first to the last character in the corresponding line. When
   QDA projects are imported into ``qc``, selections are mapped onto the
   first corresponding line.
-  *Cases,* or groupings of corpus documents, are not explicitly
   supported in ``qc``, although ``qc`` corpus documents can be
   organized into a nested directory tree. Every relevant ``qc`` command
   affords filtering documents by pattern or by explicit file list, so
   documents can effectively (but implicitly) be treated as belonging to
   cases.
-  ``qc`` corpus documents do not have variables.
-  Nested codes are central to the operation of ``qc``, and every node
   in the code tree is considered a code. Sets (groupings of codes which
   are not themselves codes) are not supported.
-  *Notes* as defined in the REFI-QDA standard are implemented as memos
   in ``qc``, and belong to the project, not to corpus documents or to
   selections. The REFI-QDA standard supports coding of notes. This is
   not explicitly supported in ``qc``, but memos could be imported into
   the corpus and then coded if desired.
