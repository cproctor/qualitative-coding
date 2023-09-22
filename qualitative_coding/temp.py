import argparse
from textwrap import fill

def prepare_corpus_text(text, width=80, preformatted=False):
    "Splits corpus text at blank lines and wraps it."
    if preformatted:
        outlines = []
        lines = text.split("\n")
        for line in lines:
            while True:
                outlines.append(line[:width])
                if len(line) < 80:
                    break
                line = line[width:]
        return "\n".join(outlines)
    else:
        paragraphs = text.split("\n\n")
        return "\n\n".join(fill(p, width=width) for p in paragraphs)

def add_code_filtering_options(command, recursive_counts=True, code_required=True):
    if code_required:
        command.add_argument("code", help="One or more codes", nargs="+")
    else:
        command.add_argument("code", help="One or more codes", nargs="*")
    command.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)
    command.add_argument("-n", "--unit", help="Unit of analysis", 
            choices=['line', 'paragraph', 'document'], default='line')
    command.add_argument("-r", "--recursive-codes", help="Include child codes", 
            action="store_true")
    if recursive_counts:
        command.add_argument("-a", "--recursive-counts", action="store_true",
            help="Counts for codes include child codes")
    
def add_table_display_options(command):
    command.add_argument("-e", "--expanded", action="store_true", 
            help="Show names of codes in expanded form")
    command.add_argument("-m", "--format", 
            help="Output format. For values, see documentation for tabulate")
    command.add_argument("-o", "--outfile", help="Filename for CSV export")
