import os
import re
import sys
import sqlite3
import logging
from typing import List, Union

import html2text

from models.object_mapping import Item, Article, Book, BookSection, ConferencePaper, Annotation
from utils import Colours, color_names

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger = logging.getLogger('zotero')
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def merge_data_of_item(item_id, item_type, conn) -> Union[Item, None]:
    i_cur = conn.cursor()
    authors = [name[0] for name in i_cur.execute("""
    SELECT firstName || ' ' ||lastName from itemCreators ic
    LEFT join creators c on ic.creatorID = c.creatorID
    WHERE ic.itemID == ? and ic.creatorTypeID == 8
    ORDER BY orderIndex
    """, (item_id,)).fetchall()]

    field_query = """
    SELECT value FROM itemData itD
    LEFT JOIN itemDataValues iDV on itD.valueID = iDV.valueID
    WHERE itD.fieldID == ? and itD.itemID == ?
    """

    title = i_cur.execute(field_query, (1, item_id)).fetchone()[0]

    if date_str := i_cur.execute(field_query, (6, item_id)).fetchone():
        year = int(re.search(r'\d\d\d\d-\d\d-\d\d', date_str[0]).group(0)[0:4])
    else:
        logger.warning(Colours.red + f"The important field year is missing. [skipping item]" +
                       Colours.reset + f" {', '.join(authors)} (???) {title}")
        return

    # creatortype 8 is author
    # fields 6 is date
    # DOI - 58
    # ToDo: Assert hard coded structure once.
    if item_type == 'book':
        if publisher := i_cur.execute(field_query, (23, item_id)).fetchone():
            reference = Book(author=authors, title=title, year=year, publisher=publisher[0])
        else:
            logger.warning(Colours.red + f"The important field publisher is missing. [skipping item]" +
                           Colours.reset + f" {', '.join(authors)} ({year}) {title}")
            return

    elif item_type == 'conferencePaper':
        if proceedings_title := i_cur.execute(field_query, (56, item_id)).fetchone():
            reference = ConferencePaper(author=authors, title=title, year=year, booktitle=proceedings_title[0])
        else:
            logger.warning(Colours.red + f"The important field proceedings title is missing. [skipping item]" +
                           Colours.reset + f" {', '.join(authors)} ({year}) {title}")
            return

    elif item_type == 'journalArticle':
        if journal := i_cur.execute(field_query, (37, item_id)).fetchone():
            reference = Article(author=authors, title=title, year=year, journal=journal[0])
        else:
            logger.warning(Colours.red + f"The important field journal is missing. [skipping item]" +
                           Colours.reset + f" {', '.join(authors)} ({year}) {title}")
            return

    elif item_type == 'bookSection':
        publisher = i_cur.execute(field_query, (23, item_id)).fetchone()
        book_title = i_cur.execute(field_query, (44, item_id)).fetchone()
        if publisher and book_title:
            reference = BookSection(author=authors, title=title, year=year, publisher=publisher, booktitle=book_title)
        else:
            logger.warning(Colours.red + f"The important field publisher oder book title is missing. [skipping item]" +
                           Colours.reset + f" {', '.join(authors)} ({year}) {title}")
            return
    else:
        raise NotImplementedError('Item Type not yet supported.')

    tags = [tag[0] for tag in i_cur.execute("""
    SELECT name from itemTags itT 
    inner join tags t on t.tagID = itT.tagID
    WHERE itT.itemID == ?
    """, (item_id, )) if not tag[0].startswith('_')]

    annotations = [Annotation(
                text=text,
                comment=comment or '',
                colour=color_names.get(color),
                page=page
            ) for text, comment, color, page in i_cur.execute("""
    SELECT text, comment, color, pageLabel FROM itemAnnotations WHERE parentItemID = ?
    """, (item_id, ))]

    notes = [Annotation(
        text='',
        comment=html2text.HTML2Text().handle(note[0]),
        colour='',
        page=0
    ) for note in i_cur.execute("""
        SELECT note FROM itemNotes WHERE parentItemID = ?
        """, (item_id,)) if 'data-citation-items' not in note[0]]
    # data-citation-items is a js-tag in a special note, that just recaptures annotations within the pdf

    # TODO: Leverage possible references between notes in Zotero.
    annotations.extend(notes)

    doi = i_cur.execute(field_query, (58, item_id)).fetchone()
    if doi is not None:
        identifier = '<doi>' + doi[0]
    else:
        identifier = '<zotero>' + str(item_id)

    return Item(bib=reference, annotations=annotations, identifier=identifier, tags=tags)


def query_zotero_db(path: str = 'C:/Users/Dominic/Zotero/zotero.sqlite') -> List[Item]:
    """
    Connects to the Zotero DB and fetches all results.
    :param path:
    :return:
    """
    assert os.path.isfile(path), Colours.red + f"The provided path is not valid. \n" + Colours.reset + path
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        item_ids = cur.execute("""
        SELECT it.itemID, typeName FROM items it
        INNER JOIN (SELECT itemTypeID, typeName FROM itemTypes 
        WHERE typeName in ('book', 'bookSection', 'conferencePaper', 'journalArticle')
        ) itypes on it.itemTypeID = itypes.itemTypeID order by typeName;
        """)
    except sqlite3.OperationalError:
        logger.warning(Colours.red + f"Database looks locked. Is Zotero still open? Please close the application." +
                           Colours.reset)
        sys.exit('Execution stopped')
    item_gen = (merge_data_of_item(item_id, item_type, conn) for item_id, item_type in item_ids)

    return list(filter(None, item_gen))


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    complete_items = query_zotero_db(os.getenv('ZOTERO_DB_PATH'))
