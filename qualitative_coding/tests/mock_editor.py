#!/usr/bin/env python3

# This is a mock editor for testing purposes. 
# Whereas a real editor would present the corpus and code files
# to the user for coding, the mock editor goes ahead and codes
# line with 'code_one' and line two (if it exists) with 'code_two'.
# When --crash is passed, exits with an exception, allowing testing
# of the error condition.

from argparse import ArgumentParser
from pathlib import Path
import sys

parser = ArgumentParser()
parser.add_argument("corpus_file_path")
parser.add_argument("codes_file_path", nargs='?')
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--crash", action="store_true")
parser.add_argument("--memo", action="store_true")
args = parser.parse_args()

if args.crash:
    if args.verbose:
        print("Crashing the mock editor, as requested...", file=sys.stderr)
    raise SystemExit(1)

if args.memo:
    if args.verbose:
        print("Mock Editor is in memo mode.")
    memo_file_path = Path(args.corpus_file_path)
    memo = "I'm having all these ideas. I need to write them down."
    memo_file_path.write_text(memo_file_path.read_text() + memo)
else:
    nlines = len(Path(args.corpus_file_path).read_text().split('\n'))
    if nlines == 1:
        Path(args.codes_file_path).write_text("code_one")
    else:
        lines = ["line, one", "line, two"] + ([""] * (nlines - 2))
        Path(args.codes_file_path).write_text('\n'.join(lines))
    if args.verbose:
        print('-' * 80)
        print("MOCK EDITOR")
        print('-' * 80)
        text = open(args.corpus_file_path)
        codes = open(args.codes_file_path)
        for tl, cl in zip(text, codes):
            print(f"{tl.strip().ljust(80, ' ')}| {cl.strip()}")
        text.close()
        codes.close()



