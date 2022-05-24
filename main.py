import os
import sys
import logging

from dotenv import load_dotenv

from models.neo4j import Publication, Author, Keyword, Excerpt, Thought, Journal, Conference, Abstract
from reference_manager import query_db
from utils import Colours

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger = logging.getLogger('main')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
# todo: add formatter with time for this logger
# todo: add file handler

load_dotenv()

logger.info(Colours.green + 'Querying the database' + Colours.reset)
results = query_db(os.getenv('ZOTERO_DB_PATH'))

logger.info(Colours.green + 'Query successful.\nTransferring to Neo4j' + Colours.reset)

for item in results:

    # Create Publication
    publication_node = Publication(title=item.bib.title, identifier=item.identifier).save()

    # Create Authors
    author_nodes = Author.create_or_update(*({'name': author} for author in item.bib.author))
    for author_node in author_nodes:
        publication_node.authors.connect(author_node)

    # Create Tags
    tag_nodes = Keyword.create_or_update(*({'name': tag} for tag in item.tags))
    for tag_node in tag_nodes:
        publication_node.tags.connect(tag_node)

    # Create Excerpts and Thoughts
    for annotation in item.annotations:
        thought_node = Thought(
            content=annotation.comment,
            color=annotation.colour,
            page=annotation.page
        ).save()

        if annotation.text:  # Note is related to a highlighted text.
            excerpt_node = Excerpt(
                content=annotation.text,  # String strip
                color=annotation.colour,
                page=annotation.page
            ).save()
            # connect Excerpt to publication and attach Thought to Excerpt
            excerpt_node.publication.connect(publication_node)
            thought_node.excerpt.connect(excerpt_node)
        else:
            # Connect Thought directly to publication
            thought_node.publication.connect(publication_node)

logger.info(Colours.green + 'Transfer complete' + Colours.reset)
