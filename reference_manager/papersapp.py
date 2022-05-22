import os
import sys
import json
import logging
import sqlite3
from typing import List, Union

from models.object_mapping import Article, Book, BookSection, ConferencePaper, Annotation, Item
from utils import Colours

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger = logging.getLogger('papers')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

MAX_TEXT_LEN = 1000  # Strips long comments, excerpts, etc. since Neo4j cuts string-properties.


colors = {'#fe8e23': 'Orange', '#1ea4fc': 'Blue', '#00d127': 'Green', '#fe3018': 'Red', '#fed12f': 'Yellow'}
# TODO: Adobe eigene Farben hinzufügen
# TODO: Add Colour Codes of papers-annotations


def unpack(row) -> Union[Item, None]:
    item_str = row[0]  # sqlite returns tuple with one item
    papers_item = json.loads(item_str)
    papers_item['user_data']['color'] = colors.get(papers_item['user_data'].get('color'))
    try:
        if papers_item['item_type'] == 'article':
            reference = Article(
                author=papers_item['article'].get('authors', []),
                title=papers_item['article']['title'],
                year=papers_item['article']['year'],
                journal=papers_item['article'].get('journal', 'Journal not found 😒')
                # Long live UTF-8. Not providing required metadata gives you a not amused smiley
            )
        elif papers_item['item_type'] == 'book':
            reference = Book(
                author=papers_item['article'].get('authors', []),
                title=papers_item['article']['title'],
                year=papers_item['article']['year'],
                publisher=papers_item['custom_metadata'].get('publisher', 'Publisher not found 😒')
            )
        elif papers_item['item_type'] == 'book_section':
            reference = BookSection(
                author=papers_item['article'].get('authors', []),
                title=papers_item['article']['title'],
                year=papers_item['article']['year'],
                publisher=papers_item['custom_metadata'].get('publisher', 'Publisher not found 😒'),
                booktitle=papers_item['custom_metadata'].get('container_title', 'Booktitle not found 😒')
            )
        elif papers_item['item_type'] == 'conference_paper':
            reference = ConferencePaper(
                author=papers_item['article'].get('authors', []),
                title=papers_item['article']['title'],
                year=papers_item['article']['year'],
                booktitle=papers_item['custom_metadata'].get('container_title', 'Proceedings title not found 😒')
            )
        else:
            logger.warning(
                Colours.red +
                f"Publication type {papers_item['item_type']} cannot be processed. [skipping item]" +
                Colours.reset + str(papers_item['article']).replace('\n', ' ')[:200])
            # item may contain abstract. Therefore, we strip newline character to have one line per log entry
            # ,and we cut after 200 chars to keep log files cleaner.
            return
    except KeyError as key_err:
        logger.warning(Colours.red + f"The important field {key_err} is missing. [skipping item]" +
                       Colours.reset + str(papers_item['article']).replace('\n', ' ')[:200])
        return

    tags = papers_item['user_data'].get('tags', [])

    gen_assessment = papers_item['user_data'].get('notes', None)
    annotations = []

    if gen_assessment:
        annotations.append(
            Annotation(
                text='',
                comment=gen_assessment,
                page=0
            )
        )
    for annotation in papers_item['user_data']['annotations']:

        if annotation['type'] == 'highlight':
            annotations.append(
                Annotation(
                    text=annotation['text'][:MAX_TEXT_LEN],
                    comment=annotation.get('note', ''),
                    colour=str(annotation['color_id']),  # TODO: convert color_id to colour name
                    page=annotation['page_start']
                )
            )

        elif annotation['type'] == 'note':
            annotations.append(
                Annotation(
                    text='',
                    comment=annotation['note'],
                    colour=str(annotation['color_id']),
                    page=annotation['page_start']
                )
            )

        else:
            logger.warning(Colours.yellow + f"Annotation type {annotation['type']} cannot be processed." +
                           Colours.reset)

    if 'doi' in papers_item['ext_ids'].keys():
        identifier = '<doi>' + papers_item['ext_ids']['doi']
    elif 'arxiv' in papers_item['ext_ids'].keys():
        identifier = '<arxiv>' + papers_item['ext_ids']['arxiv']
    else:
        identifier = '<papersapp>' + papers_item['id']

    item_mn = Item(bib=reference, annotations=annotations, identifier=identifier, tags=tags)
    return item_mn


def query_papers_db(path: str) -> List[Item]:
    """
    Connects to the PapersApp DB and fetches all results.
    :param path:
    :return:
    """
    assert os.path.isfile(path), Colours.red + f"The provided path is not valid. \n" + Colours.reset + path
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    item_gen = map(unpack, cur.execute("SELECT t.json from items t where json_extract(t.json, '$.deleted') = FALSE"))

    return list(filter(None, item_gen))


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    complete_items = query_papers_db(os.getenv('PAPERS_DB_PATH'))
