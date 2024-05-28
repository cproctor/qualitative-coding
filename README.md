# Qualitative Coding

`qc` is a free, open-source command-line-based tool for qualitative data analysis
designed to support computational thinking. In addition to making qualitative data 
analysis process more efficient, computational thinking can contribute to the richness 
of subjective interpretation. Although numerous powerful software packages exist 
for qualitative data analysis, they are generally designed to protect users from complexity 
rather than providing affordances for engaging with complexity via algorithms and 
data structures. 

QDA, in its various
forms, is a core methodology for qualitative, mixed methods, and some
quantitative research in the social sciences. There are a variety of well-known 
commercial QDA software packages such as NVivo, Dedoose, Atlas.TI, and MaxQDA.
I have used several of these individually and in research groups; `qc` emerged from 
my loosely-theorized dissatisfaction with these tools. I value open and extensible 
research software; these were proprietary and expensive. I value "plain-text 
social science" [@healy2020]; these graphical user interfaces (GUIs) were user-friendly but 
ultimately limiting. As I developed prototypes of `qc` for my own use in several 
prior research projects [@proctor2019], I found that I was continually
augmenting [@engelbart1962] my ability to engage with complexity rather than 
simplifying the problem space. The release of `qc` documented here results from
a redesign and reimplementation of the original tool, in the hope that it will be 
useful to others.

## Installation

`qc` is distributed via the Python Package Index (PYPI), and can be
installed on any POSIX system (Linux, Unix, Mac OS, or Windows Subsystem
for Linux) which has Python 3.9 or higher installed. If you want to install
`qc` globally on your system, the cleanest approaach is to use 
[pipx](https://pipx.pypa.io/stable/). 

    pipx install qualitative-coding

If your research project
is already contained within a Python package and you want to install `qc` 
as a local dependency, simply add `qualitative-coding` to `pyproject.toml`
or `requirements.txt`.

`qc` relies on [Pandoc](https://pandoc.org/) for converting between file formats, 
so make sure that is installed as well. `qc` uses a text editor for coding; 
you should install Visual Studio Code, the default editor, unless you prefer
a different editor such as emacs or vim.
