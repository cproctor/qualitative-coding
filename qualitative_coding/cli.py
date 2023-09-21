import argparse
from textwrap import fill

def merge_ranges(ranges, clamp=None):
    "Overlapping ranges? Let's fix that. Optionally supply clamp=[0, 100]"
    if any(filter(lambda r: r.step != 1, ranges)): raise ValueError("Ranges must have step=1")
    endpoints = [(r.start, r.stop) for r in sorted(ranges, key=lambda r: r.start)]
    results = []
    if any(endpoints):
        a, b = endpoints[0]
        for start, stop in endpoints:
            if start <= b:
                b = max(b, stop)
            else:
                results.append(range(a, b))
                a, b = start, stop
        results.append(range(a, b))
    if clamp is not None:
        lo, hi = clamp
        results = [range(max(lo, r.start), min(hi, r.stop)) for r in results]
    return results

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

def prompt_for_choice(prompt, options):
    "Asks for a prompt, returns an index"
    print(prompt)
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt}")
    while True:
        raw_choice = input("> ")
        if raw_choice.isdigit() and int(raw_choice) in range(1, len(options)+1):
            return int(raw_choice)
        print("Sorry, that's not a valid choice.")


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
            quantifier = "both" if len(conditions) == 2 else "all"
            message = f"{_fmt(opts)} may not {quantifier} be used."
        elif not any(conditions.values()):
            message = "One of {_fmt(opts, _and=False)} is required."
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

def add_datasource_filtering_options(command, coder_required=False):
    command.add_argument("-p", "--pattern", 
            help="Pattern to filter corpus filenames (glob-style)")
    command.add_argument("-f", "--filenames", 
            help="File path containing a list of filenames to use")
    command.add_argument("-i", "--invert", action="store_true", 
            help="Invert file selection")
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

def build_arg_parser():
    parser = argparse.ArgumentParser(prog="qc")
    parser.add_argument('-s', '--settings', default='settings.yaml')
    subparsers = parser.add_subparsers(help="command", dest="command")
    subparsers.required = True

    init = subparsers.add_parser("init", help="Initialize the qc project")
    add_datasource_filtering_options(init)
    init.add_argument("--prepare-corpus", action="store_true",
            help="Prepare all texts in corpus by wrapping at 80 chars")
    init.add_argument("--prepare-codes", action="store_true", 
            help="Prepare code files for a coder")
    init.add_argument("-w", "--preformatted", action="store_true",
            help="Wrap, but respect prior formatting")

    check = subparsers.add_parser("check", help="Check settings")

    code = subparsers.add_parser("code", help="Open a file for coding")
    add_datasource_filtering_options(code, coder_required=True)
    code.add_argument("-1", "--first", action="store_true", 
            help="Open the first file without codes")
    code.add_argument("-r", "--random", action="store_true",
            help="Open a random file without codes")

    codebook = subparsers.add_parser("codebook", help="Update the codebook", aliases=["cb"])

    ls = subparsers.add_parser("list", help="List codes", aliases=["ls"])
    ls.add_argument("-e", "--expanded", action="store_true")
    ls.add_argument("-d", "--depth", help="Maximum depth in code tree", type=int)

    rename = subparsers.add_parser("rename", help="Rename a code", aliases=['rn'])
    add_datasource_filtering_options(rename, coder_required=False)
    rename.add_argument("old_codes", help='code(s) to rename', nargs='+')
    rename.add_argument("new_code", help='code to use as a replacement')
    rename.add_argument("-u", "--update_codebook", action="store_true", 
            help="force update codebook (even if renaming is scoped)")
    find = subparsers.add_parser("find", help="Find all coded text")
    add_datasource_filtering_options(find)
    add_code_filtering_options(find, recursive_counts=False)
    find.add_argument("-B", "--before", default=2, type=int, 
            help="Number of lines before the code to show")
    find.add_argument("-C", "--after", default=2, type=int, 
            help="Number of lines after the code to show")
    find.add_argument("-l", "--no-codes", action="store_true", 
            help="Do not show matching codes")
    stats = subparsers.add_parser("stats", help="Show statistics about code usage")
    add_code_filtering_options(stats, code_required=False)
    add_datasource_filtering_options(stats)
    add_table_display_options(stats)
    stats.add_argument("-u", "--max", help="Maximum count value to show", type=int)
    stats.add_argument("-l", "--min", help="Minimum count value to show", type=int)
    stats.add_argument("-t", "--total-only", action="store_true", 
            help="Show total but not count")
    crosstab = subparsers.add_parser("crosstab", aliases=['ct'], 
            help="Cross-tabulate code occurrences")
    add_code_filtering_options(crosstab, code_required=False)
    add_datasource_filtering_options(crosstab)
    add_table_display_options(crosstab)
    crosstab.add_argument("-0", "--probs", action="store_true", 
            help="Probabilities instead of counts")
    crosstab.add_argument("-z", "--compact", help="Compact display", action="store_true")
    crosstab.add_argument("-y", "--tidy", help="Return tidy format", action="store_true")
    crosstab.add_argument("-u", "--max", help="Maximum count value to show", type=int)
    crosstab.add_argument("-l", "--min", help="Minimum count value to show", type=int)

    memo = subparsers.add_parser("memo", help="write a memo")
    memo.add_argument("coder", help="memo author")
    memo.add_argument("-m", "--message", help="short message, title of memo file")
    memo.add_argument("-l", "--list", action="store_true", dest="list_memos", 
            help="list all memos in order")
    return parser
