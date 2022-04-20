import sys
import json
import logging
import sqlite3

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger = logging.getLogger('papers')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

keys = {
    'conference_paper': {
        'bib_key': 'inproceedings',
        'core': ['author', 'title', 'booktitle', 'year'],
        'core_alias': ['authors', 'title', 'container_title', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'pages', 'address', 'month', 'organization', 'publisher', 'note']
    },
    'book_section': {
        'bib_key': 'incollection',
        'core': ['author', 'title', 'booktitle', 'publisher', 'year'],
        'core_alias': ['authors', 'title', 'container_title', 'publisher', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'type', 'chapter', 'pages', 'address', 'edition', 'month', 'note']
    },
    'article': {
        'bib_key': 'article',
        'core': ['author', 'title', 'journal', 'year'],
        'core_alias': ['authors', 'title', 'journal', 'year'],
        'optional': ['volume', 'number', 'pages', 'month', 'note']
    },
    'book': {
        'bib_key': 'book',
        'core': ['author', 'title', 'publisher', 'year'],  # oder editor
        'core_alias': ['authors', 'title', 'publisher', 'year'],
        'optional': ['volume', 'number', 'series', 'address', 'edition', 'month', 'note', 'isbn']
    },
    # still missing {'document', 'webpage', None, 'thesis', 'report', 'phdthesis}
}

colors = {'#fe8e23': 'Orange', '#1ea4fc': 'Blue', '#00d127': 'Green', '#fe3018': 'Red', '#fed12f': 'Yellow'}


def unpack(item):
    full_dict = json.loads(item[0])
    full_dict['user_data']['color'] = colors.get(full_dict['user_data'].get('color'))
    return full_dict


def get_bib(papers_item: dict) -> dict:
    """
    Takes a papers item and returns it as bib-entry. If the conversion fails, it logs the error and returns an empty
    dictionary.
    :param papers_item:
    :return:
    """
    article = papers_item['article']
    if pub_type := papers_item.get('item_type'):
        if pub_type in keys.keys():
            bib = {'type_': keys[pub_type]['bib_key']}

            for bib_key, papers_key in zip(keys[pub_type]['core'], keys[pub_type]['core_alias']):
                try:
                    bib[bib_key] = article[papers_key]
                except KeyError:
                    try:
                        bib[bib_key] = papers_item['custom_metadata'][papers_key]
                    except KeyError as e:
                        logger.warning(
                            f'{article.get("title", "Unknown title")} misses the attribute {bib_key}.')
                        return {}

        else:
            logger.warning(f'{article.get("title", "Unknown title")} has a type, that does not exist in BibTeX.')
            return {}
    else:
        logger.error(f'{article.get("title", "Unknown title")} has no type.')
        return {}


def query_db(path):
    """
    Connects to the PapersApp DB and fetches all results.
    :param path:
    :return:
    """
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    return list(map(unpack, cur.execute("SELECT t.json from items t where json_extract(t.json, '$.deleted') = FALSE")))
