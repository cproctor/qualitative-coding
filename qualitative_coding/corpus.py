# Qualitative Coding corpus
# -------------------------
# (c) 2019 Chris Proctor

# Expects codes files to be named something like [^\.]+(\.[^\.]+)?\.txt
# Corpus and codes are separated because maybe you want to keep your raw data
# and your analysis separate.

# Decided not to make a separate codebook because the codebook and the codes are tightly bound.

# TODO
# - add logging
# ensure uniqueness of corpus text paths

from itertools import chain
from collections import defaultdict
from pathlib import Path
import yaml
from qualitative_coding.tree_node import TreeNode


DEFAULT_SETTINGS = {
    'corpus_dir': 'corpus',
    'codes_dir': 'codes',
    'codebook': 'codebook.yaml',
    'log_file': 'qc.log',
}

class QCCorpus:
    
    @classmethod
    def initialize(cls, settings_file):
        if not Path(settings_file).exists():
            Path(settings_file).write_text(yaml.dump(DEFUALT_SETTINGS))
        settings = yaml.load(Path(settings_file).read_text())
        codebook_path = Path(settings['codebook'])
        if not codebook_path.is_absolute():
            codebook_path = Path(settings_file).parent / codebook_path
        if not codebook_path.exists:
            codebook_path.write_text("")
            
    def __init__(self, settings_file="settings.yaml"):
        """
        We need the actual settings file instead of just settings because it also
        provides a default (portable) working directory for relative links
        """
        self.settings_file = settings_file
        self.settings = yaml.load(Path(settings_file).read_text())

        for attr, is_dir in (('corpus_dir', True), ('codes_dir', True), ('codebook', False)):
            p = Path(self.settings[attr])
            if p.is_absolute():
                setattr(self, attr, p)
            else:
                setattr(self, attr, (Path(settings_file).resolve().parent / p).resolve())
            if not getattr(self, attr).exists():
                raise ValueError("settings['{}'] ({}) does not exist".format(attr, getattr(self, attr)))
            if is_dir and not getattr(self, attr).is_dir():
                raise ValueError("settings['{}'] ({}) is not a directory".format(attr, getattr(self, attr)))

    def initialize_codefiles(self, coder):
        "For/each text in corpus, creates a blank file of equivalent length"

    def iter_corpus(self, pattern=None):
        "Iterates over files in the corpus"
        if pattern:
            glob = '*' + pattern + '*.txt'
        else:
            glob = '*.txt'
        for f in Path(self.corpus_dir).rglob(glob):
            yield f

    def iter_corpus_codes(self, pattern=None, coder=None, merge=False):
        "Iterates over (f, codes) for code files"
        for f in self.iter_corpus(pattern):
            yield f, self.get_codes(f, coder=coder, merge=merge)

    def iter_code_files(self, coder=None):
        "Iterates over all files containing codes, optionally filtered by coder"
        pattern = f"*.{coder}.codes" if coder else "*.codes"
        for f in self.codes_dir.glob(pattern):
            yield f

    def get_code_files_for_corpus_file(self, corpus_text_path, coder=None):
        "Returns an iterator over code files pertaining to a corpus file"
        text_path = corpus_text_path.relative_to(self.corpus_dir)
        name_parts = text_path.name.split('.')
        return self.codes_dir.glob(str(text_path) + '.' + (coder or '*') + '.codes')

    def get_codes(self, corpus_text_path, coder=None, merge=False):
        """
        Returns codes pertaining to a corpus text.
        Returns a dict like {coder_id: [(line_num, code)...]}. 
        If merge or coder, there is no ambiguity;instead returns a list of [(line_num, code)...]
        """
        codes = {}
        for f in self.get_code_files_for_corpus_file(corpus_text_path, coder=coder):
            codes[self.get_coder_from_code_path(f)] = self.read_codes(f)
        if coder or merge:
            return sum(codes.values(), [])
        else:
            return codes

    def write_codes(self, corpus_text_path, coder, codes):
        "Writes a list of (line_num, code) to file"
        with open(corpus_text_path) as f:
            file_len = len(list(f))
        lines = defaultdict(list)
        for line_num, code in codes:
            lines[line_num] += [code]
        text_path = corpus_text_path.relative_to(self.corpus_dir)
        codes_path = Path(str(self.codes_dir / text_path) + '.' + coder + '.codes')
        codes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(codes_path, 'w') as outf:
            for line_num in range(file_len):
                outf.write(", ".join(lines[line_num]) + "\n")

    def read_codes(self, code_file_path):
        "When passed a file object, returns a list of (line_num, code)"
        codes = []
        with open(code_file_path) as inf:
            for line_num, line in enumerate(inf):
                codes += [(line_num, code.strip()) for code in line.split(",") if code.strip()]
        return codes

    def get_all_codes(self, pattern=None, coder=None):
        "Returns a list of all unique codes used in the corpus"
        all_codes = set()
        for f, codes in self.iter_corpus_codes(pattern=pattern, coder=coder, merge=True):
            for line_num, code in codes:
                all_codes.add(code)
        return all_codes

    def get_code_counts(self, pattern=None, coder=None):
        "Returns a defaultdict of {code: number of uses in codefiles}"
        all_codes = defaultdict(int)
        for f, codes in self.iter_corpus_codes(pattern=pattern, coder=coder, merge=True):
            for line_num, code in codes:
                all_codes[code] += 1
        return all_codes

    def get_coder_from_code_path(self, code_file_path):
        "Maps Path('some_interview.txt.cp.codes') -> 'cp'"
        parts = code_file_path.name.split('.')
        return parts[-2]

    def get_codebook(self):
        """
        Reads a tree of codes from the codebook file.
        """
        return TreeNode.read_yaml(self.codebook)

    def update_codebook(self):
        """
        Updates the codebook by adding any new codes used in the codefiles.
        Does not remove unused codes.
        """
        all_codes = self.get_all_codes()
        code_tree = self.get_codebook()
        new_codes = all_codes - set(code_tree.flatten(names=True))
        for new_code in new_codes:
            code_tree.add_child(new_code)
        TreeNode.write_yaml(self.codebook, code_tree)

    def rename_code(self, old_code, new_code):
        """
        Updates the codefiles and the codebook, replacing the old code with the new code. 
        Removes the old code from the codebook.
        """
        for corpus_path in self.iter_corpus():
            for code_file_path in self.get_code_files_for_corpus_file(corpus_path):
                codes = self.read_codes(code_file_path)
                codes = [(ln, new_code if code == old_code else code) for ln, code in codes]
                coder = self.get_coder_from_code_file_path(code_file_path)
                self.write_codes(code_file_path, coder, codes)

        code_tree = self.get_codebook()
        code_tree.rename(old_code, new_code)
        code_tree.remove_children_by_name(old_code)
        TreeNode.write_yaml(settings.codebook, code_tree)
        self.update_codebook()
                

            

        



