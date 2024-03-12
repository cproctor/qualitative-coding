from typing import List
from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Table,
    Column,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column, 
    relationship,
)
from qualitative_coding.exceptions import QCError

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "document"
    file_path: Mapped[str] = mapped_column(primary_key=True)
    file_hash: Mapped[str] 
    indices: Mapped[List["DocumentIndex"]] = relationship(back_populates="document",
            cascade="all, delete-orphan")

    class AlreadyExists(QCError):
        def __init__(self, doc):
            self.doc = doc
            err = f"A Document with file path {doc.file_path} already exists"
            super().__init__(err)

class DocumentIndex(Base):
    __tablename__ = "document_index"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "name", 
        ),
)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    time_series: Mapped[bool] = mapped_column(default=False)
    document_id: Mapped[str] = mapped_column(ForeignKey(Document.file_path))
    document: Mapped["Document"] = relationship(back_populates="indices")
    locations: Mapped[List["Location"]] = relationship(back_populates="document_index",
            cascade="all, delete-orphan")

coded_line_location_association_table = Table(
    "coded_line_location_association",
    Base.metadata,
    Column("coded_line_id", ForeignKey("coded_line.id"), primary_key=True),
    Column("location_id", ForeignKey("location.id"), primary_key=True),
)

class Location(Base):
    __tablename__ = "location"
    __table_args__ = (
        CheckConstraint("start_line <= end_line"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_line: Mapped[int]
    end_line: Mapped[int]
    document_index_id: Mapped[str] = mapped_column(ForeignKey(DocumentIndex.id))
    document_index: Mapped["DocumentIndex"] = relationship(back_populates="locations")
    coded_lines: Mapped[List["CodedLine"]] = relationship(
        secondary=coded_line_location_association_table,
        back_populates="locations",
    )

class Code(Base):
    __tablename__ = "code"
    name: Mapped[str] = mapped_column(primary_key=True)
    coded_lines: Mapped[List["CodedLine"]] = relationship(back_populates="code",
            cascade="all, delete-orphan")

class Coder(Base):
    __tablename__ = "coder"
    name: Mapped[str] = mapped_column(primary_key=True)
    coded_lines: Mapped[List["CodedLine"]] = relationship(back_populates="coder", 
            cascade="all, delete-orphan")

class CodedLine(Base):
    __tablename__ = "coded_line"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    line: Mapped[int]
    coder_id: Mapped[str] = mapped_column(ForeignKey(Coder.name))
    coder: Mapped["Coder"] = relationship(back_populates="coded_lines")
    code_id: Mapped[str] = mapped_column(ForeignKey(Code.name))
    code: Mapped["Code"] = relationship(back_populates="coded_lines")
    locations: Mapped[List["Location"]] = relationship(
        secondary=coded_line_location_association_table,
        back_populates="coded_lines"
    )
