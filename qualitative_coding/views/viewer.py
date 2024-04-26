from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.helpers import prompt_for_choice
from qualitative_coding.views.coding_ui import CodingUI
from qualitative_coding.exceptions import QCError, CodeFileParseError
from qualitative_coding.editors import editors
from tabulate import tabulate
from collections import defaultdict, Counter
from pathlib import Path
from subprocess import run, CalledProcessError
from datetime import datetime
from random import choice
from itertools import count
from textwrap import fill
import numpy as np
import csv
import yaml
import json
import re

class QCCorpusViewer:

    codes_file = "codes.txt"
    coding_session_metadata_file = ".coding_session"
    code_pattern = "[a-zA-Z0-9_\-]"

    def __init__(self, corpus):
        self.corpus = corpus
        self.settings = self.corpus.settings
        self.log = self.corpus.log

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
        coders=None,
        by_coder=False,
        by_document=False,
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
                coders=coders, 
                unit=unit, 
            )
        if codes:
            nodes = sum([tree.find(c) for c in codes], [])
            if recursive_codes:
                nodes = set(sum([n.flatten(depth=depth) for n in nodes], []))
        else:
            nodes = tree.flatten(depth=depth)
        if max_count != None:
            nodes = filter(lambda n: n.total <= max_count, nodes)
        if min_count != None:
            nodes = filter(lambda n: n.total >= min_count, nodes)
        if not zeros:
            nodes = filter(lambda n: n.total > 0, nodes)
        nodes = sorted(nodes)

        def namer(node):
            if expanded:
                return node.expanded_name()
            elif recursive_codes and not outfile:
                return node.indented_name(nodes)
            else:
                return node.name

        if by_coder:
            with self.corpus.session():
                totals_by_coder = self.corpus.count_codes_by_coder(
                    codes=codes, 
                    coders=coders,
                    recursive_codes=recursive_codes, 
                    depth=depth,
                    pattern=pattern,
                    file_list=file_list,
                    unit=unit,
                    totals=recursive_counts,
                )
                if coders:
                    all_coders = sorted(coders)
                else:
                    all_coders = sorted(c.name for c in self.corpus.get_all_coders())
                cols = all_coders + ["Total"]
                results = []
                for n in nodes:
                    row = []
                    for coder in all_coders:
                        row.append(totals_by_coder[coder][n.expanded_name()])
                    row.append(sum(row))
                    results.append([namer(n)] + row)
        elif by_document:
            with self.corpus.session():
                totals_by_doc = self.corpus.count_codes_by_document(
                    codes=codes, 
                    coders=coders,
                    recursive_codes=recursive_codes, 
                    depth=depth,
                    pattern=pattern,
                    file_list=file_list,
                    unit=unit,
                    totals=recursive_counts,
                )
                all_docs = self.corpus.get_documents(pattern=pattern, file_list=file_list)
                all_docs = sorted(d.file_path for d in all_docs)
                cols = all_docs + ["Total"]
                results = []
                for n in nodes:
                    row = []
                    for doc in all_docs:
                        row.append(totals_by_doc[doc][n.expanded_name()])
                    row.append(sum(row))
                    results.append([namer(n)] + row)
        else:
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

    def show_document_coders_pivot_table(self, 
        codes=None,
        recursive=False,
        format=None,
        pattern=None,
        file_list=None,
        coders=None,
        unit='line',
        outfile=None,
    ):
        """Shows a table where each row is a document and each column
        is a coder.
        """
        with self.corpus.session():
            if unit == 'line':
                lines = self.corpus.get_coded_lines(
                    codes=codes, 
                    pattern=pattern,
                    file_list=file_list,
                    coders=coders,
                )
                units = [(doc, coder) for _, coder, _, doc in lines]
            elif unit == 'paragraph':
                paragraphs = self.corpus.get_coded_paragraphs(
                    codes=codes, 
                    pattern=pattern,
                    file_list=file_list,
                    coders=coders,
                )
                units = [(doc, coder) for _, coder, _, doc, _, _, _ in paragraphs]
            elif unit == 'document':
                docs = self.corpus.get_coded_paragraphs(
                    codes=codes, 
                    pattern=pattern,
                    file_list=file_list,
                    coders=coders,
                )
                units = [(doc, coder) for _, coder, doc in docs]
        matrix = defaultdict(lambda: defaultdict(int))
        for doc, coder in units:
            matrix[doc][coder] += 1
        doc_index = sorted(matrix.keys())
        coder_index = set()
        for row in matrix.values():
            for coder in row.keys():
                coder_index.add(coder)
        coder_index = sorted(coder_index)
        cols = ["Document"] + coder_index + ["Total"]
        results = []
        for doc in doc_index:
            row = [doc] + [matrix[doc][c] for c in coder_index] + [sum(matrix[doc].values())]
            results.append(row)
        totals = ["Total"] + [sum(col) for col in zip(*[r[1:] for r in results])]
        results.append(totals)
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
        coders=None,
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
                coders=coders,
                expanded=expanded,
            )
        m = matrix
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
        coders=None,
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
            coders=coders,
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
            coders=None,
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
                        file_list=file_list, coders=coders)
            doc_coded_lines = defaultdict(lambda: defaultdict(set))
            doc_code_counts = defaultdict(int)
            for code, coder, line_num, doc_path in coded_lines:
                doc_code_counts[doc_path] += 1
                doc_coded_lines[doc_path][line_num].add(code)
            for doc_path, coded_lines in doc_coded_lines.items():
                with open(self.corpus.corpus_dir / doc_path) as fh:
                    lines = [line for line in fh]
                ranges = self.merge_ranges(
                    [range(n-before, n+after+1) for n in coded_lines.keys()], 
                    clamp=[0, len(lines)]
                )
                print(f"\n{doc_path} ({doc_code_counts[doc_path]})")
                print("=" * text_width)
                for r in ranges:
                    print("[{}:{}]".format(r.start, r.stop))
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
                    print("")
        elif unit == "paragraph":
            with self.corpus.session():
                coded_paragraphs = self.corpus.get_coded_paragraphs(codes=codes, 
                        pattern=pattern, file_list=file_list, coders=coders)
            doc_coded_paras = defaultdict(lambda: defaultdict(set))
            for code, coder, doc_path, para_start, para_end in coded_paragraphs:
                doc_coded_paras[doc_path][(para_start, para_end)].add(code)
            for doc_path, coded_paras in doc_coded_paras.items():
                with open(self.corpus.corpus_dir / doc_path) as fh:
                    lines = [line for line in fh]
                para_code_count = sum(len(code_set) for code_set in coded_paras.values())
                print(f"\n{doc_path} ({para_code_count})")
                print("=" * text_width)
                for (para_start, para_end), codes in coded_paras.items():
                    r = range(para_start, para_end)
                    print("[{}:{}]".format(r.start, r.stop))
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
            with self.corpus.session():
                coded_documents = self.corpus.get_coded_documents(codes=codes, 
                        pattern=pattern, file_list=file_list, coders=coders)
            doc_codes = defaultdict(set)
            for code, coder, doc_path in coded_documents:
                doc_codes[doc_path].add(code)
            if show_codes:
                self.show_text_with_codes(
                    doc_codes.keys(),
                    doc_codes.values(),
                    text_width=max(len(d) for d in doc_codes.keys()) + 1,
                )
            else:
                for doc_path in doc_codes.keys():
                    print(doc_path)

    def show_coded_text_json(self, codes, 
            recursive_codes=False, 
            depth=None,
            unit="line",
            before=2, 
            after=2, 
            text_width=80, 
            coders=None,
            pattern=None,
            file_list=None,
            show_codes=True,
        ):
        """Displays json with lines from corpus documents with their codes.
        """
        records = self.get_coded_text_json(codes, 
            recursive_codes=recursive_codes, 
            depth=depth,
            unit=unit,
            before=before, 
            after=after, 
            text_width=text_width, 
            coders=coders,
            pattern=pattern,
            file_list=file_list,
        )
        print(json.dumps(records))

    def get_coded_text_json(self, codes, 
            recursive_codes=False, 
            depth=None,
            unit="line",
            before=2, 
            after=2, 
            text_width=80, 
            coders=None,
            pattern=None,
            file_list=None,
        ):
        """Gets json with lines from corpus documents with their codes.
        """
        if recursive_codes:
            codes = set(sum([self.get_child_nodes(code, names=True) for code in codes], []))
        else:
            codes = set(codes)
        records = []
        if unit == "line": 
            with self.corpus.session():
                coded_lines = self.corpus.get_coded_lines(codes=codes, pattern=pattern, 
                        file_list=file_list, coders=coders)
            doc_coded_lines = defaultdict(lambda: defaultdict(set))
            doc_code_counts = defaultdict(int)
            for code, coder, line_num, doc_path in coded_lines:
                doc_code_counts[doc_path] += 1
                doc_coded_lines[doc_path][line_num].add(code)
            for doc_path, coded_lines in doc_coded_lines.items():
                with open(self.corpus.corpus_dir / doc_path) as fh:
                    lines = [line for line in fh]
                for line, codes in coded_lines.items():
                    for code in codes:
                        line_start = max(0, line - before)
                        line_end = min(len(lines), line + after + 1)
                        records.append({
                            "document": doc_path,
                            "line": line,
                            "code": code,
                            "text_lines": [line_start, line_end],
                            "text": ''.join(lines[line_start:line_end])
                        })
        elif unit == "paragraph":
            with self.corpus.session():
                coded_paragraphs = self.corpus.get_coded_paragraphs(codes=codes, 
                        pattern=pattern, file_list=file_list, coders=coders)
            doc_coded_paras = defaultdict(lambda: defaultdict(set))
            for code, coder, doc_path, para_start, para_end in coded_paragraphs:
                doc_coded_paras[doc_path][(para_start, para_end)].add(code)
            for doc_path, coded_paras in doc_coded_paras.items():
                with open(self.corpus.corpus_dir / doc_path) as fh:
                    lines = [line for line in fh]
                for (para_start, para_end), codes in coded_paras.items():
                    for code in codes:
                        records.append({
                            "document": doc_path,
                            "paragraph": [para_start, para_end],
                            "code": code,
                            "text": ''.join(lines[para_start:para_end]),
                        })
        elif unit == "document": 
            with self.corpus.session():
                coded_documents = self.corpus.get_coded_documents(codes=codes, 
                        pattern=pattern, file_list=file_list, coders=coders)
            doc_codes = defaultdict(set)
            for code, coder, doc_path in coded_documents:
                records.append({
                    "docuement": doc_path,
                    "code": code,
                })
        return records

    def show_text(self, lines, text_width=80):
        "Prints lines of text from a corpus document"
        for line in lines:
            print(line.strip()[:text_width])

    def show_text_with_codes(self, lines, code_sets, text_width=80, code_width=80):
        "Prints text lines with associated codes"
        sep = " | "
        for line, code_set in zip(lines, code_sets):
            text = line.strip()[:text_width].ljust(text_width)
            if code_set:
                print(fill(
                    ", ".join(sorted(code_set)),
                    initial_indent=text + sep,
                    subsequent_indent=" " * text_width + sep,
                    width=text_width + len(sep) + code_width, 
                ))
            else:
                print(text + sep)
            
    def select_file(self, coder, pattern=None, file_list=None, uncoded=False, 
            first=False, random=False):
        """Selects a single file from the corpus.
        Pattern, file_list, and invert are optionally used to filter the corpus.
        If uncoded, filters out previously-coded files.
        Then, returns returns a random matching file if random,
        the first matching file if first, and otherwise prompts to choose a matching file.
        """
        if first and random:
            raise ValueError("First and random must not both be True")
        with self.corpus.session():
            docs = self.corpus.get_documents(pattern=pattern, file_list=file_list)
            file_paths = set(doc.file_path for doc in docs)
            if uncoded:
                coded_docs = self.corpus.get_coded_documents(pattern=pattern,
                        file_list=file_list, coder=coder)
                coded_file_paths = set(fp for code, coder, fp in coded_docs)
                file_paths = file_paths - coded_file_paths
            file_paths = sorted(file_paths)
        if len(file_paths) == 0:
            raise QCError("No corpus files matched.")
        elif len(file_paths) == 1:
            return file_paths[0]
        else:
            if first:
                return file_paths[0]
            elif random:
                return choice(file_paths)
            else:
                ix = self.prompt_for_choice("Multiple files matched:", file_paths)
                return file_paths[ix]

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
        with self.corpus.session():
            self.corpus.get_or_create_coder(coder)
            command = self.get_memo_command(path)
            run(command, check=True, shell=True)

    def list_memos(self):
        "Concatenates all memo text"
        text = [f.read_text() for f in sorted(self.corpus.memos_dir.glob("*.md"))]
        return "\n\n".join(text)

    def open_editor(self, corpus_file_path, coder_name):
        codes_file_path = self.corpus.resolve_path(self.codes_file)
        full_path = self.corpus.corpus_dir / corpus_file_path
        codes_file_path.write_text(self.codes_file_text(corpus_file_path, coder_name))
        command = self.get_code_command(full_path, codes_file_path)
        try:
            p = run(command, shell=True, check=True)
            corpus_file_length = len(full_path.read_text().splitlines())
            coded_lines = self.parse_codes(codes_file_path.read_text(), corpus_file_length)
        except CalledProcessError as err:
            self.save_incomplete_coding_session(corpus_file_path, coder_name)
            raise QCError(
                "The editor closed before coding was complete" + 
                (f":\n{err.stderr}\n" if err.stderr else '') + 
                "Run qc code --recover to recover this coding session or " + 
                "qc code --abandon to abandon it."
            )

        with self.corpus.session():
            document = self.corpus.get_document(corpus_file_path)
            self.corpus.update_coded_lines(document, coder_name, coded_lines)
        codes_file_path.unlink()
        metadata_file_path = self.corpus.resolve_path(self.coding_session_metadata_file)
        if metadata_file_path.exists():
            metadata_file_path.unlink()

    def parse_codes(self, code_file_text, expected_length):
        """Parses the contents of a code file after user editing. 
        If successful, returns coded_lines, a list of {line: int, code_id: str}
        Raises CodeFileParseError if there is an error parsing the file.
        """
        code_file_lines = code_file_text.splitlines()
        if len(code_file_lines) != expected_length:
            raise CodeFileParseError(
                "Expected the codes file to have the same number of lines as the document " + 
                f"being coded ({expected_length}), but it has {len(code_file_lines)}."
            )
        coded_lines = []
        for idx, line in enumerate(code_file_lines):
            if line.strip() == '':
                continue
            codes = [self.parse_code(x) for x in line.split(',')]
            for code in codes:
                if code.strip() != "":
                    coded_lines.append({
                        "line": idx,
                        "code_id": code
                    })
        return coded_lines

    def parse_code(self, text):
        """Parses an individual code from a codes file.
        Codes 
        """
        text = text.strip()
        if not re.match(self.code_pattern, text):
            raise CodeFileParseError(f"{text} is not a valid code.")
        return text 

    def incomplete_coding_session_exists(self):
        metadata_file_path = self.corpus.resolve_path(self.coding_session_metadata_file)
        return metadata_file_path.exists()

    def abandon_incomplete_coding_session(self):
        if not incomplete_coding_session_exists():
            raise QCError("There is no incomplete coding session.")
        codes_file_path = self.corpus.resolve_path(self.codes_file)
        metadata_file_path = self.corpus.resolve_path(self.coding_session_metadata_file)
        if codes_file_path.exists():
            codes_file_path.unlink()
        if metadata_file_path.exists():
            metadata_file_path.unlink()

    def save_incomplete_coding_session(self, corpus_file_path, coder_name):
        metadata_file_path = self.corpus.resolve_path(self.coding_session_metadata_file)
        metadata_file_path.write_text(yaml.dump({
            'corpus_file_path': corpus_file_path,
            'coder_name': coder_name,
        }))

    def recover_incomplete_coding_session(self):
        if not self.incomplete_coding_session_exists():
            raise QCError("There is no incomplete coding session.")
        codes_file_path = self.corpus.resolve_path(self.codes_file)
        metadata_file_path = self.corpus.resolve_path(self.coding_session_metadata_file)
        if not codes_file_path.exists():
            raise QCError(
                "The coding file, {self.codes_file}, no longer exists. " + 
                "If you can recover {self.codes_file}, run qc code --recover " +
                "to recover it. Otherwise, run qc code --abandon to abandon " +
                "the existing session."
            )
        metadata = yaml.safe_load(metadata_file_path.read_text())
        self.open_editor(**metadata)

    def codes_file_text(self, corpus_file_path, coder):
        """Formats codes for a temporary coding file.
        """
        with self.corpus.session():
            code_line_docs = self.corpus.get_coded_lines(
                file_list=[corpus_file_path], 
                coders=[coder]
            )
        codes_per_line = defaultdict(list)
        for code, coder, line, doc in code_line_docs:
            codes_per_line[line].append(code)

        text = (self.corpus.corpus_dir / corpus_file_path).read_text().splitlines()
        lines = [', '.join(codes_per_line[i]) for i in range(len(text))]
        return '\n'.join(lines) + '\n'

    def get_code_command(self, corpus_file_path, codes_file_path):
        """Returns a shell command to open an editor for coding.
        settings['editor'] should be a key in qualitative_coding.editors.editors, 
        or in the user-specified list of editors. (This is checked during validation.)

        Users can define additional editors in settings.yaml, under the editors key. 
        name, code_command, and memo_command should be specified, using the placeholders
        {codes_file_path}, {corpus_file_path}, and {memo_file_path}.
        For example:

            ...
            editor: vim_with_linenums
            editors:
                vim_with_linenums:
                    name: Vim
                    code_command: 'vim "{codes_file_path}" -c :set nu -c :set scrollbind -c :83vsplit|view {corpus_file_path}|set scrollbind',
                    "memo_command": 'vim "{memo_file_path}',
        """
        all_editors = {**editors, **self.settings.get('editors', {})}
        cmd = all_editors[self.settings['editor']]['code_command']
        return cmd.format(corpus_file_path=corpus_file_path, codes_file_path=codes_file_path)

    def get_memo_command(self, memo_file_path):
        """Returns a shell command to open an editor for memo-writing.
        """
        all_editors = {**editors, **self.settings.get('editors', {})}
        cmd = all_editors[self.settings['editor']]['memo_command']
        return cmd.format(memo_file_path=memo_file_path)

    def prompt_for_choice(self, prompt, options):
        "Asks for a prompt, returns an index"
        print(prompt)
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        while True:
            raw_choice = input("> ")
            if raw_choice.isdigit() and int(raw_choice) in range(1, len(options)+1):
                return int(raw_choice) - 1
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
