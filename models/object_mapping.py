"""
still missing {'document', 'webpage', None, 'thesis', 'report', 'phdthesis}
"""
from typing import List, Union, Optional

from pydantic import BaseModel


class BaseReference(BaseModel):
    author: List[str]
    title: str
    year: int


class Article(BaseReference):
    journal: str
    volume: Optional[str]
    number: Optional[str]
    pages: Optional[int]
    month: Optional[str]


class Book(BaseReference):
    publisher: str
    volume: Optional[str]
    number: Optional[str]
    series: Optional[str]
    address: Optional[str]
    edition: Optional[str]
    month: Optional[str]
    isbn: Optional[str]


class BookSection(BaseReference):
    publisher: str
    booktitle: str
    volume: Optional[str]
    editor: Optional[str]
    number: Optional[str]
    series: Optional[str]
    type: Optional[str]
    chapter: Optional[str]
    pages: Optional[str]
    address: Optional[str]
    edition: Optional[str]
    month: Optional[str]


class ConferencePaper(BaseReference):
    booktitle: str
    volume: Optional[str]
    editor: Optional[str]
    number: Optional[str]
    series: Optional[str]
    pages: Optional[str]
    address: Optional[str]
    month: Optional[str]
    organization: Optional[str]
    publisher: Optional[str]


class Annotation(BaseModel):
    comment: str
    text: str = ''
    colour: str = ''
    page: int = 0


class Item(BaseModel):
    bib: Union[Article, Book, BookSection, ConferencePaper]
    annotations: List[Annotation]
    identifier: str
    tags: List[str]
