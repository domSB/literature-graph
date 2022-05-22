import os

from neomodel import config, StructuredNode, StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom
from dotenv import load_dotenv

load_dotenv()

config.DATABASE_URL = f"bolt://neo4j:{os.getenv('NEO_PASS')}@{os.getenv('NEO_URL', 'localhost')}:7687"
config.ENCRYPTED_CONNECTION = False
"""
# BUG
Cypher version needs to be downgraded to 3.5, since neo model doesn't yet support the syntax of V4.
DBMS change to cypher.default_language_version=3.5 not 4 (is in the config almost at the bottom), see
https://github.com/neo4j-contrib/neomodel/issues/487
"""
clip_long_text_at = 1000
# See https://neomodel.readthedocs.io/en/latest/properties.html#stringproperty
# Neo4j clips properties of type string with more than 4039 bytes without throwing an error


class Publication(StructuredNode):
    bib_key = StringProperty()
    identifier = StringProperty(unique_index=True)
    doi = StringProperty()
    title = StringProperty(required=True)
    rating = IntegerProperty(default=0)

    authors = RelationshipFrom('Author', 'AUTHORED')
    tags = RelationshipTo('Keyword', 'AUTHOR_TAG')
    abstract = RelationshipFrom('Abstract', 'SUMMARISES')
    excerpts = RelationshipFrom('Excerpt', 'IS_MENTIONED_IN')
    general_assessment = RelationshipFrom('Thought', 'COMMENTS_ON')
    journal = RelationshipTo('Journal', 'PUBLISHED_IN')
    conference = RelationshipTo('Conference', 'PRESENTED_AT')


class Author(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    bibliography = RelationshipTo(Publication, 'AUTHORED')


class Keyword(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    publications = RelationshipFrom('Publication', 'AUTHOR_TAG')


class Abstract(StructuredNode):
    content = StringProperty(max_length=clip_long_text_at)
    publication = RelationshipTo('Publication', 'SUMMARISES')


class Excerpt(StructuredNode):
    content = StringProperty(max_length=clip_long_text_at)
    colour = StringProperty()  # TODO: Choices festlegen
    page = IntegerProperty()
    publication = RelationshipTo('Publication', 'IS_MENTIONED_IN')
    thoughts = RelationshipFrom('Thought', 'COMMENTS_ON')


class Thought(StructuredNode):
    content = StringProperty(max_length=clip_long_text_at)
    colour = StringProperty()  # TODO: Choices festlegen
    page = IntegerProperty()  # For lose commentaries or general notes
    excerpt = RelationshipTo('Excerpt', 'COMMENTS_ON')  # Can relate to a certain excerpt
    publication = RelationshipTo('Publication', 'COMMENTS_ON')  # Otherwise, relates to whole publication or page


class Journal(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    issn = StringProperty()
    publications = RelationshipFrom('Publication', 'PUBLISHED_IN')


class Conference(StructuredNode):
    proceedings = StringProperty(required=True, unique_index=True)
    publications = RelationshipFrom('Publication', 'PUBLISHED_IN')
