# Qualitative Coding corpus viewer
# --------------------------------
# (c) 2019 Chris Proctor

# TODO: Use dataframes instead of tabulate. 
# - provide an option for exporting as df
# - Provide support for lines longer than 80. Should 
# - wrap in view, but still count accurately.

from qualitative_coding.tree_node import TreeNode
from qualitative_coding.helpers import merge_ranges
from tabulate import tabulate
from collections import defaultdict

class QCCorpusViewer:

    def __init__(self, corpus):
        self.corpus = corpus

    def list_codes(self, expanded=False):
        "Prints all the codes in the codebook"
        code_tree = self.corpus.get_codebook()
        if expanded:
            for code in code_tree.flatten(names=True, expanded=True):
                print(code)
        else:
            print(code_tree)

    def show_stats(self, codes, 
        max_count=None, 
        min_count=None, 
        depth=None, 
        expanded=False, 
        format=None,
        filepattern=None
    ):
        """
        Displays statistics about how codes are used.
        """
        # Assign counts to nodes
        if filepattern:
            self.report_files_matching_pattern(filepattern) 
            
        counts = self.corpus.get_code_counts(pattern=filepattern)
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

# ====================================

    def report_files_matching_pattern(self, pattern):
        print("From files:")
        for f in self.corpus.iter_corpus(pattern=filepattern):
            print(f"- {f}")
    
    def get_child_nodes(self, code, names=False, expanded=False, depth=None):
        "Finds all children of the given code (which may occur multiple times in the code tree)"
        code_tree = self.corpus.get_codebook()
        matches = code_tree.find(code)
        return sum([m.flatten(names=names, expanded=expanded, depth=depth) for m in matches], [])

    def show_coded_text(self, codes, 
            before=2, 
            after=2, 
            recursive=False, 
            textonly=False, 
            textwidth=80, 
            coder=None,
            filepattern=None
        ):
        "Search through all text files and show all text matching the codes"
        if recursive:
            codes = set(sum([get_child_nodes(code, names=True) for code in codes], []))
        else:
            codes = set(codes)
        print("Showing results for codes: ", ", ".join(sorted(codes)))
        if filepattern:
            self.report_files_matching_pattern(filepattern)
        
        for corpus_file in self.corpus.iter_corpus(pattern=filepattern):
            corpusCodes = defaultdict(set)
            for line_num, code in self.corpus.get_codes(corpus_file, coder=coder, merge=True):
                corpusCodes[line_num].add(code)
            matchingLines = [i for i, lineCodes in corpusCodes.items() if any(lineCodes & codes)]
            with open(corpus_file) as f:
                lines = list(f)
            ranges = merge_ranges([range(n-before, n+after+1) for n in matchingLines], clamp=[0, len(lines)])
            if any(ranges):
                print("")
                print("{} ({})".format(corpus_file, len(matchingLines)))
                print("=" * textwidth)
            for r in ranges:
                print("")
                print("[{}:{}]".format(r.start, r.stop))
                if textonly:
                    print(" ".join(lines[i].strip() for i in r))
                else:
                    for i in r:
                        print(lines[i].strip()[:textwidth].ljust(textwidth) + 
                                " | " + ", ".join(sorted(corpusCodes[i])))
            
    def open_for_coding(self, text_path):
        "vim -O f1 f2"

