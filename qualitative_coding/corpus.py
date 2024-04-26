# Qualitative Coding corpus
# -------------------------
# (c) 2023 Chris Proctor

from itertools import chain, combinations_with_replacement
from collections import defaultdict
from contextlib import contextmanager
from importlib.metadata import metadata
from pathlib import Path
import yaml
import shutil
import numpy as np
from textwrap import fill
import os
from hashlib import sha1
from pathlib import Path
from sqlalchemy import (
    create_engine,
    select,
    delete,
    not_,
    func,
    distinct,
    text
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import (
    Session,
    aliased,
    sessionmaker,
)
from sqlalchemy.dialects.sqlite import insert
from qualitative_coding.helpers import prompt_for_choice
from qualitative_coding.tree_node import TreeNode
from qualitative_coding.logs import get_logger
from qualitative_coding.exceptions import (
    QCError, 
    SettingsError, 
    InvalidParameter,
)
from qualitative_coding.database.models import (
    Base,
    Document, 
    DocumentIndex,
    Location,
    Code, 
    Coder, 
    CodedLine,
    coded_line_location_association_table
)
from qualitative_coding.editors import editors
from qualitative_coding.media_importers import media_importers
from qualitative_coding.helpers import (
    iter_paragraph_lines,
    read_settings,
)

DEFAULT_SETTINGS = {
    'qc_version': metadata('qualitative-coding')['version'],
    'corpus_dir': 'corpus',
    'database': 'qualitative_coding.sqlite3',
    'logs_dir': 'logs',
    'memos_dir': 'memos',
    'codebook': 'codebook.yaml',
    'editor': 'code',
}

class QCCorpus:
    """Provides data access to the corpus of documents and codes. 
    QCCorpus methods which access the database must be called from within
    the session context manager:

    corpus = QCCorpus('settings.yaml')
    with corpus.session():
        corpus.get_or_create_code("interesting")
    """
    
    units = ["line", "paragraph", "document"]

    @classmethod
    def initialize(cls, settings_path="settings.yaml", accept_defaults=False):
        """
        Initializes a qc project.
        If the settings file does not exist, create it.
        Otherwise, uses the settings file to initialize the expected 
        directories and files.
        """
        settings_path = Path(settings_path)
        if settings_path.exists() or accept_defaults:
            if not settings_path.exists():
                settings_path.write_text(yaml.dump(DEFAULT_SETTINGS))
            cls.validate_settings(settings_path)
            settings = yaml.safe_load(settings_path.read_text())
            for needed_dir in ["corpus_dir", "logs_dir", "memos_dir"]:
                dirpath = Path(settings[needed_dir])
                if dirpath.exists() and not dirpath.is_dir():
                    raise QCError(f"Cannot create dir {dirpath}; there is a file with that name.")
                if not dirpath.exists():
                    dirpath.mkdir()
            codebook_path = Path(settings["codebook"])
            if codebook_path.exists() and codebook_path.is_dir():
                raise QCError(f"Cannot create {dirpath}; there is a directory with that name.")
            if not codebook_path.exists():
                codebook_path.touch()
            if Path(settings["database"]).is_absolute():
                db_path = Path(settings["database"])
            else:
                db_path = settings_path.resolve().parent / settings["database"]
            if db_path.exists() and db_path.is_dir():
                raise QCError(f"Cannot create {dirpath}; there is a directory with that name.")
            if not db_path.exists():
                engine = create_engine(f"sqlite:///{db_path}")
                Base.metadata.create_all(engine)
        else:
            settings_path.write_text(yaml.dump(DEFAULT_SETTINGS))

    @classmethod
    def validate_settings(cls, settings_path):
        """Checks that settings are valid, raising QCError if not.
        This method checks the contents of the settings file, but does
        not compare it with the project itself.
        """
        try:
            errors = []
            if not Path(settings_path).exists():
                errors.append(f"Settings file {settings_path} is missing")
                raise SettingsError()
            settings = read_settings(settings_path)
            for expected_key in DEFAULT_SETTINGS:
                if expected_key not in settings:
                    errors.append(f"Expected '{expected_key}' in settings")
                elif not isinstance(settings[expected_key], str):
                    errors.append(f"Invalid path for {expected_key}: {settings[expected_key]}")
            if 'editors' in settings:
                if not isinstance(settings['editors'], dict):
                    errors.append(f"Could not read custom-defined editors.")
                    raise SettingsError()
                for name, params in settings['editors'].items():
                    expected = {'name', 'code_command', 'memo_command'}
                    if isinstance(params, dict):
                        for extra in set(params.keys()) - expected:
                            errors.append(f"Unexpected param in editors.{name}: {extra}")
                        for missing in expected - set(params.keys()):
                            errors.append(f"Missing param in editors.{name}: {extra}")
                    else:
                        errors.append(f"Expected editors.{name} to be a dict")
            if not settings.get('editor') in {**editors, **settings.get('editors', {})}:
                errors.append(f"Unrecognized editor {settings.get('editor')}")
            if errors:
                raise SettingsError()
        except SettingsError:
            errfmt = [f" - {err}" for err in errors]
            raise QCError('\n'.join(["Error validating settings:"] + errfmt))

    def __init__(self, settings_path, skip_validation=False):
        self.settings_path = Path(settings_path)
        self.settings = read_settings(settings_path)
        if not skip_validation:
            self.validate()
        self.corpus_dir = self.resolve_path(self.settings['corpus_dir'])
        self.memos_dir = self.resolve_path(self.settings['memos_dir'])
        self.logs_dir = self.resolve_path(self.settings['logs_dir'])
        self.log = get_logger(__name__, self.logs_dir, self.settings.get('debug'))
        self.codebook_path = self.resolve_path(self.settings['codebook'])
        db_file = self.resolve_path(self.settings['database'])
        self.engine = create_engine(f"sqlite:///{db_file}")

    class NotInSession(Exception):
        def __init__(self, *args, **kwargs):
            msg = (
                "QCCorpus methods accessing the database must be called within "
                "a QCCOrpus.session() context manager."
            )
            return super().__init__(msg)

    @contextmanager
    def session(self):
        """A context manager which holds open a Session.
        Client code will often need to execute multiple corpus methods
        within a single session. For example:

        with corpus.session():
            corpus.get_or_create_coder('chris')

        This context manager should not be used within QCCorpus methods.
        Instead, use get_session() below; the session will be returned
        if it is in scope.
        """

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

    def resolve_path(self, path):
        "Returns a path relative to self.settings_path"
        path = Path(path)
        if path.is_absolute():
            return path.resolve()
        else:
            return (self.settings_path.parent / path).resolve()

    def validate(self):
        "Checks that project state is valid"
        QCCorpus.validate_settings(self.settings_path)
        errors = []
        for expected_dir in ['corpus_dir', 'logs_dir', 'memos_dir']:
            path = self.resolve_path(self.settings[expected_dir])
            if not path.exists():
                errors.append(f"{expected_dir} path {path} does not exist")
            elif not path.is_dir():
                errors.append(f"{expected_dir} path {path} is not a directory")
        for expected_file in ['codebook', 'database']:
            path = self.resolve_path(self.settings[expected_file])
            if not path.exists():
                errors.append(f"{expected_file} path {path} does not exist")
            elif path.is_dir():
                errors.append(f"{expected_file} path {path} is a directory")
        if errors:
            raise QCError("Invalid settings:\n" + "\n".join([f"- {err}" for err in errors]))

    def validate_corpus_paths(self):
        """Checks that the set of files in corpus_dir exactly matches Documents. 
        Also checks that corpus document hashes match those in the database
        This is not included in QCCorpus.validate because it would create a 
        circular dependency: This method must be run from within a QCCorpus.session, 
        which cannot be instantiated until initialization is complete.
        """
        q = select(Document)
        docs_in_db = set(self.get_session().scalars(q).all())
        paths_in_db = set(doc.file_path for doc in docs_in_db)
        paths_on_fs = set()
        for dir_path, dirs, filenames in os.walk(self.corpus_dir):
            for fn in filenames:
                paths_on_fs.add(str(Path(dir_path).relative_to(self.corpus_dir) / fn))
        errors = []
        for extra in paths_on_fs - paths_in_db:
            errors.append(
                f"{extra} is in the corpus directory but is not part of the project. " + 
                f"You can fix this by running: qc corpus import {extra} --importer verbatim"
            )
        for missing in paths_in_db - paths_on_fs:
            errors.append(
                f"{missing} is missing. Either restore the file or remove it from the " + 
                f"project by running: qc corpus remove {missing}"
            )
        for doc in docs_in_db:
            path = self.corpus_dir / doc.file_path
            if path.exists():
                if doc.file_hash != self.hash_file(path):
                    errors.append(
                        f"{doc.file_path} has been changed since it was imported. " + 
                        f"This could affect the alignment of existing codes. " + 
                        f"Either restore the original version of {doc.file_path}, or " + 
                        f"import the changed version by running: qc corpus rebase " + 
                        f"{doc.file_path}"
                    )
        if errors:
            err = "Errors found in corpus:\n"
            fmt = lambda err: fill(err, initial_indent=" - ", subsequent_indent="   ")
            error_messages = [fmt(err) for err in errors]
            err += '\n'.join(error_messages)
            raise QCError(err)

    def get_code_tree_with_counts(self, 
        pattern=None,
        file_list=None,
        coders=None,
        unit='line',
    ):
        tree = self.get_codebook()
        code_counts = self.count_codes(
            pattern=pattern,
            file_list=file_list, 
            coders=coders,
            unit=unit,
        )

        def recursive_totals(node):
            for child in node.children:
                recursive_totals(child)
            node.count = code_counts.get(node.name, 0)
            node.total = node.count + sum([c.total for c in node.children])

        recursive_totals(tree)
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

    # TODO once we implement migrations, this should be simplified using a 
    # delete cascade on the coder->coded_line
    def delete_coder(self, coder_name):
        try:
            q = select(CodedLine).where(CodedLine.coder_id == coder_name)
            coded_lines = self.get_session().scalars(q)
            q = select(Coder).where(Coder.name == coder_name)
            coder = self.get_session().execute(q).scalar_one()
        except NoResultFound:
            raise QCError(f"There is no coder named {coder_name}.")
        for coded_line in coded_lines:
            self.get_session().delete(coded_line)
        self.get_session().delete(coder)
        self.get_session().commit()

    def get_all_coders(self):
        q = select(Coder)
        return self.get_session().scalars(q)

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
        return TreeNode.read_yaml(self.codebook_path)

    def get_document(self, corpus_path):
        """Fetches a document object.
        """
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
        try:
            return self.get_session().execute(q).scalar_one()
        except NoResultFound:
            raise QCError(f"Error getting paragraph for {document.file_path}, line {line}.")

    def update_coded_lines(self, document, coder, coded_line_data):
        """Updates document's coded lines for the given coder.
        document and coder should be strings, and coded_line_data should
        be a list of dicts like {'line': 1, 'code_id': 'super}.

        Fetches all existing coded lines for the document and coder, and 
        then compares the set of existing coded line data with new coded line data.
        When existing are absent from new, marks objects for deletion. 
        When new are absent from existing, creates a new CodedLine and adds it to the session.
        """
        self.get_or_create_coder(coder)
        for code_id in set(cl['code_id'] for cl in coded_line_data):
            self.get_or_create_code(code_id)
        session = self.get_session()
        q = (select(CodedLine)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.document_id == document.file_path)
            .where(CodedLine.coder_id == coder)
        )
        existing_coded_lines = self.session.scalars(q).all()
        existing_coded_line_data = {(cl.line, cl.code_id) for cl in existing_coded_lines}
        new_coded_line_data = {(d['line'], d['code_id']) for d in coded_line_data}
        for cl in existing_coded_lines:
            if (cl.line, cl.code_id) not in new_coded_line_data:
                self.get_session().delete(cl)
        for (line, code_id) in new_coded_line_data - existing_coded_line_data:
            cl = CodedLine(line=line, code_id=code_id, coder_id=coder)
            session.add(cl)
            cl.locations.append(self.get_paragraph(document, line))
        session.commit()
        self.update_codebook()

    def get_relative_corpus_path(self, corpus_path):
        """Given a Path or str, tries to return a string representation of the
        path relative to the corpus directory, suitable for Document.file_path.
        """
        try:
            relative_path = Path(corpus_path).relative_to(self.corpus_dir)
            return str(relative_path)
        except ValueError:
            if Path(corpus_path).is_absolute():
                raise ValueError(
                    f"{corpus_path} is absolute and is not relative to corpus directory "
                    f"{self.settings['corpus_dir']}"
                )
            else:
                return str(corpus_path)

    def import_media(self, file_path, recursive=False, corpus_root=None, importer="pandoc"):
        """Imports media into the corpus. 
        Importing media consists of three tasks: 

        - transforming the media's representation, 
        - saving the transformed media into the corpus directory,
        - and registering the file in the database. 

        The specified media importer handles transformation and saving. 
        When recursive is True, walks the given directory and imports all files found.
        When corpus_root is true, saves the files relative to the given subdirectory within
        the corpus.
        """
        imp = media_importers[importer](self.settings)
        source = Path(file_path)

        if not source.exists():
            raise InvalidParameter(f"{source} does not exist.")
        if recursive and not source.is_dir():
            raise InvalidParameter(f"{source} must be a dir when importing recursively.")
        if not recursive and source.is_dir():
            raise InvalidParameter(f"{source} is a dir. Use --recursive.")
        if corpus_root and Path(corpus_root).is_absolute():
            raise InvalidParameter(f"corpus_root ({corpus_root}) must be a relative path.")

        if corpus_root:
            dest_root_dir = self.corpus_dir / corpus_root
            dest_root_dir.mkdir(parents=True, exist_ok=True)
        else:
            dest_root_dir = self.corpus_dir

        if recursive:
            for dir_path, dir_names, filenames in os.walk(source):
                rel_dir_path = str(Path(dir_path).relative_to(source))
                dest_dir = dest_root_dir / rel_dir_path
                dest_dir.mkdir(parents=True, exist_ok=True)
                for fn in filenames:
                    source_path = Path(dir_path) / fn
                    dest_path = (dest_dir / fn).with_suffix(".txt")
                    imp.import_media(source_path, dest_path)
                    self.register_document(dest_path)
        else:
            dest_path = (dest_root_dir / source.name).with_suffix(".txt")
            imp.import_media(source, dest_path)
            self.register_document(dest_path)

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

    def count_codes(self, pattern=None, file_list=None, coders=None, unit="line"):
        """Returns a dict of {code:count}.
        """
        unit_column = self.get_column_to_count(unit)
        query = (
            select(Code.name, func.count(distinct(unit_column)))
            .join(Code.coded_lines)
            .group_by(Code.name)
        )
        query = self.filter_query_by_document(query, pattern, file_list, unit=unit)
        query = self.filter_query_by_coders(query, coders)
        result = self.get_session().execute(query).all()
        return dict(result)

    def get_documents(self, pattern=None, file_list=None):
        """Returns matching Document objects.
        """
        query = select(Document)
        if pattern:
            query = query.where(Document.file_path.contains(pattern))
        if file_list:
            query = query.where(Document.file_path.in_(file_list))
        return self.get_session().scalars(query).all()

    def move_document(self, target, destination, recursive=False):
        """Move a file from target to destination, updating the database.
        """
        self.validate_corpus_paths()
        target = self.corpus_dir / target
        destination = self.corpus_dir / destination
        if not target.exists():
            raise QCError(f"{target} does not exist")
        if destination.exists():
            raise QCError(f"{destination} already exists")
        if recursive and not target.is_dir():
            raise QCError(f"Cannot use --recursive when {target} is a file.")
        if not recursive and target.is_dir():
            raise QCError(f"{target} is a directory. Use --recursive")

        if recursive:
            for dir_path, dir_names, filenames in os.walk(target):
                for fn in filenames:
                    dp = Path(dir_path).relative_to(target)
                    rtarget = target / dp / fn
                    rdestination = destination / dp / fn
                    old_file_path = str(rtarget.relative_to(self.corpus_dir))
                    new_file_path = str(rdestination.relative_to(self.corpus_dir))
                    self._move_document(old_file_path, new_file_path)
        else:
            old_file_path = str(target.relative_to(self.corpus_dir))
            new_file_path = str(destination.relative_to(self.corpus_dir))
            self._move_document(old_file_path, new_file_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        target.rename(destination)
        self.get_session().commit()

    def _move_document(self, old_file_path, new_file_path):
        """Updates a document's file path, and updates DocumentIndex.document_id
        to match. Does not commit the session.
        """
        doc = self.get_documents(file_list=[old_file_path])[0]
        for document_index in doc.indices:
            document_index.document_id = new_file_path
        doc.file_path = new_file_path

    def remove_document(self, target, recursive=False):
        """Remove a document, or recursively remove all documents in a directory.
        Also deletes related CodedLines.
        """
        session = self.get_session()
        self.validate_corpus_paths()
        target = self.corpus_dir / target
        if not target.exists():
            raise QCError(f"{target} does not exist")
        if recursive and not target.is_dir():
            raise QCError(f"Cannot use --recursive when {target} is a file.")
        if not recursive and target.is_dir():
            raise QCError(f"{target} is a directory. Use --recursive")
        if recursive:
            for dir_path, dir_names, filenames in os.walk(target):
                for fn in filenames:
                    dp = Path(dir_path).relative_to(target)
                    rtarget = target / dp / fn
                    file_path = str(rtarget.relative_to(self.corpus_dir))
                    self._remove_document(file_path)
            shutil.rmtree(target)
        else:
            file_path = str(target.relative_to(self.corpus_dir))
            self._remove_document(file_path)
            target.unlink()
        session.commit()

    def _remove_document(self, file_path):
        """Removes document and all dependents from the database.
        Currently, there are no delete cascades in the database. 
        When delete cascades are added in a future migration, this 
        method will become trivial.
        
        This method is intended to be called by other methods.
        Note that it does not commit the session.
        """
        session = self.get_session()
        for cl in self.get_coded_lines(file_list=[file_path]):
            session.delete(cl)
        doc = self.get_documents(file_list=[file_path])[0]
        session.delete(doc)

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

    def filter_query_by_coders(self, query, coders=None, coded_line_alias=CodedLine):
        """Filters a query by coders, if coders are given.
        Joins the query to CodedLine and adds a where clause matching the coder name.
        """
        if coders:
            return query.where(coded_line_alias.coder_id.in_(coders))
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

    def get_coded_lines(self, codes=None, pattern=None, file_list=None, coders=None):
        """Returns (code, coder, line, file_path)
        """
        query = (
            select(
                CodedLine.code_id, 
                CodedLine.coder_id, 
                CodedLine.line, 
                DocumentIndex.document_id
            )
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.name == "paragraphs")
            .order_by(DocumentIndex.document_id, CodedLine.line)
        )
        if codes:
            query = query.where(CodedLine.code_id.in_(codes))
        query = self.filter_query_by_document(query, pattern, file_list)
        query = self.filter_query_by_coders(query, coders)
        return self.get_session().execute(query).all()

    def get_coded_paragraphs(self, codes=None, pattern=None, file_list=None, coders=None):
        """Returns (Code.name, Coder.name, CodedLine.line_number, Document.file_path, Location.id,
                Location.start_line, Location.end_line)
        """
        query = (
            select(CodedLine.code_id, CodedLine.coder_id, DocumentIndex.document_id,
                   Location.start_line, Location.end_line)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.name == "paragraphs")
            .order_by(DocumentIndex.document_id, Location.start_line)
        )
        if codes:
            query = query.where(CodedLine.code_id.in_(codes))
        query = self.filter_query_by_document(query, pattern, file_list)
        query = self.filter_query_by_coders(query, coders)
        return self.get_session().execute(query).all()

    def get_coded_documents(self, codes=None, pattern=None, file_list=None, coders=None):
        """Returns (Code.name, Coder.name, Document.file_path)
        """
        query = (
            select(CodedLine.code_id, CodedLine.coder_id, DocumentIndex.document_id)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.name == "paragraphs")
            .order_by(DocumentIndex.document_id, CodedLine.line)
        )
        if codes:
            query = query.where(CodedLine.code_id.in_(codes))
        query = self.filter_query_by_document(query, pattern, file_list)
        query = self.filter_query_by_coders(query, coders)
        return self.get_session().execute(query).all()

    def get_code_matrix(self, codes, 
        recursive_codes=False,
        recursive_counts=False,
        depth=None, 
        unit='line',
        pattern=None,
        file_list=None,
        invert=False,
        coders=None,
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
            query = self.filter_query_by_coders(query, coders, CodedLineA)
            query = self.filter_query_by_coders(query, coders, CodedLineB)

            ab_count = self.get_session().scalars(query).first()
            cooccurrences[ix_a][ix_b] = ab_count
            cooccurrences[ix_b][ix_a] = ab_count

        labels = [n.expanded_name() if expanded else n.name for n in nodes] 
        return labels, cooccurrences

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
        TreeNode.write_yaml(self.codebook_path, code_tree)

    def rename_codes(self, old_codes, new_code, pattern=None, file_list=None, coders=None):
        """
        Updates the codefiles and the codebook, replacing the old code with the new code. 
        Removes the old code from the codebook.
        """
        session = self.get_session()
        new_code = self.get_or_create_code(new_code)
        query = (
            select(CodedLine)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.name == "paragraphs")
            .where(CodedLine.code_id.in_(old_codes))
        )
        query = self.filter_query_by_document(query, pattern, file_list)
        query = self.filter_query_by_coders(query, coders)
        matching_coded_lines = session.execute(query).scalars()
        for cl in matching_coded_lines:
            doc_path = cl.locations[0].document_index.document_id
            if self.coded_line_exists(cl.coder_id, new_code.name, cl.line, doc_path):
                session.delete(cl)
            else:
                cl.code = new_code
        session.commit()
        self.update_codebook()

    def coded_line_exists(self, coder_name, code_name, line, document_file_path):
        """Checks whether a coded line exists with the given params.
        This method is a candidate for optimization.
        """
        session = self.get_session()
        query = (
            select(CodedLine)
            .where(CodedLine.coder_id == coder_name)
            .where(CodedLine.code_id == code_name)
            .where(CodedLine.line == line)
            .join(CodedLine.locations)
            .join(Location.document_index)
            .where(DocumentIndex.document_id == document_file_path)
        )
        result = session.execute(query).scalars()
        return len(list(result)) > 0

    def count_codes_by_coder(self, codes=None, coders=None, recursive_codes=False,
            depth=None, pattern=None, file_list=None, unit='line', totals=True):
        """Counts codes per-coder. Returns a dict of dicts like {"coder":{"code": n}}.
        """
        coders = coders or [c.name for c in self.get_all_coders()]
        attr = "total" if totals else "count"
        totals_by_coder = defaultdict(lambda: defaultdict(int))
        for coder in coders:
            tree = self.get_code_tree_with_counts(
                pattern=pattern, 
                file_list=file_list,
                coders=[coder], 
                unit=unit, 
            )
            if codes:
                nodes = sum([tree.find(c) for c in codes], [])
                if recursive_codes:
                    nodes = set(sum([n.flatten(depth=depth) for n in nodes], []))
            else:
                nodes = tree.flatten(depth=depth)
            for node in nodes:
                totals_by_coder[coder][node.expanded_name()] = getattr(node, attr)
        return totals_by_coder

    def count_codes_by_document(self, codes=None, coders=None, recursive_codes=False,
            depth=None, pattern=None, file_list=None, unit='line', totals=True):
        """Counts codes per-coder. Returns a dict of dicts like {"coder":{"code": n}}.
        """
        documents = self.get_documents(pattern=pattern, file_list=file_list)
        documents = [doc.file_path for doc in documents]
        attr = "total" if totals else "count"
        totals_by_doc = defaultdict(lambda: defaultdict(int))
        for doc in documents:
            tree = self.get_code_tree_with_counts(
                file_list=[doc],
                coders=coders, 
                unit=unit, 
            )
            if codes:
                nodes = sum([tree.find(c) for c in codes], [])
                if recursive_codes:
                    nodes = set(sum([n.flatten(depth=depth) for n in nodes], []))
            else:
                nodes = tree.flatten(depth=depth)
            for node in nodes:
                totals_by_doc[doc][node.expanded_name()] = getattr(node, attr)
        return totals_by_doc











