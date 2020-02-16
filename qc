#!/usr/bin/env python3

import argparse
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.viewer import QCCorpusViewer
from pathlib import Path

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

def add_code_filtering_options(command):
    command.add_argument("code", help="One or more codes", nargs="+")
    command.add_argument("-r", "--recursive", help="Include child codes", action="store_true")
    command.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)
    command.add_argument("-n", "--unit", help="Unit of analysis", choices=['line', 'document'], default='line')
    
def add_table_display_options(command):
    command.add_argument("-e", "--expanded", help="Show all results in expanded form", action="store_true")
    command.add_argument("-m", "--format", help="Output format. For values, see documentation for tabulate")

def _fmt(opts, _and=True):
    if len(opts) == 1:
        return opts[0]
    else:
        return "{} {} {}".format(", ".join(opts[:-1]), "and" if _and else "or", opts[-1])

class IncompatibleOptions(ValueError):
    pass

class Truthy:
    "Like True, but when used in comparison, coerces the other object to bool."
    val = True
    def __eq__(self, other):
        return bool(other) == self.val

    def __bool__(self):
        return self.val

    def __str__(self):
        return str(self.val) 

class Falsy(Truthy):
    "Like Truthy, but Falsy."
    val = False

def check_incompatible(args, **conditions):
    problem = all(val == getattr(args, opt, None) for opt, val in conditions.items())
    if problem:
        opts = ["--{}".format(k) for k in conditions.keys()]
        if all(conditions.values()):
                message = "{} may not {} be used.".format(_fmt(opts), "both" if len(conditions) == 2 else "all")
        elif not any(conditions.values()):
                message = "One of {} is required.".format(_fmt(opts, _and=False))
        else:
            present = ["--{}".format(o) for o, req in conditions.items() if req]
            absent = ["--{}".format(o) for o, req in conditions.items() if not req]
            message = "{}{} must be used when {} {} used.".format(
                "One of " if len(absent) > 1 else "",
                _fmt(absent), 
                _fmt(present), 
                "is" if len(present) == 1 else "are"
            )
        print(args)
        raise IncompatibleOptions(message)

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

rename = subparsers.add_parser("rename", help="Rename a code")
rename.add_argument("old_code")
rename.add_argument("new_code")
rename.add_argument("-c", "--coder", help="Name of coder")

find = subparsers.add_parser("find", help="Find all coded text")
add_datasource_filtering_options(find)
add_code_filtering_options(find)
find.add_argument("-B", "--before", help="Number of lines before the code to show", default=2, type=int)
find.add_argument("-C", "--after", help="Number of lines after the code to show", default=2, type=int)
find.add_argument("-t", "--no-codes", help="Do not show matching codes", action="store_true")

stats = subparsers.add_parser("stats", help="Show statistics about code usage")
stats.add_argument("code", help="Code(s) to display", nargs="*")
stats.add_argument("-u", "--max", help="Maximum count value to show", type=int)
stats.add_argument("-l", "--min", help="Minimum count value to show", type=int)
stats.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)
stats.add_argument("-e", "--expanded", help="Show all results in expanded form", action="store_true")
stats.add_argument("-m", "--format", help="Output format. For values, see documentation for tabulate")
stats.add_argument("-p", "--pattern", help="Pattern to filter corpus filenames (glob-style)")
stats.add_argument("-f", "--filenames", help="File path containing a list of filenames to use")
stats.add_argument("-i", "--invert", help="Invert file selection", action="store_true")
stats.add_argument("-n", "--unit", help="Unit of analysis", choices=['line', 'document'], default='line')

memo = subparsers.add_parser("memo", help="write a memo")
memo.add_argument("coder", help="id of memo author")
memo.add_argument("-m", "--message", help="short message, title of memo file")
memo.add_argument("-l", "--list", help="list all memos in order", action="store_true", dest="list_memos")

def main(args):
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
    if args.command == "rename":
        corpus.rename_code(args.old_code, args.new_code, coder=args.coder)
    if args.command == "find":
        viewer.show_coded_text(
            args.code, 
            before=args.before, 
            after=args.after, 
            recursive=args.recursive,
            depth=args.depth,
            unit=args.unit,
            file_pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            show_codes=not args.no_codes,
        )
    if args.command == "stats":
        files = Path(args.filenames).read_text().split("\n") if args.filenames else None
        viewer.show_stats(
            args.code, 
            max_count=args.max, 
            min_count=args.min, 
            depth=args.depth, 
            expanded=args.expanded, 
            format=args.format, 
            file_pattern=args.pattern,
            file_list=files,
            invert_files=args.invert,
            unit=args.unit
        )

    if args.command == "memo":
        if args.list_memos:
            print(viewer.list_memos())
        else:
            viewer.memo(args.coder, args.message)

args = parser.parse_args()
main(args)

