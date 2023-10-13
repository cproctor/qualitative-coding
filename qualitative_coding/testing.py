from sqlalchemy import (
    create_engine,
    select,
    not_,
    func,
)
from sqlalchemy.orm import (
    Session,
    aliased,
)
from qualitative_coding.database.models import (
    Base,
    Document, 
    DocumentIndex,
    Location,
    Code, 
    Coder, 
    CodedLine,
)

class CorpusTestingMethodsMixin:
    """Provides methods used during testing.
    """
    def get_paragraphs(self, corpus_path):
        relpath = self.get_relative_corpus_path(corpus_path)
        q = (
            select(Location)
            .join(Location.document_index)
            .join(DocumentIndex.document)
            .where(Document.file_path == relpath)
        )
        print(q)
        with Session(self.engine) as session:
            return session.scalars(q).all()

    def temp_show_coded_lines(self):
        with Session(self.engine) as session:
            q = select(CodedLine)
            print(session.execute(q).all())

