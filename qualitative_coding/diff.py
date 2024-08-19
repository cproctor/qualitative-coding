import re
from more_itertools import peekable
from difflib import unified_diff
from subprocess import run

def get_git_diff(path):
    "Gits a diff between file state and HEAD"
    result = run(f"git diff {path}", shell=True, capture_output=True, text=True)
    return result.stdout

def get_diff(path0, path1):
    "Gets a diff between two file paths"
    with open(path0) as fh:
        doc0 = [line for line in fh]
    with open(path1) as fh:
        doc1 = [line for line in fh]
    return ''.join(unified_diff(doc0, doc1))

def reindex_coded_lines(coded_lines, diff):
    """Returns a new version of coded_lines, with line numbers updated to account for diff.
    Assumes coded_lines are sorted by line number.
    """
    offsets = peekable(read_diff_offsets(diff))
    current_offset_line = 0
    current_offset = 0
    cum_offset = 0
    reindexed_coded_lines = []
    for code, coder, line, path in coded_lines:
        try:
            if offsets.peek()[0] <= line:
                current_offset_line, current_offset = next(offsets)
                cum_offset += current_offset
        except StopIteration:
            pass


    return reindexed_coded_lines

def read_diff_offsets(diff):
    """Reads a unified diff and returns a list of (line, offset) tuples.
    For example, (6, 2) represents an insertion of 2 lines at line 6. 
    Adjacent deletions and insertions are assumed to be edited versions
    of the same line, so if 4 lines were deleted and 3 lines inserted at
    line 10, this would be represented as (13, -1).
    """
    offsets = []
    lines = peekable(diff.split('\n'))
    try:
        read_preamble(lines)
        while True:
            offsets += read_hunk(lines)
    except StopIteration:
        return offsets

def read_preamble(lines):
    line = next(lines)
    while not line.startswith('---'):
        line = next(lines)
    line = next(lines)
    assert(line.startswith('+++'))

def read_hunk(lines):
    line = next(lines)
    line_number = read_line_number(line)
    minus = 0
    plus = 0
    in_op = False
    op_start_line_number = 1
    ops = []
    try:
        while not lines.peek().startswith('@'):
            line = next(lines)
            if in_op:
                if line[0] == '-':
                    minus += 1
                elif line[0] == '+':
                    plus += 1
                else:
                    in_op = False
                    if plus - minus > 0:
                        ops.append((op_start_line_number, plus - minus))
                    elif plus - minus < 0:
                        ops.append((op_start_line_number + minus - plus - 1, plus - minus))
            else:
                if line[0] == '-':
                    in_op = True
                    op_start_line_number = line_number
                    minus, plus = 1, 0
                elif line[0] == '+':
                    in_op = True
                    op_start_line_number = line_number
                    minus, plus = 0, 1
            line_number += 1
    finally:
        if in_op:
            if plus - minus > 0:
                ops.append((op_start_line_number, plus - minus))
            elif plus - minus < 0:
                ops.append((op_start_line_number + minus - plus - 1, plus - minus))
        return ops

def read_line_number(hunk_preamble):
    match = re.match('\s*@@ \-(\d+)', hunk_preamble)
    return int(match.group(1))

def in_git_repo():
    "Checks whether the current working directory is in a git repo."
    return run("git status", shell=True, capture_output=True).returncode == 0

    











