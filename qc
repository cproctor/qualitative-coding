#!/usr/bin/env python3

import argparse
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.viewer import QCCorpusViewer
from qualitative_coding.helpers import (
    Truthy, 
    Falsy, 
    _fmt, 
    check_incompatible,
)

parser = argparse.ArgumentParser(prog="qc")
parser.add_argument('-s', '--settings', default='settings.yaml')
subparsers = parser.add_subparsers(help="command", dest="command")
subparsers.required = True

def add_datasource_filtering_options(command, coder_required=False):
    command.add_argument("-p", "--pattern", help="Pattern to filter corpus filenames (glob-style)")
    command.add_argument("-f", "--filenames", help="File path containing a list of filenames to use")
    command.add_argument("-i", "--invert", help="Invert file selection", action="store_true")
    if coder_required:
        command.add_argument("coder", help="Name of coder")
    else:
        command.add_argument("-c", "--coder", help="Name of coder")

def add_code_filtering_options(command, recursive_counts=True, code_required=True):
    if code_required:
        command.add_argument("code", help="One or more codes", nargs="+")
    else:
        command.add_argument("code", help="One or more codes", nargs="*")
    command.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)
    command.add_argument("-n", "--unit", help="Unit of analysis", choices=['line', 'paragraph', 'document'], default='line')
    command.add_argument("-r", "--recursive-codes", help="Include child codes", action="store_true")
    if recursive_counts:
        command.add_argument("-a", "--recursive-counts", help="Counts for codes include child codes", action="store_true")
    
def add_table_display_options(command):
    command.add_argument("-e", "--expanded", help="Show names of codes in expanded form", action="store_true")
    command.add_argument("-m", "--format", help="Output format. For values, see documentation for tabulate")
    command.add_argument("-o", "--outfile", help="Filename for CSV export")

init = subparsers.add_parser("init", help="Initialize the qc project")
add_datasource_filtering_options(init)
init.add_argument("--prepare-corpus", help="Prepare all texts in corpus by wrapping at 80 chars", action="store_true")
init.add_argument("--prepare-codes", help="Prepare code files for a coder", action="store_true")
init.add_argument("-w", "--preformatted", help="Wrap, but respect prior formatting", action="store_true")

check = subparsers.add_parser("check", help="Check settings")

code = subparsers.add_parser("code", help="Open a file for coding")
add_datasource_filtering_options(code, coder_required=True)
code.add_argument("-1", "--first", help="Open the first file without codes", action="store_true")
code.add_argument("-r", "--random", help="Open a random file without codes", action="store_true")

codebook = subparsers.add_parser("codebook", help="Update the codebook", aliases=["cb"])

ls = subparsers.add_parser("list", help="List codes", aliases=["ls"])
ls.add_argument("-e", "--expanded", action="store_true")
ls.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)

rename = subparsers.add_parser("rename", help="Rename a code", aliases=['rn'])
add_datasource_filtering_options(rename, coder_required=False)
rename.add_argument("old_codes", help='code(s) to rename', nargs='+')
rename.add_argument("new_code", help='code to use as a replacement')
rename.add_argument("-u", "--update_codebook", help="force update codebook (even if renaming is scoped)", action="store_true")

find = subparsers.add_parser("find", help="Find all coded text")
add_datasource_filtering_options(find)
add_code_filtering_options(find, recursive_counts=False)
find.add_argument("-B", "--before", help="Number of lines before the code to show", default=2, type=int)
find.add_argument("-C", "--after", help="Number of lines after the code to show", default=2, type=int)
find.add_argument("-l", "--no-codes", help="Do not show matching codes", action="store_true")

stats = subparsers.add_parser("stats", help="Show statistics about code usage")
add_code_filtering_options(stats, code_required=False)
add_datasource_filtering_options(stats)
add_table_display_options(stats)
stats.add_argument("-u", "--max", help="Maximum count value to show", type=int)
stats.add_argument("-l", "--min", help="Minimum count value to show", type=int)
stats.add_argument("-t", "--total-only", help="Show total but not count", action="store_true")

crosstab = subparsers.add_parser("crosstab", help="Cross-tabulate code occurrences", aliases=['ct'])
add_code_filtering_options(crosstab, code_required=False)
add_datasource_filtering_options(crosstab)
add_table_display_options(crosstab)
crosstab.add_argument("-0", "--probs", help="Probabilities instead of counts", action="store_true")
crosstab.add_argument("-z", "--compact", help="Compact display", action="store_true")
crosstab.add_argument("-y", "--tidy", help="Return tidy format", action="store_true")
crosstab.add_argument("-u", "--max", help="Maximum count value to show", type=int)
crosstab.add_argument("-l", "--min", help="Minimum count value to show", type=int)

memo = subparsers.add_parser("memo", help="write a memo")
memo.add_argument("coder", help="memo author")
memo.add_argument("-m", "--message", help="short message, title of memo file")
memo.add_argument("-l", "--list", help="list all memos in order", action="store_true", dest="list_memos")

def main(args):
    check_incompatible(args, invert=True, pattern=None)

    if args.command == "init":
        if not Path(args.settings).exists():
            QCCorpus.initialize(args.settings)
            return 
        else:
            QCCorpus.initialize(args.settings)
    corpus = QCCorpus(args.settings)
    viewer = QCCorpusViewer(corpus)
    if hasattr(args, 'filenames') and args.filenames:
        file_list = Path(args.filenames).read_text().split("\n")
    else:
        file_list = None

    if args.command == "check":
        corpus.validate()

    if args.command == "code":
        check_incompatible(args, first=True, random=True)
        if args.first:
            choice = "first"
        elif args.random:
            choice = "random"
        else:
            choice = None
        viewer.open_for_coding(
            pattern=args.pattern, 
            file_list=file_list,
            invert=args.invert,
            coder=args.coder, 
            choice=choice
        )

    if args.command == "init":
        check_incompatible(args, prepare_corpus=False, preformatted=True)
        check_incompatible(args, prepare_codes=True, coder=None)
        check_incompatible(args, prepare_codes=False, coder=True)
        if args.prepare_corpus:
            corpus.prepare_corpus(
                pattern=args.pattern, 
                file_list=file_list,
                invert=args.invert,
                preformatted=args.preformatted)
        if args.prepare_codes:
            corpus.prepare_code_files(pattern=args.pattern, coder=args.coder)

    if args.command in ["codebook", "cb"]:
        corpus.update_codebook()
    if args.command in ["list", "ls"]:
        viewer.list_codes(args.expanded, depth=args.depth)
    if args.command in ["rename", "rn"]:
        corpus.rename_codes(
            old_codes=args.old_codes, 
            new_code=args.new_code, 
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            update_codebook=args.update_codebook,
        )
    if args.command == "find":
        viewer.show_coded_text(
            args.code, 
            before=args.before, 
            after=args.after, 
            recursive_codes=args.recursive_codes,
            depth=args.depth,
            unit=args.unit,
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            show_codes=not args.no_codes,
        )
    if args.command == "stats":
        check_incompatible(args, recursive=False, depth=Truthy())
        check_incompatible(args, recursive_counts=False, total_only=True)
        viewer.show_stats(
            args.code, 
            max_count=args.max, 
            min_count=args.min, 
            depth=args.depth, 
            recursive_codes=args.recursive_codes,
            recursive_counts=args.recursive_counts,
            expanded=args.expanded, 
            format=args.format, 
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            unit=args.unit,
            outfile=args.outfile,
            total_only=args.total_only,
        )

    if args.command in ["crosstab", "ct"]:
        check_incompatible(args, code=Truthy(), depth=Truthy(), recursive_codes=False)
        check_incompatible(args, tidy=True, compact=True)
        check_incompatible(args, tidy=True, probs=True)
        check_incompatible(args, tidy=False, min=Truthy())
        check_incompatible(args, tidy=False, max=Truthy())
        if args.tidy:
            viewer.tidy_codes(
                args.code, 
                depth=args.depth, 
                recursive_codes=args.recursive_codes,
                recursive_counts=args.recursive_counts,
                expanded=args.expanded, 
                format=args.format, 
                pattern=args.pattern,
                file_list=file_list,
                invert=args.invert,
                coder=args.coder,
                unit=args.unit,
                outfile=args.outfile,
                minimum=args.min,
                maximum=args.max,
            )
        else:
            viewer.crosstab(
                args.code, 
                depth=args.depth, 
                recursive_codes=args.recursive_codes,
                recursive_counts=args.recursive_counts,
                expanded=args.expanded, 
                format=args.format, 
                pattern=args.pattern,
                file_list=file_list,
                invert=args.invert,
                coder=args.coder,
                unit=args.unit,
                outfile=args.outfile,
                probs=args.probs,
                compact=args.compact,
            )

    if args.command == "memo":
        if args.list_memos:
            print(viewer.list_memos())
        else:
            viewer.memo(args.coder, args.message)

args = parser.parse_args()
main(args)
