# Interview Coding

Qualitative coding for comptuer scientists. 

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
the interface supported it. 

Qualitative Coding, or `qc`, was designed to address these issues. The impetus
was my own dissertation work. 

## Limitations

- Due to its nature as a command-line program, `qc` is only well-suited to coding textual data. 
- `qc` uses line numbers as a fundamental unit. Therefore, it requires text files in your corpus to be 
  hard-wrapped at 80 characters. The `init` task will handle this for you. 
- Currently, the only interface for actually doing the coding is a split-screen
  in vim, with the corpus text on one side and comma-separated codes adjacent. This works well 
  for me, but might not work well for you. I have other ideas in the pipeline,
  but they won't be around soon.

# Installation

    pip install qualitative-coding

# Setup 

- All the source files you want to code should be in a directory (possibly
  nested). 
- Choose a working directory. Run `qc init`. This will create `settings.yaml`.
- In `settings.yaml`, update `corpus_dir` with the directory holding your source
  files. This may be relative to `settings.yaml` or absolute. Similarly, specify
  directories for `codes_dir` `logs_dir`, `memos_dir`, and the YAML file where you want
  to store your codebook. Unless you're particular, the default settings are fine. 
- Run `qc init --prepare_corpus --prepare_codes --coder yourname`. This will
  hard-wrap all the text in your corpus at 80 characters and create blank coding
  files. 

# Usage

## Workflow

`qc` is designed to give you a powerful terminal-based interface. The general
workflow is to use `code` to apply qualitative codes to your text files. As you
go, you will start to have ideas about the meanings and organization of your
codes. Use `memo` to capture these. 

Once you finish a round of coding, it's time to reorganize your codes. Use
`codebook` to refresh the codebook based on new coding. Use `stats` to see the
distribution of your codes. If you want to move codes into a tree, make these
changes directly in the codebook's YAML. If you realize you have redundant
codes, use `rename`. 

The `--coder` argument supports keeping track of multiple coders on a project,
and there are options to filter on coder where relevant. Analytical tools, such
as correlations (on multiple units of analysis) and inter-rater reliatbility are
coming. 

## Commands

Use `--help` for a full list of available options for each command.

### init
Initializes a new coding project, as described above.

    $ qc init

### check
Checks that all required files and directories are in place. 

    $ qc check

### code
Opens a split-screen vim window with a corpus file and the corresponding code
file. The name of the coder is a required positional argument. 
Use `--pattern` to glob-match the corpus file you want to code. If
multiple are matched, you will be prompted to choose. The `--first-without-codes` option is
particularly useful for coding the next uncoded text.

    $ qc code chris -f

### codebook (cb)
Scans through all the code files and adds new codes to the codebook. 

    $ qc codebook

### list (ls)
Lists all the codes currently in use. By default, lists them as a tree. The `--expanded` option 
will instead flatten the list of codes, and list each as something like `subjects:math:algebra`.

    $ qc list --expanded

### rename
Goes through all the code files and replaces one code with another. Removes the old code from the codebook.

    $ qc rename funy funny

### find
Displays all occurences of the provided code(s). With the `--recursive` option, also includes child
codes in the codebook's tree of codes. Note that a code may appear multiple times in the codebook; in this case, 
the `--recursive` option will search for all children of all instances. When you want to grab text for a quotation,
use the `--textonly` option. The `--files` option lets you filter which corpus files to search.

    $ qc find math science art --recursive

### stats
Displays frequency of usage for each code. Note that counts include all usages of children.
List code names to show only certain codes. Filter code results with 
`--depth`, `--max`, and `--min`. Use the `--expanded` option to show the full name of each code, rather than the 
tree representation. Arguments to `--format` may be any supported by [tabulate](https://bitbucket.org/astanin/python-tabulate).
The `--files` option lets you filter which corpus files to use in computing stats.

    $ qc stats curriculum math algebra --depth 1
