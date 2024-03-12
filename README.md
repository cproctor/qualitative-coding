# Qualitative Coding

Qualitative coding for computer scientists. 

Qualitative coding is a form of feature extraction in which text (or images,
video, etc.) is tagged with features of interest. Sometimes the codebook is
defined ahead of time, other times it emerges through multiple rounds of coding.
For more on how and why to use qualitative coding, see Emerson, Fretz, and
Shaw's *Writing Ethnographic Fieldnotes* or Shaffer's *Quantitative
Ethnography*.

Most of the tools available for qualitative coding and subsequent analysis were
designed for non-programmers. They are GUI-based, proprietary, and don't expose 
the data in well-structured ways. Concepts from computer science, such as trees,
sorting, and filtering, could also be applied to qualitative coding analysis if
the interface supported it. Furthermore, a command-line based tool can be
combined with other utilities into flexible pipelines. 

Qualitative Coding, or `qc`, was designed to address these issues. I have used
`qc` as a primary coding tool in a [SIGCSE
paper](https://chrisproctor.net/research/proctor_2019_defining/) on
packaging and releasing a stable version was my own dissertation work. 
`qc` is in active use on forthcoming publications and receives regular updates
as we need new features. 

## Limitations

- Due to its nature as a command-line program, `qc` is only well-suited to coding textual data. 
- `qc` uses line numbers as a fundamental unit. Therefore, it requires text files in your corpus to be 
  hard-wrapped at 80 characters. The `corpus import` task can handle this for you. 
- Coding is done in a two-column view in a variety of supported editors, including
  Visual Studio Code, vim, and emacs. If you are not used to using a text editor, 
  or if you prefer a more graphical coding experience, `qc` might not be the best option.

# Installation

    pip install qualitative-coding

# Setup 

Choose a working directory for your project. Run `qc init -y`. This will create 
`settings.yaml` with the default settings, and set up the required files 
and directories for you. (Visual Studio Code is the default editor.) 

# Usage

## Workflow

`qc` is designed to give you a powerful terminal-based interface. The general
workflow is to use `code` to apply qualitative codes to your text files. As you
go, you will start to have ideas about the meanings and organization of your
codes. Use `memo` to capture these. 

Once you finish a round of coding, it's time to reorganize your codes. Edit 
`codebook.yaml`, grouping the flat list of codes into a hierarchy.
Use `codes stats` to see the distribution of your codes. 
Use `codes rename` if you want to rename existing codes.

After you finish coding, you may want to use your codes for analysis. Tools 
are provided for viewing statistics, cross-tabulation, and examples of codes, 
with many options for selecting and filtering at various units of analysis. 
Results can be exported to CSV for downstream analysis.

The `--coder` argument supports keeping track of multiple coders on a project,
and there are options to filter on coder where relevant. More analytical tools, 
such as inter-rater reliability, are coming. 

## Tutorial

Create a new directory somewhere. We will create a virtual environment, intstall
`qc`, and download some sample text from Wikipedia. 

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install qualitative-coding
    $ qc init -y
    $ curl -o what_is_coding.txt "https://en.wikipedia.org/w/index.php?title=Coding_%28social_sciences%29&action=raw"
    $ qc corpus import what_is_coding.txt

Now we're ready to start coding. This next command will open a split-window session in 
your editor of choice; add comma-separated codes to the blank file on the right. 
Once you've added some codes, we can analyze and refine them.

    $ qc code chris
    $ qc codebook
    $ qc codes list
    - a_priori
    - analysis
    - coding_process
    - computers
    - errors
    - grounded_coding
    - themes

Now that we have coded our corpus (consisting of a single document), we should
think about whether these codes have any structure. Re-organize some of your
codes in `codebook.yaml`. When you finish, run `codebook` again. It will go
through your corpus and add any missing codes. 

    $ qc codes list
    - analysis
    - coding_process
        - a_priori
        - grounded_coding
    - computers
    - errors
    - themes

I decided to group a priori coding and grounded coding together under coding
process. Let's see some statistics on the codes:

    $ qc codes stats
    Code                  Count
    ------------------  -------
    analysis                  2
    coding_process            7
    .  a_priori               2
    .  grounded_coding        2
    computers                 2
    errors                    1
    themes                    2

`stats` has lots of useful filtering and formatting options. For example, `qc
codes stats --pattern wiki --depth 1 --min 10 --format latex` would only consider files
having "wiki" in the filename. Within these files, it would show only
top-level categories of codes having at least ten instances, and would output a
table suitable for inclusion in a LaTeX document. Use `--help` on any command to
see available options.

Next, we might want to see examples of what we have coded. 

    $ qc codes find analysis
    Showing results for codes:  analysis
    
    what_is_coding.txt (2)
    ================================================================================
    
    [0:3]
    In the [[social science|social sciences]], '''coding''' is an analytical process | analysis
    in which data, in both [[quantitative research|quantitative]] form (such as      | 
    [[questionnaire]]s results) or [[qualitative research|qualitative]] form (such   | 
    
    [52:57]
    process of selecting core thematic categories present in several documents to    | 
    discover common patterns and relations.<ref>Grbich, Carol. (2013). "Qualitative  | 
    Data Analysis" (2nd ed.). The Flinders University of South Australia: SAGE       | analysis
    Publications Ltd.</ref>                                                          | 
                                                                                     | 

Again, there are lots of options for filtering and viewing your coding. At some
point, you will probably want to revise your codes. You can easily rename a
code, or collapse codes together, with the `rename` command. This updates your 
codebook as well as in all your code files.

    $ qc codes rename grounded_coding grounded

At this point, you are starting to realize some of the deeper themes running
through your corpus. Capturing these in an "integrative memo" is an important
part of qualitative coding. `memo` will open a preformatted document for you in vim. 

    $ qc memo chris --message "Thoughts on coding process"

Congratulations! You have finished the first round of coding. Before you move
on, this would be an excellent time to check your files into version control.
I hope you find `qc` to be powerful and efficient; it's worked for me!

-Chris Proctor

## Commands

Use `--help` for a full list of available options for each command.

### init
Initializes a new coding project. If `settings.yaml` is missing, writes the settings
file with default values. Make any desired edits, and then run `qc init` again. 
You can skip this step by passing **--accept-defaults** (**-y**) to the first
invocation of `qc init`. It is safe to re-run `qc init`. 

    $ qc init

### check
Checks that all required files and directories are in place. 

    $ qc check

### code
Opens a split-screen vim window with a corpus file and the corresponding code
file. The name of the coder is a required positional argument. 
After optionally filtering using common options (below), select a document with
no existing codes (for this coder) using **--first** (**-1**) or **--random**
(**-r**)

    $ qc code chris -1

Save and close your editor when you finish. In the unlikely event that your editor 
crashes or your battery dies before you finish coding, your saved changes are 
persisted in `codes.txt`. Run `qc code --recover` to resume the coding session.

### codebook (cb)
Ensures that all codes in the project are included in the codebook. (New codes are
added automatically, but if you accidentally delete some while editing the codebook, 
`qc codebook` will replace them.)

    $ qc codebook

### coders
List all coders in the current project.

### memo
Opens your default editor to write a memo, optionally passing **--message** (**-m**)
as the title of the memo. Use **--list** (**-l**) to list all memos.

    $ qc memo -m "It's all starting to make sense..."

### upgrade
Upgrade a `qc` project from a prior version of `qc`.

### version
Show the current version of `qc`.

## Corpus commands
The following commands are grouped under `qc corpus`.

### corpus list
List all files in the corpus.

### corpus import
Import files into the corpus, copying source files into `corpus`, formatting them 
(see options), and registering them in the database. Individual files can be imported, 
or directories can be recursively imported using **--recursive** (**-r**). 

    $ qc corpus import transcripts --recursive

If you want to import files into a specific subdirectory within the `corpus`, use 
**--corpus-root** (**-c**). For example, if you wanted to import an additional 
transcript after importing the transcripts directory, you could run:

    $ qc corpus import follow_up.txt --corpus-root transcripts

Several importers are available to format files, and can be specified using
**--importer** (**-i**). The default importer, `pandoc`, uses 
[Pandoc](https://pandoc.org/) to convert files into plain-text, and then hard-wrap
them at 80 characters. `verbatim` imports text files without making any changes. 
Future importers will include text extraction from PDFs and automatic transcription of 
audio files.

### corpus move (mv)
Move a document from one corpus path to another (or recursively move a directory 
with **--recursive** (**-r**)). Do not move corpus files directly or they will become
out of sync with their metadata in the database.

### corpus remove (rm)
Remove a document from the corpus, along with codes applied to the document. 
Or recursively remove all documents in a directory with **--recursive** (**-r**).

## Codes commands
The following commands are grouped under `qc code`.

### codes list (ls)
Lists all the codes currently in the codebook.

    $ qc list --expanded

### codes rename
Goes through all the code files and replaces one or more codes with another. 
Removes the old codes from the codebook.

    $ qc rename humorous funy funnny funny

### codes find
Displays all occurences of the provided code(s). 

    $ qc find math science art

### codes stats
Displays frequency of usage for each code. Note that counts include all usages of children.
List code names to show only certain codes. In addition to the common options below, 
code results can be filtered with `--max`, and `--min`. 

    $qc stats --recursive-codes --depth 2

### codes crosstab (ct)
Displays a cross-tabulation of code co-occurrence within the unit of analysis,
as counts or as probabilities (**--probs**, **-0**). Optionally use a compact
(**--compact**, **-z**) output format to display more columns. 
In the future, this may also include odds ratios. 

    $qc crosstab planning implementation evaluation --recursive-codes --depth 1 --probs

## Common Options

### Specify the settings file

Every `qc` command supports **--settings** (**-s**), which allows you to specify a settings file. 
This makes it possible to run `qc` commands from outside the project directory or from 
within scripts without ambiguity. 

The settings file can also be specified via the **QC_SETTINGS** environment variable. This 
is makes it easy to check multiple settings files into version control (e.g. for users
with different preferences, or to try out different codebook structures).

### Filter the corpus

- **--pattern** `pattern` (**-p**): Only include corpus files and their codes which match
  (glob-style) `pattern`.
- **--filenames** `filepath` (**-f**): Only include corpus files listed in
  `filepath` (one per line).

### Filter code selection

- **code** [codes]: Many commands have an optional positional argument in which
  you may list codes to consider. If none are given, the root node in the tree
  of codes is assumed.
- **--coder** `coder` (**-c**): Only include codes entered by `coder` (if you
  use different names for different rounds of coding, you can also use this to
  filter by round of coding). 
- **--recursive-codes** (**-r**): Include children of selected codes. 
- **--depth** `depth` (**-d**): Limit the recursive depth of codes to select. 
- **--unit** `unit` (**-n**): Unit of analysis for reporting. Currently
  "line", "paragraph", and "document" are supported. Paragraphs are delimted
  by blank lines.
- **--recursive-counts** (**-a**): When counting codes, also count instances of
  codes' children. In contrast to **--recursive-codes**, which controls which
  codes will be reported, this option controls how the counting is done. 

### Output and formatting

- **--format** `format` (**-m**): Formatting style for output table. Supported
  values include "html", "latex", "github", and 
  [many more](https://pypi.org/project/tabulate/). 
- **--expanded** (**-e**): Show names of codes in expanded form (e.g. 
  "coding_process:grounded")
- **--outfile** `outfile` (**-o**): Save tabular results to a csv file instead
  of displaying.
