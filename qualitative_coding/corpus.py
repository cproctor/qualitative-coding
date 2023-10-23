# Qualitative Coding corpus
# -------------------------
# (c) 2023 Chris Proctor

from itertools import chain, combinations_with_replacement
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
import yaml
import numpy as np
from hashlib import sha1
from pathlib import Path
from sqlalchemy import (
    create_engine,
    select,
    not_,
    func,
    distinct,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import (
    Session,
    aliased,
    sessionmaker,
)
from sqlalchemy.dialects.sqlite import insert
from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.exceptions import QCError
from qualitative_coding.database.models import (
    Base,
    Document, 
    DocumentIndex,
    Location,
    Code, 
    Coder, 
    CodedLine,
)
from qualitative_coding.testing import CorpusTestingMethodsMixin

DEFAULT_SETTINGS = {
    'corpus_dir': 'corpus',
    'database': 'qualitative_coding.sqlite3',
    'logs_dir': 'logs',
    'memos_dir': 'memos',
    'codebook_file': 'codebook.yaml',
    'editor': 'nano',
}

def iter_paragraph_lines(fh):
    p_start = 0
    in_whitespace = False
    for i, line in enumerate(fh):
        if line.strip() == "":
            in_whitespace = True
        elif in_whitespace:
            yield p_start, i
            p_start = i
            in_whitespace = False
    yield p_start, i + 1

def recursive_count(node):
    for child in node.children:
        recursive_count(child)
    node.count = code_counts.get(node.name, 0)
    node.total = node.count + sum(c.count for c in node.children)

class QCCorpus(CorpusTestingMethodsMixin):
    """Provides data access to the corpus of documents and codes. 
    QCCorpus methods which access the database must be called from within
    the session context manager:

    corpus = QCCorpus()
    with corpus.session():
        corpus.get_or_create_code("interesting")
    """
    
    units = ["line", "paragraph", "document"]

    @classmethod
    def initialize(cls, settings_file="settings.yaml"):
        """
        If the settings file does not exist, creates it. Uses the settings
        file to initialize the expected directories and files.
        """
        settings_path = Path(settings_file)
        if not settings_path.exists():
            settings_path.write_text(yaml.dump(DEFAULT_SETTINGS))
        settings = yaml.safe_load(settings_path.read_text())
        for key, val in settings.items():
            path = Path(val)
            if key.endswith("dir"):
                if path.exists():
                    if not path.is_dir():
                        msg = f"Expected {key} ({val}) to be a directory"
                        raise ValueError(msg)
                else:
                    path.mkdir(parents=True)
            elif key.endswith("file"):
                if path.exists():
                    if path.is_dir():
                        msg = f"Expected {key} ({val}) to be a file"
                        raise ValueError(msg)
                else:
                    path.touch()
        if not Path(settings['database']).exists():
            engine = create_engine(f"sqlite:///{settings['database']}")
            Base.metadata.create_all(engine)

    def __init__(self, settings):
        """
        We need the actual settings file instead of just settings because it also
        provides a default (portable) working directory for relative links
        """
        self.settings = settings
        self.validate()
        self.log = get_logger(
            __name__, 
            self.settings['logs_dir'], 
            self.settings.get('debug')
        )
        self.engine = create_engine(f"sqlite:///{self.settings['database']}")

    class NotInSession(Exception):
        def __init__(self, *args, **kwargs):
            msg = (
                "QCCorpus methods accessing the database must be called within "
                "a QCCOrpus.session() context manager."
            )
            return super().__init__(msg)

    @contextmanager
    def session(self):
        "A context manager which holds open a Session"
        session_context_manager = Session(self.engine)
        self.session = session_context_manager.__enter__()
        yield
        del self.session
        session_context_manager.__exit__(None, None, None)

    def get_session(self):
        "A context manager for sa's Session"
        try:
            return self.session
        except AttributeError:
            raise self.NotInSession()

    def validate(self):
        "Checks that files are as they should be"
        errors = []
        for attr in DEFAULT_SETTINGS.keys():
            if attr not in self.settings:
                errors.append(f"settings['{attr}'] is missing")
            elif attr.endswith('dir'):
                path = Path(self.settings[attr])
                if not path.exists():
                    errors.append(f"settings['{attr}'] ({path}) path does not exist.")
                elif not path.is_dir():
                    errors.append(f"settings['{attr}'] ({path}) is not a directory")
            elif attr.endswith('file'):
                path = Path(self.settings[attr])
                if not path.exists():
                    errors.append(f"settings['{attr}'] ({path}) path does not exist.")
                elif path.is_dir():
                    errors.append(f"settings['{attr}'] ({path}) is a directory")
        if errors:
            raise QCError("Invalid settings:\n" + "\n".join([f"- {err}" for err in errors]))

    def check_corpus_document_hashes(self):
        "Checks that corpus document hashes match those in the database"
        raise NotImplementedError()

    def get_code_tree_with_counts(self, 
        pattern=None,
        file_list=None,
        coder=None,
        unit='line',
    ):
        tree = self.get_codebook()
        code_counts = self.count_codes(
            pattern=pattern,
            file_list=file_list, 
            coder=coder,
            unit=unit,
        )
        for node in tree.flatten():
            node.count = code_counts.get(node.name, 0)
        recursive_count(tree)
        return tree

    def get_or_create_coder(self, coder_name):
        try:
            q = select(Coder).where(Coder.name == coder_name)
            return self.get_session().execute(q).scalar_one()
        except NoResultFound:
            coder = Coder(name=coder_name)
            self.get_session().add(coder)
            self.get_session().commit()
            return coder

    def get_all_coders(self):
        q = select(Coder.name)
        return self.get_session().execute(q).scalars()

    def get_or_create_code(self, code_name):
        try:
            q = select(Code).where(Code.name == code_name)
            return self.get_session().execute(q).scalar_one()
        except NoResultFound:
            code = Code(name=code_name)
            self.get_session().add(code)
            self.get_session().commit()
            return code

    def get_codes(self, pattern=None, file_list=None, coder=None):
        "Returns a list of all unique codes used in the corpus"
        query = select(Code.name).join(Code.coded_lines)
        query = self.filter_query_by_document(query, pattern, file_list)
        if coder:
            query = query.join(CodedLine.coder).where(Coder.name == coder)
        result = self.get_session().scalars(query).all()
        return set(result)

    def get_codebook(self):
        "Reads a tree of codes from the codebook file."
        return TreeNode.read_yaml(self.settings['codebook_file'])

    def get_document(self, corpus_path):
        relpath = self.get_relative_corpus_path(corpus_path)
        q = select(Document).where(Document.file_path == relpath)
        return self.get_session().scalars(q).first()

    def get_paragraph(self, document, line, index_name="paragraphs"):
        """Gets the paragraph Location for the given document and the given line.
        """
        q = (
            select(Location)
            .join(Location.document_index)
            .join(DocumentIndex.document)
            .where(Document.file_path == document.file_path)
            .where(DocumentIndex.name == index_name)
            .where(Location.start_line <= line)
            .where(Location.end_line > line)
        )
        return self.get_session().execute(q).scalar_one()

    def create_coded_lines_if_needed(self, document, coded_line_data):
        """Inserts or ignores data for coded lines, associating them with the Document
        through paragraphs.
        """
        stmt = (
            insert(CodedLine)
            .values(coded_line_data)
            .on_conflict_do_nothing()
            .returning(CodedLine)
        )
        result = self.get_session().scalars(stmt)
        for coded_line in result:
            paragraph = self.get_paragraph(document, coded_line.line)
            coded_line.locations.append(paragraph)
        self.get_session().commit()

    def get_relative_corpus_path(self, corpus_path):
        """Given a Path or str, tries to return a string representation of the
        path relative to the corpus directory, suitable for Document.file_path.
        """
        try:
            relative_path = Path(corpus_path).relative_to(self.settings['corpus_dir'])
            return str(relative_path)
        except ValueError:
            if Path(corpus_path).is_absolute():
                raise ValueError(
                    f"{corpus_path} is absolute and is not relative to corpus directory "
                    f"{self.settings['corpus_dir']}"
                )
            else:
                return str(corpus_path)

    def hash_file(self, corpus_path):
        """Computes the hash of a document at a corpus path.
        """
        return sha1(Path(corpus_path).read_bytes()).hexdigest()

    def register_document(self, corpus_path):
        """Adds database entries for a document.
        Document contents are stored in files under the corpus_dir
        """
        doc = self.get_document(corpus_path)
        if doc:
            raise Document.AlreadyExists(doc)
        relpath = self.get_relative_corpus_path(corpus_path)
        document = Document(
            file_path=relpath,
            file_hash=self.hash_file(corpus_path),
        )
        self.get_session().add(document)
        index = DocumentIndex(
            name="paragraphs",
            document=document,
        )
        self.get_session().add(index)
        with open(corpus_path) as fh:
            for p_start, p_end in iter_paragraph_lines(fh):
                self.get_session().add(Location(
                    start_line=p_start, 
                    end_line=p_end,
                    document_index=index,
                ))
        self.get_session().commit()

    def count_codes(self, pattern=None, file_list=None, coder=None, unit="line"):
        """Returns a dict of {code:count}.
        """
        unit_column = self.get_column_to_count(unit)
        query = (
            select(Code.name, func.count(distinct(unit_column)))
            .join(Code.coded_lines)
            .group_by(Code.name)
        )
        query = self.filter_query_by_document(query, pattern, file_list, unit=unit)
        query = self.filter_query_by_coder(query, coder)
        result = self.get_session().execute(query).all()
        return dict(result)

    def get_documents(self, pattern=None, file_list=None):
        query = select(Document)
        if pattern:
            query = query.where(Document.file_path.contains(pattern))
        if file_list:
            query = query.where(Document.file_path.in_(file_list))
        return self.get_session().scalars(query).all()

    def filter_query_by_document(self, query, pattern=None, file_list=None, 
            unit="line"):
        """Filters a query by which documents match. 
        When unit is paragraph or document, ensures that the query is joined to needed
        tables regardless of whether pattern or file_list are provided.
        """
        if pattern or file_list or unit == "paragraph" or unit == "document":
            query = query.join(CodedLine.locations).join(Location.document_index)
        if pattern or file_list or unit == "document":
            query = query.join(DocumentIndex.document)
        if unit == "paragraph": 
            query = query.where(DocumentIndex.name == "paragraphs")
        if pattern:
            query = query.where(Document.file_path.contains(pattern))
        if file_list:
            query = query.where(Document.file_path.in_(file_list))
        return query

    def filter_query_by_coder(self, query, coder=None, coded_line_alias=CodedLine):
        """Filters a query by coder, if coder is given.
        Joins the query to CodedLine and adds a where clause matching the coder name.
        """
        if coder:
            return query.where(coded_line_alias.coder_id == coder)
        else:
            return query

    def get_column_to_count(self, unit="line", coded_line_alias=CodedLine, 
            location_alias=Location, document_alias=Document):
        """Returns the table and column for a given unit of analysis.
        """
        return {
            "line": coded_line_alias.id,
            "paragraph": location_alias.id,
            "document": document_alias.file_path,
        }[unit]

    def get_coded_lines(self, codes=None, pattern=None, file_list=None, coder=None, unit="line"):
        """Returns (Code.name, CodedLine.line_number, Document.file_path)
        """
        query = (
            select(CodedLine.code_id, CodedLine.line, DocumentIndex.document_id)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .order_by(DocumentIndex.document_id, CodedLine.line)
        )
        if codes:
            query = query.where(CodedLine.code_id.in_(codes))
        query = self.filter_query_by_document(query, pattern, file_list)
        query = self.filter_query_by_coder(query, coder)
        return self.get_session().execute(query).all()

    def get_code_matrix(self, codes, 
        recursive_codes=False,
        recursive_counts=False,
        depth=None, 
        unit='line',
        pattern=None,
        file_list=None,
        invert=False,
        coder=None,
        expanded=False,
    ):
        """Returns a list of codes and a matrix of (codes * selections). 
        Each code represents its code set, consisting of itself and 
        matching child codes, if `recursive_codes` is set. 
        Selections are each unit within each matching corpus file.
        """
        tree = self.get_codebook()
        if codes:
            nodes = sum([tree.find(c) for c in codes], [])
            if recursive_codes:
                nodes = set(sum([n.flatten(depth=depth) for n in nodes], []))
        else:
            nodes = tree.flatten(depth=depth)
        node_names = set([n.name for n in nodes])
        if recursive_counts:
            code_sets = [(n.name, set(n.flatten(names=True))) for n in nodes]
        else:
            code_sets = [(n.name, set([n.name])) for n in nodes]

        CodedLineA = aliased(CodedLine)
        CodedLineB = aliased(CodedLine)
        LocationA = aliased(Location)
        LocationB = aliased(Location)
        unit_column = self.get_column_to_count(unit, coded_line_alias=CodedLineA,
            location_alias=LocationA)
        cooccurrences = np.zeros((len(nodes), len(nodes)), dtype=int)
        combos = combinations_with_replacement(enumerate(code_sets), 2)
        for (ix_a, (c_a, cs_a)), (ix_b, (c_b, cs_b)) in combos:
            query = (
                select(func.count(distinct(unit_column)))
                .where(CodedLineA.code_id.in_(cs_a))
                .where(CodedLineB.code_id.in_(cs_b))
                .where(CodedLineA.line == CodedLineB.line)
                .join(LocationA, CodedLineA.locations)
                .join(LocationB, CodedLineB.locations)
                .where(LocationA.document_index_id == LocationB.document_index_id)
            )
            query = self.filter_query_by_coder(query, coder, CodedLineA)
            query = self.filter_query_by_coder(query, coder, CodedLineB)

            ab_count = self.get_session().scalars(query).first()
            cooccurrences[ix_a][ix_b] = ab_count
            cooccurrences[ix_b][ix_a] = ab_count

        labels = [n.expanded_name() if expanded else n.name for n in nodes] 
        return labels, cooccurrences

# ======== EVERYTHING BELOW HERE IS QUESTIONABLE ===============

    def XXXwrite_codes(self, corpus_text_path, coder, codes):
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

    def XXXread_codes(self, code_file_path, unit='line'):
        """Reads codes from a code file as a list of (ix, code).
        ix is the selection index and code is a string.
        When unit is 'line', selection index is the line number.
        When unit is 'paragraph', selection index is the paragraph number.
        When unit is 'document', selection index is 0.
        """
        codes = []
        with open(code_file_path) as inf:
            for line_num, line in enumerate(inf):
                codes += [(line_num, code.strip()) for code in line.split(",") if code.strip()]
        if unit == 'line': 
            return codes
        elif unit == 'paragraph':
            corpus_file_path = self.get_corpus_file_path(code_file_path)
            para_starts = self.get_paragraph_start_lines(corpus_file_path)
            return [(self.get_paragraph_index(para_starts, line), code) for line, code in codes]
        elif unit == 'document': 
            return [(0, c) for c in set(code for i, code in codes)]
        else:
            raise NotImplementedError("Unit must be 'line' or 'document'.")

    def XXXis_coded(self, corpus_file_path, coder):
        """Returns True when coder has entered codes for corpus_file_path
        """
        raise NotImplementedError("TODO")

    def XXXget_paragraph_start_lines(self, corpus_file_path):
        """Returns a list of lines on which paragraphs start
        """
        paras = []
        in_paragraph = False
        with open(corpus_file_path) as inf:
            for ix, line in enumerate(inf):
                if in_paragraph and line.strip() == '':
                    in_paragraph = False
                elif not in_paragraph and line.strip() != '':
                    paras.append(ix)
        return paras

    def XXXget_paragraph_index(self, para_starts, line_num):
        """Maps a line number to a paragraph index. 
        para_starts is a list of starting lines for paragraphs. 
        Note that -1 is a valid return value, if codes are applied 
        to lines preceding the first paragraph.
        """
        for para_ix, para_start in enumerate(para_starts):
            if line_num < para_start:
                return para_ix
        return len(para_starts) - 1

    def get_coded_selections(self, pattern=None, file_list=None, invert=False, coder=None, unit='line'):
        """Returns a dict like {code: selections}.
        Selections is a set of (file_path, selection_ix).
        """
        coded_selections = defaultdict(set)
        for corpus_file in self.iter_corpus(pattern=pattern, file_list=file_list, invert=invert):
            codes = self.get_codes(corpus_file, coder=coder, merge=True, unit=unit)
            grouped_codes = defaultdict(set)
            for ix, code in codes:
                grouped_codes[ix].add(code)
            for ix in sorted(grouped_codes.keys()):
                for code in grouped_codes[ix]:
                    coded_selections[code].add((str(corpus_file), ix))
        return coded_selections

    def update_codebook(self):
        """
        Updates the codebook by adding any new codes used in the codefiles.
        Does not remove unused codes.
        """
        all_codes = self.get_codes()
        code_tree = self.get_codebook()
        new_codes = all_codes - set(code_tree.flatten(names=True))
        for new_code in new_codes:
            code_tree.add_child(new_code)
        TreeNode.write_yaml(self.settings['codebook_file'], code_tree)

    def rename_codes(self, old_codes, new_code, pattern=None, file_list=None, invert=False, coder=None,
                update_codebook=False):
        """
        Updates the codefiles and the codebook, replacing the old code with the new code. 
        Removes the old code from the codebook.
        """
        for corpus_path in self.iter_corpus(pattern=pattern, file_list=file_list, invert=invert):
            for code_file_path in self.get_code_files_for_corpus_file(corpus_path, coder=coder):
                existing_codes = self.read_codes(code_file_path)
                if len(existing_codes) == 0: 
                    continue
                line_nums, codes = zip(*self.read_codes(code_file_path))
                if set(old_codes) & set(codes):
                    new_codes = [(ln, new_code if code in old_codes else code) for ln, code in zip(line_nums, codes)]
                    existing_coder = self.get_coder_from_code_path(code_file_path)
                    self.write_codes(corpus_path, existing_coder, new_codes)

        global_rename = pattern is None and file_list is None and invert is None and coder is None
        if global_rename or update_codebook:
            code_tree = self.get_codebook()
            for old_code in old_codes:
                code_tree.rename(old_code, new_code)
                code_tree.remove_children_by_name(old_code)
                self.log.info(f"Renamed code {old_code} to {new_code}")
            TreeNode.write_yaml(self.settings['codebook_file'], code_tree)
            self.update_codebook()
                

            

        




