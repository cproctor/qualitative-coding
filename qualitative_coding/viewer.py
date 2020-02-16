# Qualitative Coding corpus viewer
# --------------------------------
# (c) 2019 Chris Proctor

# TODO: Use dataframes instead of tabulate. 
# - provide an option for exporting as df
# - Provide support for lines longer than 80. Should 
# - wrap in view, but still count accurately.

from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.helpers import merge_ranges, prompt_for_choice
from tabulate import tabulate
from collections import defaultdict
from subprocess import run
from datetime import datetime
from random import shuffle

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
        expanded=False, 
        format=None,
        file_pattern=None,
        file_list=None,
        invert_files=False,
        unit='line',
    ):
        """
        Displays statistics about how codes are used.
        """
        # Assign counts to nodes
        if file_pattern:
            self.report_files_matching_pattern(file_pattern, file_list=file_list, invert=invert_files) 
            
        counts = self.corpus.get_code_counts(pattern=file_pattern, file_list=file_list, 
                invert=invert_files, unit=unit)
        rootNode = self.corpus.get_codebook()
        for node in rootNode.flatten():
            node.count = counts[node.name]

        # Filter nodes to show
        if codes:
            matches = sum([rootNode.find(c) for c in codes], [])
            nodes = set(sum([m.flatten(depth=depth) for m in matches], []))
        else:
            nodes = rootNode.flatten(depth=depth)
        if max_count:
            nodes = filter(lambda n: n.sum("count") <= max_count, nodes)
        if min_count:
            nodes = filter(lambda n: n.sum("count") >= min_count, nodes)
        nodes = sorted(nodes)

        # Format for display
        if expanded:
            results = [(n.expanded_name(), n.sum("count")) for n in nodes]
        else:
            results = []
            for n in nodes:
                ancestorTraversal = n.parent.backtrack_to(nodes)
                if ancestorTraversal is None: # This node goes all the way back to root
                    formattedName = ":".join(n.name for n in n.ancestors())
                else: 
                    ancestorDepth = n.depth() - len(ancestorTraversal) - 1
                    formattedName = '.' + "  " * ancestorDepth + ":".join(a.name for a in ancestorTraversal+[n])
                results.append((formattedName,  n.sum("count")))
        print(tabulate(results, ["Code", "Count"], tablefmt=format))

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
            recursive=False, 
            depth=None,
            unit="line",
            before=2, 
            after=2, 
            textwidth=80, 
            coder=None,
            file_pattern=None,
            file_list=None,
            invert=False,
            show_codes=True,
        ):
        "Search through all text files and show all text matching the codes"
        if recursive:
            codes = set(sum([self.get_child_nodes(code, names=True) for code in codes], []))
        else:
            codes = set(codes)

        if show_codes:
            print("Showing results for codes: ", ", ".join(sorted(codes)))
        if file_pattern and unit == "line":
            self.report_files_matching_pattern(file_pattern, file_list=file_list, invert=invert)
        
        for corpus_file in self.corpus.iter_corpus(pattern=file_pattern, file_list=file_list, invert=invert):
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



