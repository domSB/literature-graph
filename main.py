import os

from dotenv import load_dotenv

from models import Publication, Author, Keyword, Excerpt, Thought, Journal, Conference, Abstract
from papersapp import query_db

load_dotenv()

results = query_db(os.getenv('PAPERS_DB_PATH'))

for papers_item in results:
    id_ = papers_item['id']
    reference = papers_item['article']
    annotations = papers_item['user_data']['annotations']
    tags = papers_item['user_data'].get('tags', [])
    gen_assessment = papers_item['user_data'].get('notes', None)
    authors = reference.get('authors', [])
    title = reference['title']

    color = papers_item['user_data']['color']
    rating = papers_item['user_data'].get('rating', 0)

    # Create Publication
    publication_node = Publication(title=title, papers_id=id_).save()

    # Create Authors
    author_nodes = Author.create_or_update(*({'name': author} for author in authors))
    for author_node in author_nodes:
        publication_node.authors.connect(author_node)

    # Create Tags
    tag_nodes = Keyword.create_or_update(*({'name': tag} for tag in tags))
    for tag_node in tag_nodes:
        publication_node.tags.connect(tag_node)

    # Special Note in Papers, that is related to the whole publication
    if gen_assessment:
        ga_node = Thought(
            content=gen_assessment[:1000]  # String strip
        ).save()  # has no colour nor any page reference
        ga_node.publication.connect(publication_node)

    # Create Excerpts and Thoughts
    for annotation in annotations:
        anno_id = annotation['id']
        if annotation['type'] == 'highlight':

            # Excerpts are always created, since they cannot exist already.
            excerpt_node = Excerpt(
                content=annotation['text'][:1000],  # String strip
                color=str(annotation['color_id']),
                page=annotation['page_start']
            ).save()
            excerpt_node.publication.connect(publication_node)
            if annotation['has_note']:
                thought_node = Thought(
                    content=annotation['note'],
                    color=str(annotation['color_id']),  # Only Integer, should be Word
                    page=annotation['page_start']
                ).save()
                thought_node.excerpt.connect(excerpt_node)
        elif annotation['type'] == 'note':
            thought_node = Thought(
                content=annotation['note'],
                color=str(annotation['color_id']),
                page=annotation['page_start']
            ).save()
            thought_node.publication.connect(publication_node)
        elif annotation['type'] == 'strikethrough':
            pass
        else:
            raise NotImplementedError('Unbekannter Annotationstyp')
