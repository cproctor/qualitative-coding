Introduction
============

This documentation introduces ``qc``, a free, open-source software package for
qualitative data analysis (QDA) designed to support the application of
computational thinking (CT) to qualitative research. 

QDA, in its various
forms, is a core methodology for qualitative, mixed methods, and some
quantitative research in the social sciences. There are a variety of
well-known commercial QDA software packages such as NVivo, Dedoose,
Atlas.TI, and MaxQDA. I have used several of these individually and in
research groups; ``qc`` emerged from my loosely-theorized
dissatisfaction with these tools. I value open and extensible research
software; these were proprietary and expensive. I value “plain-text
social science” (Healy 2020); these graphical user interfaces (GUIs)
were user-friendly but ultimately limiting. As I developed prototypes of
``qc`` for my own use in several prior research projects (Proctor,
Bigman, and Blikstein 2019), I found that I was continually augmenting
(Engelbart 1962) my ability to engage with complexity rather than
simplifying the problem space. The release of ``qc`` documented here
results from a redesign and reimplementation of the original tool, in
the hope that it will be useful to others.

Background
==========

Qualitative data analysis
-------------------------

``qc`` is designed to support the application of computational thinking
(CT) to the process of qualitative data analysis (QDA). In the social
sciences, QDA is a process of applying codes to text, images, video, and
other artifacts, then analyzing the resulting patterns of codes and
using the codes to more deeply understand the text. The adjective
“qualitative” applies to the data being analyzed (that is, the data
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
or “make the world visible” (Denzin and Lincoln 2011), often with
central interest in how the researcher’s subjectivity (their sense of
who they are) or positionality (their relationship to what is being
studied) shapes the results. Reliability is often irrelevant to a
qualitative research design; the reality under study is understood to be
produced through the research, so the researcher’s subjectivity and
positionality are essential traces of that process. Nevertheless, making
the QDA process transparent by documenting and sharing the researcher’s
iterative process of coding texts and developing interpretations would
make qualitative research more persuasive, and could help other
researchers understand the specific process which led to the results.

Commercial QDA software packages such as NVivo, Dedoose, Atlas.TI, and
MaxQDA, are widespread and well-known; they are commonly taught in
qualitative methods courses, and are a core part of many research
groups’ methodologies. That said, my own observations suggest that there
is quite a bit of heterogeneity in whether and how such tools are used
in practice; collaborators’ preferences or budget pressure sometimes
leads to a “lowest common denominator” of coding texts manually, or
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
humanized insights grounded in the researcher’s subjectivity.

Computational thinking
----------------------

The central design hypothesis of ``qc`` is that a closer partnership
between the researcher and the computational tool can enhance the
quality of QDA. The kind of close partnership I have in mind depends on
the researcher’s ability to conceptualize the data and the process in
computational terms, becoming immersed in the matrices, trees, and other
computational structures inherent to QDA rather than remaining “outside”
at the level of user interface. This practice, called *computational
thinking*, has been defined as “the thought processes involved in
formulating problems and their solutions so that the solutions are
represented in a form that can effectively be carried out by an
information-processing agent” (Wing 2011, 33). The application of CT to
QDA would mean conceptualizing the goal and the process of QDA in
computational terms, keeping a mental model of the work the computer is
doing for you.

All QDA software will be a “leaky abstraction” (Spolsky 2002), a
simplification which aims to let the user get their work done without
needing to worry about the complexity of how the work is
accomplished–and which only partially succeeds at this goal. Therefore,
actively thinking about how one’s tools are modeling the problem is
necessary, or at least has the potential to improve the tool’s
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
the efficiency and the quality of my QDA practice. The codebook’s nested
tree of codes is the structure within which themes emerge from codes.
Open coding produces a flat list of codes; an iterative process of
grouping related codes together under parent codes gradually produces a
hierarchy of increasingly-grauluar meanings, often with several
top-level themes. ``qc``\ ’s affordances for showing code statistics and
finding coded excerpts of codes and their children helps guide this
process. I often conceptualize the process of querying for statistics
and coded examples in terms of a relational database, scoping queries by
code, coder, and document. Finally, I draw on concepts and practices
from version control systems such as git in managing research progress.
Tracking changes to the project makes it easier to document the process,
step back to previous versions, and to maintain multiple versions in
parallel.

Design rationale
================

This section explains how several design decisions support ``qc``\ ’s
goal of engaging CT in the QDA process.

Command-line interface (CLI)
----------------------------

The most surprising decision in the design of ``qc`` may be its
implementation as a command-line utility rather than a graphical user
interface such as a web application. Users who are not already persuaded
of the value of a text-based user interface (CLI) are unlikely to choose
this tool. While a graphical user interface (GUI) provides stronger
affordances (disclosing the actions available to the user), a CLI
requires the user to make a cognitive reach for what they are looking
for. In my own experience, however, a CLI invites a more active stance
than a GUI, requiring the user to reach “into” the sensemaking process,
maintaining an internal model of the emerging qualitative analysis.

A CLI is particularly strong where the underlying model is too complex
to present in its entirety in a single view. QDA is an example of such a
situation. Even in a moderately-sized corpus, there is too much text to
be able to engage it directly and there are too many codes to hold in
mind at once (never mind their emergent tree structure). If a GUI were
to support such complex queries, it would likely be tucked away in a
menu and would require a complex form–losing the GUI’s advantages in
discoverability.

Rich query interface
--------------------

Many of ``qc``\ ’s commands can be thought of as views onto the model;
in my QDA process I am constantly moving between coding, viewing
examples of previosuly-applied codes, revising the structure of the
codebook, running analyses, and writing memos. From time to time I am
also interested in comparing my coding with that of other team members.
``qc``\ ’s queries offer a powerful array of options. Consider the
following query, whose complexity is not atypical in normal usage:

.. code-block:: console

   % qc codes stats equity participation --recursive-codes --recursive-counts \
   --pattern round1 --min 5 --depth 2 --unit paragraph --format latex

This query reports counts for the codes “equity,” “participation,” and
all their subcodes, showing usage for the code itself as well as a sum
of counts for all subcodes, restricting the count to documents whose
names match “round1” and using the paragraph as a unit of analysis. The
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
--------------------------

All files related to a ``qc`` project are contained within a directory:

::

   project
   ├── codebook.yaml
   ├── corpus
   │   ├── admin.txt
   │   ├── board_member.txt
   │   └── teacher.txt
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
----------------------

The argument for CT in QDA cuts in two directions. It supports the case
for tools like ``qc``: a researcher who can hold computational structures
in mind will be a more effective analyst. But it also generates a
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

.. _autocode:

AI in QDA
=========

This section provides a conceptual introduction to the techniques
underlying ``qc``\ 's autocode features. It is intended to be accessible
to researchers without a machine-learning background, while also
justifying the specific design choices to readers who are familiar with
these methods.

Embeddings: from text to numbers
---------------------------------

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

Classification: learning from the researcher's codes
----------------------------------------------------

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

Evaluating the model
--------------------

Before committing to autocode predictions on unreviewed documents,
it is useful to estimate the model's likely quality. ``qc`` supports
two complementary approaches.

**Inter-rater agreement** (``qc codes agreement``) quantifies the
agreement between two or more coders' judgments about the same
documents. *Krippendorff's alpha* is appropriate when multiple coders
have coded the same material on equal footing; it handles unequal
numbers of ratings and missing data gracefully, which is common in
qualitative research. *Cohen's kappa* is a pairwise, chance-corrected
agreement coefficient appropriate when exactly two coders are being
compared. Both metrics treat each text unit (line, paragraph, or
document) as a binary judgment for each code: is this code present or
absent? Values above 0.80 are generally considered excellent; above
0.60 is acceptable; below 0.40 suggests substantial disagreement.
*F1 score* is appropriate when one coder is treated as the authoritative
reference (e.g., evaluating autocode predictions against a gold-standard
human coder): *precision* measures what fraction of the model's
predictions are correct; *recall* measures what fraction of the true
positive cases the model identified.

**Cross-validation** (``qc codes agreement --metric cv``) provides an
estimate of how well the model will perform on *new, unseen* examples,
before any new predictions are written to the database. The procedure
divides the existing human-coded examples into groups (*folds*),
repeatedly training on all but one fold and evaluating on the held-out
fold. The resulting precision, recall, and F1 scores estimate the
model's likely quality on the unreviewed documents. Because this
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

Active learning: making uncertainty productive
----------------------------------------------

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

Vignette
========

In the style of vignettes published with R packages (Wickham and Bryan
2023), this section provides a narrative introduction to ``qc``, guiding
a first-time user through installation and initial usage while also
pointing out features and suggesting workflows. The QDA workflow best
supported by ``qc`` is similar to that of other QDAS products: an
iterative cycle of “notice things,” “think about things,” and “collect
things” (Seidel 1998, 2). The primary difference between ``qc`` and
today’s well-known QDAS products is in the relationship between the user
and the software: ``qc`` provides different affordances for noticing,
thinking about, and collecting ideas during QDA.

Installation
------------

Start by following the steps in :ref:`installation`. 

Explore an existing project
---------------------------

The fastest way to experience what ``qc`` has to offer is to start with
an existing project: an excerpt from the coded interview transcripts
from members of a committee considering whether to add computer science
to the district’s primary and secondard schools (Proctor, Bigman, and
Blikstein 2019). The commands below create a directory on the Desktop,
download the demo project, and unpack it into the directory.

.. code-block:: console

   $ cd ~/Desktop
   $ curl -O https://computationalliteracies.net/people/chris/demo.qdpx
   $ mkdir qc_demo
   $ cd qc_demo
   $ qc init --import ../demo.qdpx

Now let’s use ``qc`` to look around this project. Which documents are
included in the corpus?

.. code-block:: console

   % qc corpus list
   admin.txt
   board_member.txt
   teacher.txt

What codes have been applied? ``qc codes stats`` will show all codes in
the codebook with a count of the number of uses across the whole corpus.
However this project was coded using open coding, resulting in 112
distinct codes–too many to easily comprehend. Instead, we will modify
the command to show the nested tree of codes, along with a count for
that specific code as well as a total for that code and all of its
children. Finally, ``--min 10`` filters out codes used fewer than ten
times.

.. code-block:: console

   % qc codes stats --recursive-codes --recursive-counts --min 10
   Code                              Count    Total
   ------------------------------  -------  -------
   rq1_definition                        5       55
   .  rationales                         0       27
   .    equity                          12       15
   rq2_curriculum_and_instruction        0       93
   .  curriculum                         4       47
   .    cs_scope_and_sequence            0       11
   .    graduation_requirement          16       16
   .    interdisciplinary_cs             2       11
   .  pedagogy                           4       43
   .    participation                    3       15
   .    tools                            1       14
   rq3_process                           0      102
   .  identity                           0       60
   .    computational_identity           6       27
   .    identity_categories              1       27
   .      gender                        20       20

We can zoom in on particular codes using the same command. For example,
the following command shows the code tree for ``rationales``, or
justifications given for why computer science ought to be taught in
primary and secondary schools. We again specify recursive codes and
recursive counts, this time using the short form of these flags
(``-ra``). We also add the ``--by-document`` flag, to get a sense of
differences across interviewees.

.. code-block:: console

   % qc codes stats rationales -ra --by-document
                                   admin.txt    board_member.txt    teacher.txt    Total
   -------------------------------  -----------  ------------------  -------------  -------
   rq1_definition:rationales                 12                  10              5       27
   .    equity                                7                   8              0       15
   .      every_student                       2                   0              0        2
   .      everyone_should_learn_cs            1                   0              0        1
   .    exposure                              3                   1              4        8
   .    job                                   2                   1              1        4

It appears that equity (as a rationale for teaching computer science)
came up more in interviews with the administrator and the board member
than with the teacher. To explore this pattern, we can we can view lines
coded with “equity,” or any of its child codes.

.. code-block:: console

   % qc codes find equity -r
   
   admin.txt (7)
   ================================================================================
   [40:45]
   learning computer science when I went to college at Organization_339 back in the |
   early '70s and I could see that was something that I thought, just like math,    |
   every kid should know. So, fast forward to when I got to Location_92, which was  | everyone_should_learn_cs
   in the early '80s, I got there in '83 and I started teaching computer science    |
   in about '85, as well as math and I recognized that it was a niche class and it  |

   [93:98]
   academic officer, the elementary academic officer, just figured we would spin    |
   our wheels and we wouldn't go anywhere but when we started talking about         |
   opportunity, she recognized that was an opportunity for all students and being   | equity
   a member of the underrepresented minority, she got behind us, which was great.   |
   However, this year, she did not come to our meetings because she didn't think    |
   
   [118:123]
   kids, that they would have English as a second language kids so that we could    |
   make sure that we were going to create a program that would meet the needs of    |
   all the students and create opportunity for all students to learn computer       | equity
   science, not just programming but the team work and the thinking, the            |
   analytical thinking that goes into computer science but definitely programming   |
   
Here’s an interesting pattern: the discussion of equity tends to be
framed in universal terms–what “every kid should know;” an “opportunity
for all students.” This consideration of what students should learn
feels connected to the “participation” codes under research question 2
(how CS should be taught) and the “committee_participation” codes under
research question 3 (the decision-making process which should be used).
We can use a cross-tabulation to quickly explore this idea. The ``-a``
flag again counts all subcodes. This time we omit ``-r``; including
subcodes as separate items in the cross-tabulation would make the table
unweildy.

.. code-block:: console

   % qc codes crosstab -a equity participation committee_participation
                   code    equity    participation    committee_participation
   -----------------------  --------  ---------------  -------------------------
                    equity        15                7                          0
             participation                         15                          0
   committee_participation                                                     9

The “equity” and “participation” codes co-occur quite a bit, but neither
co-occurs with “committee_particpation.” This illustrates one of the
paper’s findings: that many of the well-documented attitudes and
stereotypes that exclude students from computer science learning in the
classroom also appeared in decision-making processes about K12 computer
science, such as the committee under study.

The default unit of analysis is a line, so that the cross-tabulation
above shows how many lines have both codes. The ``--unit`` option could
be used to specify a different unit of analysis (``paragraph`` and
``document`` are supported; a window-based unit of analysis is under
development).

The next steps from here might include additional coding (using
``qc code``), adding hierarchical structure to the codebook (
edit ``codebook.yaml`` using an editor of your choice), viewing code stats 
after editing the codebook, 
and writing memos (``qc memo``) to document
emerging themes. We have found that in larger projects, the options to
scope queries to subsets of coders or subsets of the corpus become
increasingly useful. The query outputs shown above can also be formatted
as CSV or JSON for downstream processing, or as LaTeX, HTML, or many
other formats for inclusion in a publication.

Create a new project
--------------------

Setup
~~~~~

This section is a guide to starting a new ``qc`` project. Either save
the excerpt below as ``teacher_2.txt`` on your Desktop (another teacher 
interview from the project described in the previous section), or select 
one or more of your own documents to work with.
These could be in any text-based file format (the default
importer uses `Pandoc <https://pandoc.org/>`__, and so can handle any
file format supported by Pandoc.) 

.. code-block:: console

   Research_Assistant:         So just to start, it would be helpful to 
   understand what your background is in computer science and also with 
   Location 63.

   Person_121:    So, I worked for years in the tech industry before I decided
   to teach elementary school. I wasn't, so my background is engineering but not 
   computer science, though the work I was doing was programming. And so after 
   fifteen years in the tech industry, I lost my job, I went back to school, I 
   did my multiple subject credential, and I started teaching as an elementary 
   school teacher in Location 63.

   Person_121:    So I literally just started as a classroom teacher, nothing 
   else. I had no CS in mind at that time. And right about the time I started in 
   Year was around the time Location 63 was getting smart boards in the classroom, 
   one by one and I got to test that.  And then one thing led to another and I 
   noticed how students who otherwise may not be motivated learning were motivated 
   by the use of technology, so I got more into using technology with teaching to 
   engage the students and engage them as a result.

   Person_121:    During the course of that, I stumbled upon Scratch, and 
   you're probably familiar with Scratch, I'm not sure, but it's the language 
   developed at MIT Media Lab with children in mind. While I was still a fifth 
   grade classroom teacher, I stumbled upon that and I thought oh this is 
   fantastic and it'll be great to use with my classroom. So, I created a unit 
   that I started doing that spring, and every single child was not only super 
   engaged, but it was the creative aspect, the problem solving and the teamwork 
   that went with it and all of these other skills that I noticed that. And then 
   made learning more fun, of course. And they were learning a lot. So this was 
   like in, I don't know, many years ago and the only thing that existed at that 
   time was Scratch for children. And I think Scratch was probably usable at that 
   time, til maybe fourth grade, but that would also be pushing it a little, but 
   fifth was just sort of right.

Create a new directory on your filesystem. In this example, we will
initialize a new project in a directory called ``qc_project`` on the current 
user’s desktop, and intialize a new project.

.. code-block:: console

   % cd ~/Desktop
   % mkdir qc_project
   % cd qc_project
   % qc init

When ``qc init`` is run, a settings file (``settings.yaml`` by default)
is created with default values, and project assets are created in 
in the locations specified in the settings file. Running ``ls`` will show 
the contents of our project. (See :ref:`textfiles` for details.)

.. code-block:: console

   ~/Desktop/qc_project % ls
   codebook.yaml
   corpus
   memos
   qc.log
   qualitative_coding.sqlite3
   settings.yaml

Import documents
~~~~~~~~~~~~~~~~

Now let’s import the document. When you import a document,
``qc`` creates a plain-text formatted copy within ``corpus`` and adds
document metadata to the database. If you are going to import your own document, 
use its file path instead of ``~/Desktop/teacher_2.txt`` in the command below.
If you want to keep a text document’s existing formatting, use
``--importer verbatim`` to tell ``qc`` not to apply any formatting. 

.. code-block:: console

   $ qc corpus import ~/Desktop/teacher_2.txt

We can confirm that the document was imported by listing corpus
documents. 

.. code-block:: console

   % qc corpus list
   teacher_2.txt

Coding
~~~~~~

Now we will code the document.
What kind of codes should be used? This is a broad topic beyond the scope of this vignette; 
a well-designed qualitative research project should clearly articulate its methodological 
choices and ground them in a theoretical framework. For this example, we will be
a bit informal: we will use open coding (codes are not restricted to a predefined codebook)
with a mix of in vivo (using participants' words as codes) and in vitro (using the coder's 
interpretation as codes) coding, with an analytical focus guided by the codebook in the 
previous section. 

You will code your document using a text editor. Visual Studio Code is the default editor; 
see :ref:`editor` for other options. Run ``qc code user``, where ``user`` is
the username you want to use while coding. This will launch your editor with 
the document to be coded and ``codes.txt`` (containing any existing codes, otherwise empty) 
side-by-side as shown in Figure 1. Add codes to ``codes.txt`` on the line corresponding
to a line in the corpus document. Each code may be any combination of letters,
numbers, and underscores; when multiple codes are applied to a line,
separate them with a comma. Save your changes and close the editor to end the
coding session. ``qc`` will read ``codes.txt``, update the database 
with changes in coded lines, and then delete ``codes.txt``. 

.. note::

   If you are using Visual Studio Code, the document and the coding file will
   probably open in separate tabs. Split the view (View -> Editor Layout -> Split Right),
   drag them so they are side-by-side, and then enable the Scroll Sync extension 
   if installed, to keep the line numbers in each document aligned.

.. figure:: coding_vscode.png
   :alt: Figure 1. Screen shot of the coding interface using Visual Studio Code.

   Figure 1. Screen shot of the coding interface using Visual Studio Code.

Organizing the codebook
~~~~~~~~~~~~~~~~~~~~~~~

Now that you have finished coding, ``qc`` will have updated your codebook with all new codes. 
To continue the cycle of "notice things," "think about things," and "collect
things" (Seidel 1998, 2), let's see a summary of our coding. 

.. code-block:: console

   % qc codes stats

   Code                       Count
   -----------------------  -------
   creativity                     1
   developmental_fit              1
   elementary                     1
   engineering                    1
   i_had_no_cs_on_my_mind         1
   increased_motivation           1
   made_learning_fun              1
   problem_solving                1
   professional_experience        1
   scratch                        2
   smart_boards                   1
   stumbled_upon_tech             1
   teacher_agency                 1

A simple count of discrete codes might be just right for some projects, but 
if we want to start making sense of the coding it would help to organize the 
codebook, grouping similar codes together. To do this, edit the nested structure
of codes in ``codebook.yaml``. (Run ``code codebook.yaml`` to open the codebook in 
Visual Studio Code). Initially, the codebook is just a list of codes:

.. code-block:: yaml

   - creativity
   - developmental_fit
   - elementary
   - engineering
   - i_had_no_cs_on_my_mind
   - increased_motivation
   - made_learning_fun
   - problem_solving
   - professional_experience
   - scratch
   - smart_boards
   - stumbled_upon_tech
   - teacher_agency

Some of these codes belong together. For example, "scratch" and "smart_boards"
are both technologies. "creativity," "increased_motivation," "made_learning_fun,"
and "problem_solving" were all named as reasons for teaching computer science. 
(As with coding, different qualitative methodologies have different approaches to organizing
codes.) After grouping codes together, our codebook looks like this:

.. code-block:: yaml

   - reasons_for_teaching_cs:
     - creativity
     - increased_motivation
     - made_learning_fun
     - problem_solving
   - teacher_identity:
     - elementary
     - engineering
     - professional_experience
   - technologies:
     - scratch
     - smart_boards
   - trajectory:
     - developmental_fit
     - i_had_no_cs_on_my_mind
     - stumbled_upon_tech
     - teacher_agency

Now the stats are more meaningful, especially if we show codes in 
their nested structure (``--recursive-codes``, ``-r``) and the 
sum of each code and its children (``--recursive-counts``, ``-a``). 

.. code-block:: console

   % qc codes stats -ra
   Code                          Count    Total
   --------------------------  -------  -------
   reasons_for_teaching_cs           0        4
   .  creativity                     1        1
   .  increased_motivation           1        1
   .  made_learning_fun              1        1
   .  problem_solving                1        1
   teacher_identity                  0        3
   .  elementary                     1        1
   .  engineering                    1        1
   .  professional_experience        1        1
   technologies                      0        3
   .  scratch                        2        2
   .  smart_boards                   1        1
   trajectory                        0        4
   .  developmental_fit              1        1
   .  i_had_no_cs_on_my_mind         1        1
   .  stumbled_upon_tech             1        1
   .  teacher_agency                 1        1

Depending on the qualitative methodology being used, you might want to 
iterate between coding and organizing the codebook. After open
coding, we often have multiple codes with similar meanings. Sometimes we
choose to rename or merge codes to reduce the total number of distinct codes, but
more often we just group similar codes together as subcodes, and then
use the parent code in our analysis. 

Commands are provided for renaming and merging codes
(:ref:`codes_rename`), dele
coding scheme stabilizes 


Viewing coded text
~~~~~~~~~~~~~~~~~~

If you want to think about the meaning of a group of codes, it is helpful to 
see relevant excerpts from the document. Let's view excerpts which were coded
with "trajectory," using ``--recursive-codes`` or ``-r`` to also include its 
children.

.. code-block:: console

   % qc codes find trajectory -r
   
   teacher_2.txt (4)
   ================================================================================
   [9:14]
                                                                                    | 
   Person_121: So I literally just started as a classroom teacher, nothing else. I  | 
   had no CS in mind at that time. And right about the time I started in Year was   | i_had_no_cs_on_my_mind
   around the time Location 63 was getting smart boards in the classroom, one by    | 
   one and I got to test that. And then one thing led to another and I noticed how  | 
   
   [19:25]
   probably familiar with Scratch, I’m not sure, but it’s the language developed at | 
   MIT Media Lab with children in mind. While I was still a fifth grade classroom   | 
   teacher, I stumbled upon that and I thought oh this is fantastic and it’ll be    | stumbled_upon_tech
   great to use with my classroom. So, I created a unit that I started doing that   | teacher_agency
   spring, and every single child was not only super engaged, but it was the        | 
   creative aspect, the problem solving and the teamwork that went with it and all  | 
   
   [27:30]
   years ago and the only thing that existed at that time was Scratch for children. | 
   And I think Scratch was probably usable at that time, til maybe fourth grade,    | 
   but that would also be pushing it a little, but fifth was just sort of right.    | developmental_fit

Memoing
~~~~~~~

Often, looking at groups of codes together leads to conceptual insights worth documenting. 
``qc`` provides a simple integrated memoing function which uses your text editor to open 
a new file in your memos directory. 

.. code-block:: console

   % qc memo chris --message "How teachers get involved with CS"

.. figure:: memo.png
   :alt: Figure 3. A memo.

   Figure 3. A memo.

From here, you are ready to import more documents, continue coding,
refining the codebook, and
the iterative cycle of "notice things," "think about things,"
and "collect things" which characterizes QDA. Please feel free to
contact the authors for support, or to share your experience with
``qc``.

Autocoding
~~~~~~~~~~

As you accumulate hand-coded documents, ``qc`` can use them to train a
machine learning classifier that predicts codes for new documents. The
technical background is given in :ref:`autocode`; here we describe how
autocoding integrates into the coding workflow.

**Checking readiness.** Start by confirming that you have enough coded
examples per code to train useful classifiers. The ``autocode_min_examples``
setting (default: 5) is the required floor; 10–20 examples per code
gives meaningfully better classifiers in practice.

.. code-block:: console

   % qc codes stats --recursive-codes --recursive-counts --coders chris

   Code                       Count
   -----------------------  -------
   professional_experience       14
   cs_entry                      11
   increased_motivation           8
   scratch                        4

Codes with very few examples — like ``scratch`` here — may be skipped
during training. Continue hand-coding until you have enough examples for
the codes that matter most.

**Embedding the corpus.** Autocoding requires corpus documents to be
converted to numerical embeddings using a text embedding API. This is a
one-time cost; results are cached on disk and reused until the documents
change. The embedding API is configured in ``settings.yaml`` via
``autocode_api_base``, ``autocode_api_model``, and ``autocode_api_key``;
``qc``\ 's defaults use a locally-running model (e.g. via
`LM Studio <https://lmstudio.ai>`__ or `Ollama <https://ollama.com>`__),
which keeps all data on your machine.

.. code-block:: console

   % qc autocode embed
   Embedding corpus... ████████████████ 40/40 documents

**Cross-validation.** Before writing any predictions to the database,
use ``qc codes agreement --metric cv`` to estimate per-code classifier
quality via k-fold cross-validation. No predictions are written at this
step.

.. code-block:: console

   % qc codes agreement -c chris --metric cv

   Code                      Examples    Precision    Recall      F1
   ----------------------  ----------  -----------  --------  ------
   professional_experience         14         0.82      0.78    0.80
   cs_entry                        11         0.71      0.65    0.68
   increased_motivation             8         0.60      0.55    0.57
   scratch                          4        (skipped — too few examples)

Codes with low F1 scores or with too few examples need more hand-coded
examples before autocoding will be reliable. Continue coding and re-run
until you are satisfied.

**Bulk applying predictions.** Apply the trained classifiers to documents
not yet coded by any human coder. The ``--auto --no-edit`` flags write
predictions directly to the database under a separate coder name (here,
``auto.v1``), so they can be inspected or discarded independently of your
hand-coding.

.. code-block:: console

   % qc code auto.v1 --auto --no-edit -c chris
   Wrote 1,240 predictions across 22 codes for 30 documents.

Because autocode predictions are stored under a named coder, all existing
``qc codes`` commands work with them normally. To inspect predictions:

.. code-block:: console

   % qc codes stats --coders auto.v1
   % qc codes find cs_entry --coders auto.v1

To discard a round of predictions entirely and start over:

.. code-block:: console

   % qc coders delete auto.v1

**Interactive active learning.** The classifier knows which lines it is
most uncertain about. The ``qc autocode`` command uses that uncertainty
to direct your coding effort where it is most valuable. Its invocation is
analogous to ``qc code CODER``:

.. code-block:: console

   % qc autocode human.v2 --train-coders chris auto.v1

``qc`` shows the most uncertain line in context, along with ranked
candidate codes and confidence scores:

.. code-block:: console

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

   Enter codes (comma-separated), or press Enter to skip:

After each response, the model retrains and moves to the next most
uncertain line. Press Ctrl-C or type ``quit`` to end the session at any
point; all annotations are saved immediately to the database.

**Evaluating predictions.** To assess how well autocode predictions agree
with a human coder, use ``qc codes agreement --metric f1``. The first
``-c`` coder is treated as ground truth:

.. code-block:: console

   % qc codes agreement -c chris auto.v1 --metric f1

   Code                      Precision    Recall      F1
   ----------------------  -----------  --------  ------
   professional_experience        0.85      0.80    0.82
   cs_entry                       0.76      0.70    0.73
   increased_motivation           0.65      0.61    0.63

Advanced patterns
-----------------

Collaboration in heterogeneous groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Preferences and comfort levels with tools often varies across research teams, 
and requiring the use of specific tools can be a source of inequitable gate-keeping.
We have successfully used ``qc`` in several research collaborations 
where some team members preferred to code in a shared spreadsheet. 
By importing members' coding into ``qc``, 
we have been able to access the full power of ``qc``, while allowing everyone
to use a tool that is comfortable.

Here is one simple workflow: copy a corpus document into a shared spreadsheet, 
and then create a column for each coder, as shown in Figure 2.
When you are ready to transfer codes into ``qc``, open the document for 
coding (e.g. ``qc code chris``), and replace the entire contents of 
``codes.txt`` with the appropriate column from the spreadsheet. Save and close
the editor. 

.. figure:: coding_google_docs.png
   :alt: Figure 2. An online spreadsheet ready for coding.

   Figure 2. An online spreadsheet ready for coding.

Automated coding
~~~~~~~~~~~~~~~~

You could automatically apply codes to a document by writing a script and
defining it as an editor (see :ref:`editor`); the script would receive the
path to a corpus file and the codes file, and would write codes into the codes
file. For example, when we were analyzing student-written computer programs, we combined
manual qualitative coding with automated static analysis of the programs,
which added codes marking syntactic structures and manipulation of variables.
This allowed us to integrate what students were doing (via our qualitative coding)
with how they were doing it (via static analysis).

``qc`` also supports machine-learning-assisted coding through the ``autocode``
command group, described in :ref:`autocode` and demonstrated in the Vignette. Unlike
approaches that send documents to LLMs with a prompt, ``qc``\ 's autocode system trains
on the researcher's own prior coding using word embeddings and support vector machines,
keeping the researcher's analytical judgment at the center of the process.

Multiple codebooks
~~~~~~~~~~~~~~~~~~

Much of ``qc``\ ’s power comes from the ability to quickly and easily
iterate the structure of the codebook, and then to see the results
through flexible and powerful queries which use the codebook. Sometimes
it even makes sense to maintain multiple codebooks. For example, after a large
and messy initial round of coding, we often want to significantly refactor
the codebook, merging and deleting codes, and organizing them according 
to the constructs we have decided to focus on. We prefer to do this refactoring
in new codebooks so that it is easy to explore multiple alternatives. 
We also use multiple codebooks when we are re-coding an existing corpus for a
new analysis focused on different constructs.

The easiest way to work with multiple codebooks is to have multiple settings
files, each specifying a different codebook. Then specify the desired settings
file when running ``qc`` commands. See :ref:`settings` for details.

Alternatively, if the project is
stored in a version control system such as git (highly recommended),
changes to the codebook can be maintained in separate branches of the
repository.

Package documentation
=====================

All ``qc`` commands are described below with their most common options.
Use ``--help`` for a full and up-to-date list of available options for each command.

General commands
----------------

.. _init: 

init
~~~~

Initializes a new coding project. If the settings file is not present,
writes the settings file with default values and then initializes project
assets (e.g. the corpus directory, the codebook, the database, the log file)
as specified in the settings file.

If you wish to edit the settings file before creating project assets (e.g. 
to specify a different location for the corpus directory), use the 
``--write-settings-file`` (``-w``) flag. This will write the settings file and 
then stop. Make any desired edits, and then run ``qc init`` again.

It is safe to re-run ``qc init``.

.. code-block:: console

   % qc init

check
~~~~~

Checks that all required files and directories are in place.

.. code-block:: console

   % qc check

code
~~~~

Opens your text editor with a corpus file and a temporary coding file.
The name of the coder is a required positional argument. After optionally
filtering the corpus using common options
(below), select a document with no existing codes (for this coder) using
``--first`` (``-1``) or ``--random`` (``-r``). Otherwise, you will be
presented with a list of corpus files and asked to choose which to code.

.. code-block:: console

   % qc code chris -1

Save and close your editor when you finish. In the unlikely event that
your editor crashes or your battery dies before you finish coding, your
saved changes are persisted in ``codes.txt``. Run ``qc code <coder> --recover``
to resume the coding session, or ``qc code <coder> --abandon`` to delete
the coding session.

**Automated coding.** Adding ``--auto`` uses trained classifiers (see
:ref:`autocode`) to pre-populate the coding file with predictions before
the editor opens, so the researcher reviews and corrects rather than
coding from scratch. Use ``-c TRAIN_CODERS`` to specify which coder(s)
provide training data; embeddings must already be generated (see
``qc autocode embed``).

.. code-block:: console

   % qc code auto -1 --auto -c chris

Adding ``--no-edit`` writes predictions directly to the database without
opening an editor. This is the bulk prediction mode: predictions are
applied to all corpus documents not already coded by any human coder, and
the coding is saved under the given coder name. Use ``--threshold`` to
override the confidence threshold from settings, and ``--no-hierarchy``
to disable tree-descent post-processing.

.. code-block:: console

   % qc code auto.v1 --auto --no-edit -c chris

codebook (cb)
~~~~~~~~~~~~~

Ensures that all codes in the project are included in the codebook. (New
codes are added automatically, but if you accidentally delete some while
editing the codebook, ``qc codebook`` will ensure they are all present.)

.. code-block:: console

   % qc codebook

coders
~~~~~~

List all coders in the current project.

.. code-block:: console

   % qc coders

coders delete
~~~~~~~~~~~~~

Delete all coded lines for the named coder and remove the coder record.
This is the primary mechanism for reverting autocode predictions cleanly:

.. code-block:: console

   % qc coders delete auto.v1

memo
~~~~

Opens your editor to write a memo, optionally passing ``--message``
(``-m``) as the title of the memo. Use ``--list`` (``-l``) to list all
memos.

.. code-block:: console

   % qc memo chris -m "It's all starting to make sense..."

export
~~~~~~

Export the current project in ``.qpdx`` format. See :ref:`interop`.

upgrade
~~~~~~~

Upgrade a ``qc`` project from a prior version of ``qc``.
Upgrade (or downgrade) to a specific version using ``--version`` (``-v``).

.. code-block:: console

   % qc upgrade

version
~~~~~~~

Show the current version of ``qc``. This project uses `semantic
versioning <https://semver.org/>`__.

.. code-block:: console

   % qc version
   qualitative-coding 1.4.0

Corpus commands
---------------

The following commands are grouped under ``qc corpus``.

corpus list (ls)
~~~~~~~~~~~~~~~~

List all files in the corpus.

.. code-block:: console

   % qc corpus list

corpus import
~~~~~~~~~~~~~

Import files into the corpus, copying source files into ``corpus``,
formatting them (see options), and registering them in the database.
Individual files can be imported, or directories can be recursively
imported using ``--recursive`` (``-r``).

.. code-block:: console

   % qc corpus import transcripts --recursive

If you want to import files into a specific subdirectory within the
``corpus``, use ``--corpus-root`` (``-c``). For example, if you wanted
to import an additional transcript after importing the transcripts
directory, you could run:

.. code-block:: console

   % qc corpus import follow_up.txt --corpus-root transcripts

Several importers are available to format files, and can be specified
using ``--importer`` (``-i``). The default importer, ``pandoc``, uses
`Pandoc <https://pandoc.org/>`__ to convert files into plain-text, and
then hard-wrap them at 80 characters. ``vtt`` imports VTT files 
(a closed-caption format produced by Zoom and other services which 
transcribe audio), stripping away the timestamps and collapsing adjacent
captions with the same speaker. ``verbatim`` imports text files without 
making any changes. Future importers will include text
extraction from PDFs and automatic transcription of audio files.

corpus move (mv)
~~~~~~~~~~~~~~~~

Move a document from one corpus path to another, or recursively move a
directory with ``--recursive`` (``-r``). Do not move corpus files
directly or they will become out of sync with their metadata in the
database.

.. code-block:: console

   % qc corpus move corpus/interview.txt corpus/pre/annabelle.txt

corpus remove (rm)
~~~~~~~~~~~~~~~~~~

Remove a document from the corpus, along with codes applied to the
document. Or recursively remove all documents in a directory with
``--recursive`` (``-r``).

.. code-block:: console

   % qc corpus remove corpus/pre/annabelle.txt

corpus update
~~~~~~~~~~~~~

Update a document in the corpus. When a document changes, ``qc`` 
needs to update the positions of all existing coded lines, which requires
access to the old version and the updated version. Documents
can be updated using two strategies. First, provide a new version 
of the document, stored outside of the corpus:

.. code-block:: console

   % qc corpus update corpus/interview.txt --new revised_interview.txt

If your project is stored in a git repository (highly recommended), 
you can also edit the document directly; the committed verison of the document
is considered the old version.

.. code-block:: console

   % qc corpus update corpus/interview.txt

Use ``--dryrun`` (``-d``) to show a diff of the changes without updating the 
corpus.

corpus anonymize
~~~~~~~~~~~~~~~~

.. note::

   This command requires installing the optional language model. See 
   :ref:`installation`.

Anonymize corpus documents. Documents containing personally-identifiable
information (PII) frequently need to have this imformation removed in order to 
protect the privacy of research participants. This can be automated using
Named Entity Recognition (although it is not perfect; make sure you check 
for PII). It is often good practice to remove PII from documents as early 
in the analysis process as possible.

First, generate a key file mapping named entities (e.g. people, places, 
organizations) to placeholders.

.. code-block:: console
    
   % qc corpus anonymize

The key file is called ``key.yaml`` by default; choose another name with 
``--key`` (``-k``) when necessary. Now edit the key file. All terms appearing
in the key file will be substituted for their placeholders, so delete any 
terms which you want to preserve. Often the same person is referred to in 
different ways; it's fine to assign the same placeholder to several terms.
For example: 

.. code-block:: yaml

   Chris Proctor: Person_1
   Dr. Proctor: Person_1
   Chris: Person_1

If you later reverse the anonymization, placeholders will be replaced with
the first matching term. So "Person_1" will be replaced with "Chris Proctor."

Once the key file is ready, create anonymized copies of corpus documents:

.. code-block:: console
    
   % qc corpus anonymize

This time, the key file already exists, so anonymized copies of the corpus are
created in ``anonymized`` (specify another directory with ``--out-dir`` (``-o``)). 
If you want to update the corpus with the anonymized versions, use
``--update`` (``-u``).  At this point, you could move the key 
file to another computer to protect the PII. 
If you later wish to de-anonymize the corpus, move the key file back into 
the project and run:

.. code-block:: console
    
   % qc corpus anonymize --reverse

Codes commands
--------------

The following commands are grouped under ``qc codes``.

codes list (ls)
~~~~~~~~~~~~~~~

Lists all the codes currently in the codebook.

.. code-block:: console

   % qc codes list --expanded

.. _codes_rename: 

codes rename
~~~~~~~~~~~~

Goes through all the code files and replaces one or more codes with
another. Removes the old codes from the codebook.

.. code-block:: console

   % qc codes rename humorous funy funnny funny

codes find
~~~~~~~~~~

Displays all occurences of the provided code(s).

.. code-block:: console

   % qc codes find math science art

codes stats
~~~~~~~~~~~

Displays frequency of usage for each code. Note that counts include all
usages of children. List code names to show only certain codes. In
addition to the common options below, code results can be filtered with
``--max``, and ``--min``.

.. code-block:: console

   % qc codes stats --recursive-codes --depth 2

Use ``--by-coder`` (``-C``) for separate columns for each coder, and
``--by-document`` for separate columns for each document. When
``--by-coder`` and ``--by-document`` are given, displays a pivot table
of code counts by document and coder. (Optionally filter coders using
``--coders`` (``-c``) and filter documents using the options listed
below in “Filter the corpus.”)

codes crosstab (ct)
~~~~~~~~~~~~~~~~~~~

Displays a cross-tabulation of code co-occurrence within the unit of
analysis, as counts or as probabilities (``--probs``, ``-0``).
Optionally use a compact (``--compact``, ``-z``) output format to
display more columns.

.. code-block:: console

   % qc codes crosstab planning implementation evaluation --recursive-codes --depth 1 --probs

codes agreement
~~~~~~~~~~~~~~~

Computes inter-rater agreement or classifier quality across all selected
codes. The ``--metric`` option selects the measure; ``-c`` specifies the
coders to include.

- ``--metric alpha`` (default): Krippendorff's Alpha. Handles multiple
  coders and missing data; the current methodological recommendation for
  reporting IRR in qualitative research.
- ``--metric kappa``: Cohen's Kappa. Pairwise, chance-corrected
  agreement; requires exactly two coders.
- ``--metric f1``: Precision, Recall, and F1. Appropriate when one coder
  is treated as ground truth (e.g. evaluating autocode predictions
  against a human coder). Requires exactly two coders; the first ``-c``
  coder is treated as ground truth.
- ``--metric cv``: K-fold cross-validation (``--folds N``, default 5).
  Trains a classifier on each fold and reports estimated Precision,
  Recall, and F1. Requires embeddings (see ``qc autocode embed``). Used
  to assess classifier quality *before* writing any predictions.

.. code-block:: console

   % qc codes agreement -c chris anna --metric alpha
   % qc codes agreement -c chris auto.v1 --metric f1
   % qc codes agreement -c chris --metric cv --folds 5

Each corpus line is treated as a binary judgment unit (coded / not coded
with this code) for each rater. Output follows the standard tabulate
format and respects ``--format``, ``--outfile``, and all common corpus
filter options.

Autocode commands
-----------------

The following commands are grouped under ``qc autocode`` (alias: ``qc ac``).
They require embeddings to have been generated first with ``qc autocode embed``.
See :ref:`autocode` for a technical overview and the Vignette for a
worked example.

autocode embed
~~~~~~~~~~~~~~

Embed all corpus documents using the configured embedding API. Skips
documents whose embedding cache is already valid; use ``--force`` to
re-embed everything. Accepts the standard ``--pattern`` and
``--filenames`` corpus filter options.

.. code-block:: console

   % qc autocode embed
   % qc autocode embed --force -p round2

autocode describe
~~~~~~~~~~~~~~~~~

Show a description of the classifier that would be trained given the
current settings and coded data — without actually training it. Displays
all autocode hyperparameters from ``settings.yaml`` and a per-code
summary (positive example count, training status). Use this to document
the configuration before or after a batch of predictions.

.. code-block:: console

   % qc autocode describe -c chris --recursive-codes

autocode CODER
~~~~~~~~~~~~~~

Interactive active learning loop. Analogous to ``qc code CODER``, but
``qc`` selects lines to show based on classifier uncertainty rather than
document order. Use ``--train-coders`` to specify which coders' coding
trains the classifier.

.. code-block:: console

   % qc autocode human.v2 --train-coders chris auto.v1

For each iteration, ``qc`` displays the most uncertain line in context
along with ranked candidate codes and confidence scores, then prompts for
codes. After each response, the classifier retrains and selects the next
most uncertain line. Press Ctrl-C or type ``quit`` to end the session;
all annotations are saved immediately. Use ``--context N`` to control
how many surrounding lines are shown (default: 3), and
``--uncertainty-threshold`` to set the confidence floor below which lines
are still presented.

autocode outliers
~~~~~~~~~~~~~~~~~

For each code, identify coded lines whose embeddings are farthest from
the centroid of that code's training examples — likely miscodes or edge
cases worth reviewing. Use ``-n N`` to control how many outliers are
reported per code.

.. code-block:: console

   % qc autocode outliers -c chris --recursive-codes -n 5

autocode density
~~~~~~~~~~~~~~~~

Report per-code cohesion as mean pairwise cosine distance among coded
lines' embeddings. A small mean distance indicates a tight, well-defined
code; a large distance suggests a vague or over-broad code that may
benefit from splitting.

.. code-block:: console

   % qc autocode density -c chris

autocode similar
~~~~~~~~~~~~~~~~

Find pairs of codes whose centroids are close in embedding space —
candidates for merging. Use ``--threshold FLOAT`` to control the
similarity cutoff (default: 0.9).

.. code-block:: console

   % qc autocode similar -c chris --threshold 0.85

Common options
--------------

Specify the settings file
~~~~~~~~~~~~~~~~~~~~~~~~~

Every ``qc`` command supports ``--settings`` (``-s``), which allows you
to specify a settings file. This makes it possible to run ``qc``
commands from outside the project directory or from within scripts
without ambiguity. Sometimes it is also helpful to keep multiple
settings files in a project, for example when different coders prefer
different editors, or if you wish to keep multiple versions of the
codebook with different code trees.

The settings file can also be specified via the ``QC_SETTINGS``
environment variable. This makes it easy to check multiple settings
files into version control (e.g. for users with different preferences,
or to try out different codebook structures) while still using the 
intended settings file without needing to specify it. 

Filter the corpus
~~~~~~~~~~~~~~~~~

Commands which operate on or iterate over the corpus have options to
filter which documents are included.

-  ``--pattern [pattern]`` (``-p``): Only include corpus files and their
   codes which match ``pattern`` as a substring of the document path.
-  ``--filenames [filepath]`` (``-f``): Only include corpus files listed
   in ``filepath`` (one per line).

Filter code selection
~~~~~~~~~~~~~~~~~~~~~

-  ``code`` [codes]: Many commands have an optional positional argument
   in which you may list codes to consider. If none are given, the root
   node in the tree of codes is assumed.
-  ``--coder`` ``coder`` (``-c``): Only include codes entered by
   ``coder`` (if you use different names for different rounds of coding,
   you can also use this to filter by round of coding).
-  ``--recursive-codes`` (``-r``): Include children of selected codes.
-  ``--depth`` ``depth`` (``-d``): Limit the recursive depth of codes to
   select.
-  ``--unit`` ``unit`` (``-n``): Unit of analysis for reporting.
   Currently “line”, “paragraph”, and “document” are supported.
   Paragraphs are delimited by blank lines. When ``--unit`` is not
   supplied on the command line, the value of the ``unit`` key in
   ``settings.yaml`` is used (default: ``line``). Setting ``unit``
   in ``settings.yaml`` also controls how embeddings are generated
   for autocode (see :ref:`autocode`).
-  ``--recursive-counts`` (``-a``): When counting codes, also count
   instances of codes’ children. In contrast to ``--recursive-codes``,
   which controls which codes will be reported, this option controls how
   the counting is done.

Output and formatting
~~~~~~~~~~~~~~~~~~~~~

-  ``--format`` ``format`` (``-m``): Formatting style for output table.
   Supported values include “html”, “latex”, “github”, and `many
   more <https://pypi.org/project/tabulate/>`__.
-  ``--expanded`` (``-e``): Show names of codes in expanded form (e.g. 
   “coding_process:grounded”)
-  ``--outfile`` ``outfile`` (``-o``): Save tabular results to a csv
   file instead of displaying them to the screen. This is particularly
   useful in scripts.

 .. _settings: 

Settings
--------
The behavior of ``qc`` can be configured using your settings file, 
which by default is ``settings.yaml``. New projects are created with 
sensible defaults. The following settings are available:

qc_version
~~~~~~~~~~
The version of ``qc`` you are using. Do not change this; use ``qc upgrade`` if 
you need to upgrade to a new version of ``qc``.

corpus_dir
~~~~~~~~~~
The location of your corpus. Default: ``corpus``.

database
~~~~~~~~
The path to your ``qc`` database file. Default: ``qualitative_coding.sqlite3``.

memos_dir
~~~~~~~~~
The path to memos created with ``qc memo``. Default: ``memos``.

codebook
~~~~~~~~
The path to the codebook file. Default: ``codebook.yaml``.

.. _editor: 

editor
~~~~~~
Name of the code editor. Default: ``code`` (Visual Studio Code). The following editors are 
supported:

* ``code``
* ``vim``
* ``nvim``
* ``emacs``

Additional editors can be specified in an optional ``editors`` setting, as shown below.
Specify a terminal command which should be invoked for coding a document (using 
placeholders for ``{corpus_file_path}`` and ``{codes_file_path}``). Additionally, specify
a terminal command which should be invoked for writing memos, using a placeholder
for ``{memo_file_path}``. 

For example, if you wanted to use `Sublime Text <https://www.sublimetext.com/>`__, 
you would need to make sure Sublime Text can be called from the terminal
(`instructions <https://www.sublimetext.com/docs/command_line.html>`__), and then use 
the following configuration in ``settings.yaml``: 

.. code-block:: yaml

   editor: sublime
   editors: 
     sublime:
       name: Sublime Text
       code_command: 'subl "{corpus_file_path}" "{codes_file_path}" --command "new_pane" --wait'
       memo_command: 'subl "{memo_file_path}" --wait'

Additional examples are available in ``qc``'s `built-in editor support <https://github.com/cproctor/qualitative-coding/blob/main/qualitative_coding/editors.py>`__. 

During coding, ``qc`` creates a temporary codes file with the same number of lines 
as the corpus document and existing codes on the appropriate lines. 
The coder should update and save the codes file. When the code command successfully 
terminates, ``qc`` reads the codes file, updates the codes in the project database, and 
then deletes the temporary codes file and the metadata file. 

log_file
~~~~~~~~
Path of the log file. Default: ``qc.log``.

verbose
~~~~~~~
When set to ``true``, human-readable logs will be printed to the screen after each command,
providing more detail about commands. Default: ``false``.

unit
~~~~
Unit of analysis for reporting commands (``qc codes stats``, ``qc codes find``,
``qc codes crosstab``) and for generating embeddings. Supported values: ``line``
(default), ``paragraph`` (blank-line delimited), ``document``. Individual commands
can override this via ``--unit`` (``-n``); when the flag is omitted, this setting
is used.

Autocode settings
~~~~~~~~~~~~~~~~~

The following settings configure the ``qc autocode`` command group. All have
sensible defaults; most projects only need to set the embedding API connection.

``autocode_embeddings_dir``
  Directory for cached embeddings. Default: ``embeddings``. Add this directory
  to ``.gitignore`` — embeddings can be large and are reproducibly regenerated
  from the corpus.

``autocode_window``
  List of ``[lines_before, lines_after]`` included in each line's embedding
  text. Larger windows give classifiers more context; smaller windows are
  faster. Default: ``[2, 2]``. Only relevant when ``unit: line``.

``autocode_min_examples``
  Minimum number of positive examples required to train a classifier for a
  code. Codes with fewer examples are skipped. Default: ``5``.

``autocode_confidence_threshold``
  Minimum classifier confidence required to write a prediction. Default:
  ``0.6``.

``autocode_child_threshold``
  When walking the code tree, minimum confidence required to prefer a child
  code over its parent. Default: ``0.4``.

``autocode_api_base``
  Base URL for the OpenAI-compatible embedding API. Default:
  ``http://localhost:1234/v1``. Set to ``https://api.openai.com/v1`` for
  OpenAI, or use any compatible local server (LM Studio, Ollama).

``autocode_api_key``
  API key for the embedding service. Default: empty string (suitable for local
  servers). Can alternatively be set via the ``QC_AUTOCODE_API_KEY``
  environment variable.

``autocode_api_model``
  Name of the embedding model on the configured server. Default:
  ``text-embedding-nomic-embed-text-v1.5``.

Logging
-------

``qc`` uses `structlog <https://www.structlog.org>`__, and emits JSON-formatted logs 
to support later analysis (e.g. for research on qualitative data analysis practices) 
or to document the coding process. Custom structlog configuration may be stored in 
``log_config.py``, allowing ``qc``'s logs to be integrated into a project's logs or 
sent to a central logging server.

.. _interop:

Interoperability with other QDA software
----------------------------------------

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
package is obliged to implement the full specification. ``qc``\ ’s user
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

Contributing
============

.. image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg 
   :alt: Contributor Covenant 2.1 badge
   :target: https://www.contributor-covenant.org/

Development of ``qc`` follows the Contributor Covenant. 
Chris Proctor (chrisp@buffalo.edu), the project lead, would be delighted to hear 
about your experience using ``qc``.
Bug reports, feature requests, and discussion of the future directions of 
``qc`` takes place on the project repository's
`issues page <https://github.com/cproctor/qualitative-coding/issues>`__. 
Code contributions to this project should be via pull requests on this repository. 

If you are considering using ``qc`` in a research project or need help, you are
also welcome to contact Chris directly via email. 

Acknowledgements
================

Partial support for development of ``qc`` was provided by UB's Digital Studio Scholarship
Network. Logo design by Blessed Mhungu. 

References
==========

.. container:: references csl-bib-body hanging-indent
   :name: refs

   .. container:: csl-entry
      :name: ref-denzin2011

      Denzin, Norman K, and Yvonna S Lincoln. 2011. *The Sage Handbook
      of Qualitative Research*. sage.

   .. container:: csl-entry
      :name: ref-engelbart1962

      Engelbart, Douglas C. 1962. “Augmenting Human Intellect: A
      Conceptual Framework,” 64–90.

   .. container:: csl-entry
      :name: ref-healy2020

      Healy, Kieran. 2020. “The Plain Person’s Guide to Plain Text
      Social Science.”

   .. container:: csl-entry
      :name: ref-jackson2018

      Jackson, Kristi, Trena Paulus, and Nicholas Woolf. 2018. “The
      Walking Dead Genealogy: Unsubstantiated Criticisms of Qualitative
      Data Analysis Software (QDAS) and the Failure to Put Them to
      Rest.” *The Qualitative Report*, March.
      https://doi.org/10.46743/2160-3715/2018.3096.

   .. container:: csl-entry
      :name: ref-mcilroy1978

      McIlroy, Doug, E PInson, and B Tague. 1978. “UNIX Time-Sharing
      System.” *The Bell System Technical Journal*, 1902–3.

   .. container:: csl-entry
      :name: ref-proctor2019

      Proctor, Chris, Maxwell Bigman, and Paulo Blikstein. 2019.
      “Defining and Designing Computer Science Education in a K12 Public
      School District.” In *Proceedings of the 50th ACM Technical
      Symposium on Computer Science Education*, 314–20. SIGCSE ’19. New
      York, NY, USA: Association for Computing Machinery.
      https://doi.org/10.1145/3287324.3287440.

   .. container:: csl-entry
      :name: ref-seidel1998qualitative

      Seidel, John V. 1998. “Qualitative Data Analysis.”

   .. container:: csl-entry
      :name: ref-spolsky2002

      Spolsky, Joel. 2002. “The Law of Leaky Abstractions.” *Joel on
      Software*.

   .. container:: csl-entry
      :name: ref-vanblommestein2019

      van Blommestein, Fred. 2019. “REFI-QDA: Exchange of Processed Data
      Between Qualitative Data Analysis Software Packages.”

   .. container:: csl-entry
      :name: ref-wickham2023

      Wickham, Hadley, and Jennifer Bryan. 2023. *R Packages*. "
      O’Reilly Media, Inc.".

   .. container:: csl-entry
      :name: ref-wing2011research

      Wing, Jeanette. 2011. “Research Notebook: Computational
      Thinking—What and Why.” *The Link Magazine* 6: 20–23.
