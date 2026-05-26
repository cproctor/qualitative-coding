Documentation
=============

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

Export the current project in ``.qpdx`` format. See :ref:`interop` in Background.

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

For each code, identify the coded lines that the trained classifier
assigns lowest confidence — these lie nearest the decision boundary and
are likely miscodes or edge cases worth reviewing. Use ``-n N`` to
control how many outliers are reported per code.

.. code-block:: console

   % qc autocode outliers -c chris --recursive-codes -n 5

autocode cohesion
~~~~~~~~~~~~~~~~~

Report per-code semantic cohesion as the fraction of embedding variance
explained by the first principal component. A high value indicates a
tight, well-defined code whose examples cluster in one semantic
direction; a low value suggests the code covers disparate concepts and
may benefit from splitting.

.. code-block:: console

   % qc autocode cohesion -c chris

autocode similar
~~~~~~~~~~~~~~~~

Find pairs of codes whose trained classifiers generalize to each other's
positive examples. For each pair, reports mean P(B | A's examples) and
mean P(A | B's examples). High scores in both directions suggest merge
candidates; asymmetric scores suggest a subset relationship. Use
``--threshold FLOAT`` to control the minimum score to report (default:
0.5).

.. code-block:: console

   % qc autocode similar -c chris --threshold 0.7

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
