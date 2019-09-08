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

Due to its nature as a command-line program, `qc` is only well-suited to coding
textual data. 

# Installation

    pip install qualitative-coding

# Setup 

- All the source files you want to code should be in a directory (possibly
  nested). 
- Choose a working directory. Run `qc init`. This will create `settings.yaml`.
- In `settings.yaml`, update `corpus_dir` with the directory holding your source
  files. This may be relative to `settings.yaml` or absolute. Similarly, specify
a directory `codes_dir` where you will store the files containing your codes.
Update the locations of `codebook` and `log_file` as well, if you like. 
- Run `qc init` again. 

# Usage

---

## OLD

This repo contains the text from interviews and tools for analyzing them. Our strategy will be:

1. Open coding: Tagging whatever seems interesting in the interviews
2. Developing/adopting frameworks: Organizing codes into hierarchies, possibly informed by prior research (for example, Paulo's four rationales for CS, reserach on inclusion/exclusion in CS, etc. 
3. Analytical memos: Paragraph-length writing in which we start to process the patterns we're seeing into interpretive claims
4. Supporting interpretive claims with quantitative analyses of codes and 

## Coding tools

The `src/codes.py` script contains a bunch of useful tools. The tools are configured in `src/settings.py`. 
Run the script with no arguments for help. You can get help for a specific command by:

    ./codes.py rename --help

### codebook (cb)
Scans through all the code files and adds new codes to the codebook. 

    ./codes.py codebook

### list (ls)
Lists all the codes currently in use. By default, lists them as a tree. The `--expanded` option 
will instead flatten the list of codes, and list each as something like `subjects:math:algebra`.

    ./codes.py list --expanded

### rename
Goes through all the code files and replaces one code with another. Removes the old code from the codebook.

    ./codes.py rename funy funny

### find
Displays all occurences of the provided code(s). With the `--recursive` option, also includes child
codes in the codebook's tree of codes. Note that a code may appear multiple times in the codebook; in this case, 
the `--recursive` option will search for all children of all instances. When you want to grab text for a quotation,
use the `--textonly` option. The `--files` option lets you filter which corpus files to search.

    ./codes.py find math science art --recursive

### stats
Displays frequency of usage for each code. Note that counts include all usages of children.
List code names to show only certain codes. Filter code results with 
`--depth`, `--max`, and `--min`. Use the `--expanded` option to show the full name of each code, rather than the 
tree representation. Arguments to `--format` may be any supported by [tabulate](https://bitbucket.org/astanin/python-tabulate).
The `--files` option lets you filter which corpus files to use in computing stats.

    ./codes.py stats curriculum math algebra --depth 0
    ./codes.py stats --max 1

## Command-line tools

### Search for any text 

    grep -r "professional" interviews/*.txt

### Split a text file at 80 characters

    fold -w 80 -s file.txt > file.txt

## Roadmap
I plan to keep developing this set of tools, for this and other qualitative coding projects. The following tools are coming:

- inter-rater reliability
- Show stats for particular coders or particular texts
- add autocomplete for codes
- glob matching for filtering which corpus files to consider
- distribute as a separate library, `qc`, and provide a default configuration without settings. (By default, name.txt is a corpus file 
  and name.codes.coderlabel.txt is a corresponding code file.
    - Add filter options on codefiles, so that you can use only a later coding if you like. Does this
      put too much responsibility on the user to set up an appropriate naming scheme?
- Add search and filter options on list as well. These should be abstracted out as separate functions.
- In find, show codes in hierarchy when listing which codes will be shown
    - In the class, have a queryset for codes which is lazily evaluated, so that filters can be chain-applied. Probably this is a class.
- In `find`, wrap code text at a set number of lines, and leave whitespace on the text side until all the codes for a line have been displayed.
