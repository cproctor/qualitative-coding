# Qualitative Coding corpus viewer
# --------------------------------
# (c) 2019 Chris Proctor

from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.helpers import merge_ranges, prompt_for_choice
from tabulate import tabulate
from collections import defaultdict, Counter
from subprocess import run
from datetime import datetime
from random import shuffle
from itertools import count
import numpy as np
import csv

class QCCorpusViewer:

    def __init__(self, corpus):
        self.corpus = corpus
        self.log = get_logger(__name__, self.corpus.settings['logs_dir'], self.corpus.settings.get('debug'))

    def list_codes(self, expanded=False, depth=None):
        "Prints all the codes in the codebook"
        code_tree = self.corpus.get_codebook()
        if expanded:
            for code in code_tree.flatten(names=True, expanded=expanded, depth=depth):
                print(code)
        else:
            print(code_tree.__str__(max_depth=depth))


    def show_stats(self, codes, 
        max_count=None, 
        min_count=None, 
        depth=None, 
        recursive_codes=False,
        recursive_counts=False,
        unit='line',
        expanded=False, 
        format=None,
        pattern=None,
        file_list=None,
        invert=False,
        coder=None,
        outfile=None,
        total_only=False,
    ):
        """
        Displays statistics about how codes are used.
        """
        if pattern:
            self.report_files_matching_pattern(
                pattern=pattern, 
                file_list=file_list, 
                invert=invert
            ) 
        tree = self.corpus.get_code_tree_with_counts(
            pattern=pattern, 
            file_list=file_list,
            invert=invert, 
            coder=coder, 
            unit=unit, 
        )
        if codes:
            nodes = sum([tree.find(c) for c in codes], [])
            if recursive_codes:
                nodes = set(sum([n.flatten(depth=depth) for n in nodes], []))
        else:
            nodes = tree.flatten(depth=depth)
        if max_count:
            nodes = filter(lambda n: n.total <= max_count, nodes)
        if min_count:
            nodes = filter(lambda n: n.total >= min_count, nodes)
        nodes = sorted(nodes)

        def namer(node):
            if expanded:
                return node.expanded_name()
            elif recursive_codes and not outfile:
                return node.indented_name(nodes)
            else:
                return node.name

        if recursive_counts:
            if total_only:
                cols = ["Code", "Total"]
                results = [(namer(n), n.total) for n in nodes]
            else:
                cols = ["Code", "Count", "Total"]
                results = [(namer(n), n.count, n.total) for n in nodes]
        else:
            cols = ["Code", "Count"]
            results = [(namer(n), n.count) for n in nodes]

        if outfile:
            with open(outfile, 'w') as fh:
                writer = csv.writer(fh)
                writer.writerow(cols)
                writer.writerows(results)
        else:
            print(tabulate(results, cols, tablefmt=format))

    def crosstab(self, codes, 
        recursive_codes=False,
        recursive_counts=False,
        depth=None, 
        unit='line',
        pattern=None,
        file_list=None,
        invert=False,
        coder=None,
        probs=False,
        expanded=False, 
        compact=False,
        outfile=None,
        format=None,
    ):
        labels, matrix = self.corpus.get_code_matrix(
            codes, 
            recursive_codes=recursive_codes,
            recursive_counts=recursive_counts,
            depth=depth, 
            unit=unit,
            pattern=pattern,
            file_list=file_list,
            invert=invert,
            coder=coder,
            expanded=expanded,
        )
        m = frequencies = matrix.T @ matrix
        if probs:
            totals = np.diag(m).reshape((-1, 1))
            m = m / totals
        if compact:
            data = [[ix, code, *row] for ix, code, row in zip(count(), labels, m)]
            cols = ["ix", "code", *range(len(labels))]
        else:
            data = [[code, *row] for code, row in zip(labels, m)]
            cols = ["code", *labels]
        if outfile:
            with open(outfile, 'w') as fh:
                writer = csv.writer(fh)
                writer.writerow(cols)
                writer.writerows(data)
        else:
            index_cols = 2 if compact else 1
            data = self.mask_lower_triangle(data, index_cols)
            print(tabulate(data, cols, tablefmt=format, stralign="right"))

    def mask_lower_triangle(self, data, num_index_cols):
        "Replaces values in the lower triangle of a 2d Python list with ''"
        def mask(v, i, j):
            should_mask = i >= num_index_cols and i - num_index_cols < j
            return '' if should_mask else v
        return [[mask(v, i, j) for i, v in enumerate(row)] for j, row in enumerate(data)]

    def tidy_codes(self, codes, 
        recursive_codes=False,
        recursive_counts=False,
        depth=None, 
        unit='line',
        pattern=None,
        file_list=None,
        invert=False,
        coder=None,
        expanded=False, 
        outfile=None,
        format=None,
        minimum=None,
        maximum=None,
    ):
        """Returns a tidy table containing one row for each combination of codes.
        """
        labels, matrix = self.corpus.get_code_matrix(
            codes, 
            recursive_codes=recursive_codes,
            recursive_counts=recursive_counts,
            depth=depth, 
            unit=unit,
            pattern=pattern,
            file_list=file_list,
            invert=invert,
            coder=coder,
            expanded=expanded,
        )
        counts = Counter(map(tuple, matrix))
        valid = lambda c: (minimum is None or c >= minimum) and (maximum is None or c <= maximum)
        data = [(count, *values) for values, count in counts.items() if valid(count)]
        cols = ("count", *labels)

        if outfile:
            with open(outfile, 'w') as fh:
                writer = csv.writer(fh)
                writer.writerow(cols)
                writer.writerows(data)
        else:
            print(tabulate(data, cols, tablefmt=format))

    def report_files_matching_pattern(self, pattern, file_list=None, invert=False):
        print("From files:")
        for f in sorted(self.corpus.iter_corpus(pattern=pattern, file_list=file_list, invert=invert)):
            print("- {}".format(f.relative_to(self.corpus.corpus_dir)))
    
    def get_child_nodes(self, code, names=False, expanded=False, depth=None):
        "Finds all children of the given code (which may occur multiple times in the code tree)"
        code_tree = self.corpus.get_codebook()
        matches = code_tree.find(code)
        return sum([m.flatten(names=names, expanded=expanded, depth=depth) for m in matches], [])

    def show_coded_text(self, codes, 
            recursive_codes=False, 
            depth=None,
            unit="line",
            before=2, 
            after=2, 
            textwidth=80, 
            coder=None,
            pattern=None,
            file_list=None,
            invert=False,
            show_codes=True,
        ):
        "Search through all text files and show all text matching the codes"
        if recursive_codes:
            codes = set(sum([self.get_child_nodes(code, names=True) for code in codes], []))
        else:
            codes = set(codes)

        if show_codes:
            print("Showing results for codes: ", ", ".join(sorted(codes)))
        if pattern and unit == "line":
            self.report_files_matching_pattern(pattern, file_list=file_list, invert=invert)
        
        for corpus_file in self.corpus.iter_corpus(pattern=pattern, file_list=file_list, invert=invert):
            cf = corpus_file.relative_to(self.corpus.corpus_dir)
            if unit == "document":
                doc_codes = self.corpus.get_codes(corpus_file, coder=coder, merge=True, unit='document')
                if len(doc_codes & codes):
                    if show_codes:
                        template = "{:<" + str(textwidth) + "}| {}"
                        print(template.format(str(cf), ", ".join(sorted(doc_codes & codes))))
                    else:
                        print(cf)
            elif unit == "line":
                corpusCodes = defaultdict(set)
                for line_num, code in self.corpus.get_codes(corpus_file, coder=coder, merge=True, unit='line'):
                    corpusCodes[line_num].add(code)
                matchingLines = [i for i, lineCodes in corpusCodes.items() if len(lineCodes & codes)]
                with open(corpus_file) as f:
                    lines = list(f)
                ranges = merge_ranges([range(n-before, n+after+1) for n in matchingLines], clamp=[0, len(lines)])
                if len(ranges) > 0:
                    print("\n{} ({})".format(cf, len(matchingLines)))
                    print("=" * textwidth)
                    for r in ranges:
                        print("\n[{}:{}]".format(r.start, r.stop))
                        if show_codes:
                            for i in r:
                                print(
                                    lines[i].strip()[:textwidth].ljust(textwidth) + 
                                    " | " + ", ".join(sorted(corpusCodes[i]))
                                )
                        else:
                            print(" ".join(lines[i].strip() for i in r))
            else:
                raise NotImplementedError("Unit must be 'line' or 'document'.")
            
    def open_for_coding(self, pattern=None, file_list=None, invert=None, coder=None, choice=None):
        if coder is None:
            raise ValueError("Coder is required")
        corpus_files = sorted(list(self.corpus.iter_corpus(pattern=pattern, file_list=file_list, invert=invert)))
        if not any(corpus_files):
            raise ValueError("No corpus files matched.")
        if len(corpus_files) == 1:
            f = corpus_files[0]
        else:
            if choice is not None:
                if choice == 'first':
                    files_to_search = corpus_files
                elif choice == 'random':
                    shuffle(corpus_files)
                    files_to_search = corpus_files
                else:
                    raise ValueError("Choice argument must be 'first' or 'random'")
                f = None
                for cf in files_to_search:
                    if len(self.corpus.get_codes(cf, coder=coder)) == 0:
                        f = cf
                        break 
                if f is None:
                    raise ValueError(f"All {len(corpus_files)} matching files have codes")
            else:
                story_index = prompt_for_choice("Multiple files matched:", 
                        [f.relative_to(self.corpus.corpus_dir) for f in corpus_files])
                f = corpus_files[story_index]
        code_file = self.corpus.get_code_file_path(f, coder)
        self.log.debug(f"{coder} opened {f} for coding")
        self.open_editor([f, code_file])

    def memo(self, coder, message=""):
        "Opens a memo file for coding"
        fname = datetime.now().strftime("%Y-%m-%d-%H-%M") + '_' + coder
        if message:
            fname += "_" + message.replace(" ", "_").lower()
        fname += ".md"
        path = self.corpus.memos_dir / fname
        if message:
            path.write_text(f"# {message}\n\n{coder} {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        else:
            path.write_text(f"# Memo by {coder} on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n") 
        self.log.info(f"{coder} wrote memo {message}")
        self.open_editor(path)

    def list_memos(self):
        "Concatenates all memo text"
        text = [f.read_text() for f in sorted(self.corpus.memos_dir.glob("*.md"))]
        return "\n\n".join(text)

    def open_editor(self, files):
        if not (isinstance(files, list) or isinstance(files, tuple)):
            files = [files]
        run(["vim", "-O"] + files)



