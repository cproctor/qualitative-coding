#!/usr/bin/env python3

import argparse
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.viewer import QCCorpusViewer
from pathlib import Path

parser = argparse.ArgumentParser(prog="python codes.py")
parser.add_argument('-s', '--settings', default='settings.yaml')
subparsers = parser.add_subparsers(help="command", dest="command")
subparsers.required = True

init = subparsers.add_parser("init", help="Initialize the qc project")
init.add_argument("--prepare-corpus", help="Prepare all texts in corpus by wrapping at 80 chars", action="store_true")
init.add_argument('-p', "--pattern", help="pattern to match for which files to format")
init.add_argument("-f", "--preformatted", help="Wrap, but respect prior formatting", action="store_true")
init.add_argument("--prepare-codes", help="Prepare code files for a coder", action="store_true")
init.add_argument("--coder", help="Name of coder")

check = subparsers.add_parser("check", help="Check settings")

code = subparsers.add_parser("code", help="Open a file for coding")
code.add_argument("coder", help="Name of coder")
code.add_argument('-p', "--pattern", help="pattern to match for which files to format")
code.add_argument("-f", "--first", help="Open the first file without codes", action="store_true")
code.add_argument("-r", "--random", help="Open a random file without codes", action="store_true")

codebook = subparsers.add_parser("codebook", help="Update the codebook", aliases=["cb"])

ls = subparsers.add_parser("list", help="List codes", aliases=["ls"])
ls.add_argument("-e", "--expanded", action="store_true")

rename = subparsers.add_parser("rename", help="Rename a code")
rename.add_argument("old_code")
rename.add_argument("new_code")

find = subparsers.add_parser("find", help="Find all coded text")
find.add_argument("code", help="Code(s) to find", nargs="+")
find.add_argument("-B", "--before", help="Number of lines before the code to show", default=2, type=int)
find.add_argument("-C", "--after", help="Number of lines after the code to show", default=2, type=int)
find.add_argument("-r", "--recursive", help="Include child codes", action="store_true")
find.add_argument("-t", "--textonly", help="Show text but not codes", action="store_true")
find.add_argument("-f", "--files", help="Filter corpus filenames to use (glob-style)")
find.add_argument("-l", "--list", help="List files containing code", action="store_true", dest="list_files")

stats = subparsers.add_parser("stats", help="Show statistics about code usage")
stats.add_argument("code", help="Code(s) to display", nargs="*")
stats.add_argument("-u", "--max", help="Maximum count value to show", type=int)
stats.add_argument("-l", "--min", help="Minimum count value to show", type=int)
stats.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)
stats.add_argument("-e", "--expanded", help="Show all results in expanded form", action="store_true")
stats.add_argument("-m", "--format", help="Output format. For values, see documentation for tabulate")
stats.add_argument("-f", "--files", help="Filter corpus filenames to use (glob-style)")

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

    if args.command == "check":
        corpus.validate()

    if args.command == "code":
        if args.first and args.random:
            raise ValueError("Incompatible flags. Can't choose first and random")
        if args.first:
            choice = "first"
        elif args.random:
            choice = "random"
        else:
            choice = None
        viewer.open_for_coding(pattern=args.pattern, coder=args.coder, choice=choice)

    if args.command == "init":
        if args.prepare_corpus:
            corpus.prepare_texts(pattern=args.pattern, preformatted=args.preformatted)
        if args.prepare_codes:
            if not args.coder:
                raise ValueError("Name of coder is required")
            corpus.prepare_code_files(pattern=args.pattern, coder=args.coder)

    if args.command in ["codebook", "cb"]:
        corpus.update_codebook()
    if args.command in ["list", "ls"]:
        viewer.list_codes(args.expanded)
    if args.command == "rename":
        corpus.rename_code(args.old_code, args.new_code)
    if args.command == "find":
        viewer.show_coded_text(
            args.code, 
            before=args.before, 
            after=args.after, 
            recursive=args.recursive,
            textonly=args.textonly, 
            filepattern=args.files,
            list_files=args.list_files
        )
    if args.command == "stats":
        viewer.show_stats(
            args.code, 
            max_count=args.max, 
            min_count=args.min, 
            depth=args.depth, 
            expanded=args.expanded, 
            format=args.format, 
            filepattern=args.files
        )

    if args.command == "memo":
        if args.list_memos:
            print(viewer.list_memos())
        else:
            viewer.memo(args.coder, args.message)

args = parser.parse_args()
main(args)





