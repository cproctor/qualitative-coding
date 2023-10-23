# Qualitative Coding corpus viewer
# --------------------------------
# (c) 2019 Chris Proctor

from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.helpers import prompt_for_choice
from qualitative_coding.views.coding_ui import CodingUI
from qualitative_coding.exceptions import QCError
from tabulate import tabulate
from collections import defaultdict, Counter
from pathlib import Path
from subprocess import run
from datetime import datetime
from random import choice
from itertools import count
import numpy as np
import csv

class QCCorpusViewer:

    def __init__(self, corpus):
        self.corpus = corpus
        self.settings = self.corpus.settings
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
        coder=None,
        outfile=None,
        total_only=False,
        zeros=False,
    ):
        """
        Displays statistics about how codes are used.
        """
        if pattern:
            self.report_files_matching_pattern(
                pattern=pattern, 
                file_list=file_list
            ) 
        with self.corpus.session():
            tree = self.corpus.get_code_tree_with_counts(
                pattern=pattern, 
                file_list=file_list,
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
        if not zeros:
            nodes = filter(lambda n: n.count > 0, nodes)
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
        with self.corpus.session():
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
        m = matrix
        print(matrix)
        if probs:
            totals = np.diag(m).reshape((-1, 1))
            m = m / totals
            print(totals)
            print(m)
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
            if not probs:
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

    def report_files_matching_pattern(self, pattern, file_list=None):
        with self.corpus.session():
            docs = self.corpus.get_documents(pattern=pattern, file_list=file_list)
            file_paths = [doc.file_path for doc in docs]
        print("From files:")
        for fp in file_paths:
            print(f"- {fp}")
    
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
            text_width=80, 
            coder=None,
            pattern=None,
            file_list=None,
            show_codes=True,
        ):
        """Displays lines from corpus documents with their codes.
        """
        if recursive_codes:
            codes = set(sum([self.get_child_nodes(code, names=True) for code in codes], []))
        else:
            codes = set(codes)
        if unit == "line": 
            with self.corpus.session():
                coded_lines = self.corpus.get_coded_lines(codes=codes, pattern=pattern, 
                        file_list=file_list, coder=coder)
            doc_coded_lines = defaultdict(lambda: defaultdict(set))
            doc_code_counts = defaultdict(int)
            for code, line_num, doc_path in coded_lines:
                doc_code_counts[doc_path] += 1
                doc_coded_lines[doc_path][line_num].add(code)
            for doc_path, coded_lines in doc_coded_lines.items():
                with open(Path(self.settings['corpus_dir']) / doc_path) as fh:
                    lines = [line for line in fh]
                ranges = self.merge_ranges(
                    [range(n-before, n+after+1) for n in coded_lines.keys()], 
                    clamp=[0, len(lines)]
                )
                print(f"\n{doc_path} ({doc_code_counts[doc_path]})")
                print("=" * text_width)
                for r in ranges:
                    print("\n[{}:{}]".format(r.start, r.stop))
                    if show_codes:
                        self.show_text_with_codes(
                            [lines[i] for i in r],
                            [doc_coded_lines[doc_path][i] for i in r],
                            text_width=text_width,
                        )
                    else:
                        self.show_text(
                            [lines[i] for i in r],
                            text_width=text_width,
                        )
                        print(" ".join(lines[i].strip() for i in r))
        elif unit == "paragraph":
            with self.corpus.session():
                coded_paragraphs = self.corpus.get_coded_paragraphs(codes=codes, 
                        pattern=pattern, file_list=file_list, coder=coder)
            doc_coded_paras = defaultdict(lambda: defaultdict(set))
            doc_code_counts = defaultdict(int)
            for code, doc_path, para_start, para_end in coded_paragraphs:
                doc_code_counts[doc_path] += 1
                doc_coded_paras[doc_path][(para_start, para_end)].add(code)
            for doc_path, coded_paras in doc_coded_paras.items():
                with open(Path(self.settings['corpus_dir']) / doc_path) as fh:
                    lines = [line for line in fh]
                print(f"\n{doc_path} ({doc_code_counts[doc_path]})")
                print("=" * text_width)
                for (para_start, para_end), codes in coded_paras.items():
                    r = range(para_start, para_end)
                    print("\n[{}:{}]".format(r.start, r.stop))
                    if show_codes:
                        self.show_text_with_codes(
                            [lines[i] for i in r],
                            [codes] + [[] for i in range(para_end - para_start)],
                            text_width=text_width,
                        )
                    else:
                        self.show_text(
                            [lines[i] for i in r],
                            text_width=text_width,
                        )
                        print(" ".join(lines[i].strip() for i in r))
        elif unit == "document": 
            print("DOCUMENT")

    def show_text(self, lines, text_width=80):
        "Prints lines of text from a corpus document"
        for line in lines:
            print(line.strip()[:text_width])

    def show_text_with_codes(self, lines, code_sets, text_width=80, code_width=80):
        "Prints text lines with associated codes"
        for line, code_set in zip(lines, code_sets):
            print(
                line.strip()[:text_width].ljust(text_width) + 
                " | " + ", ".join(sorted(code_set))
            )
            
    def select_file(self, coder, pattern=None, file_list=None, invert=None, uncoded=False, 
            first=False, random=False):
        """Selects a single file from the corpus.
        Pattern, file_list, and invert are optionally used to filter the corpus.
        If uncoded, filters out previously-coded files.
        Then, returns returns a random matching file if random,
        the first matching file if first, and otherwise prompts to choose a matching file.
        """
        if first and random:
            raise ValueError("First and random must not both be True")
        corpus_files = sorted(list(self.corpus.iter_corpus(pattern=pattern, 
                file_list=file_list, invert=invert)))
        if uncoded:
            corpus_files = [cf for cf in corpus_files if self.corpus.is_coded(cf, coder)]
        if len(corpus_files) == 0:
            raise QCError("No corpus files matched.")
        elif len(corpus_files) == 1:
            return corpus_files[0]
        else:
            if first:
                return corpus_files[0]
            elif random:
                return choice(corpus_files)
            else:
                ix = self.prompt_for_choice("Multiple files matched:", 
                        [f.relative_to(self.corpus.corpus_dir) for f in corpus_files])
                return corpus_files[ix]

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
        run(f"{self.settings['editor']} {path}", check=True, shell=True)

    def list_memos(self):
        "Concatenates all memo text"
        text = [f.read_text() for f in sorted(self.corpus.memos_dir.glob("*.md"))]
        return "\n\n".join(text)

    def open_editor(self, files):
        corpus_file, codes_file = files
        text = Path(corpus_file).read_text().splitlines()
        if Path(codes_file).exists():
            codes = Path(codes_file).read_text().splitlines()
        else:
            codes = ["" for line in text]
        codebook = []
        ui = CodingUI(text, codes, codebook)
        ui.run()

        #if not (isinstance(files, list) or isinstance(files, tuple)):
            #files = [files]
        #run(["vim", "-O"] + files)

    def prompt_for_choice(self, prompt, options):
        "Asks for a prompt, returns an index"
        print(prompt)
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        while True:
            raw_choice = input("> ")
            if raw_choice.isdigit() and int(raw_choice) in range(1, len(options)+1):
                return int(raw_choice)
            print("Sorry, that's not a valid choice.")

    def merge_ranges(self, ranges, clamp=None):
        "Overlapping ranges? Let's fix that. Optionally supply clamp=[0, 100]"
        if any(filter(lambda r: r.step != 1, ranges)): 
            raise ValueError("Ranges must have step=1")
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



