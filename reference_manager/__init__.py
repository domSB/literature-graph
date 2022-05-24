import re
import os

from reference_manager.papersapp import query_papers_db
from reference_manager.zotero import query_zotero_db


def query_db(path: str):
    """
    simplifing function. Estimates the reference manager from the path and calls the correct method.
    May fail if the files are renamed or moved.
    :param path:
    :return:
    """
    if re.search('[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}.db', path) is not None:
        return query_papers_db(path)
    elif os.path.basename(path) == 'zotero.sqlite':
        return query_zotero_db(path)
    else:
        raise NotImplementedError('reference manager not supported or not correctly detected.')


__all__ = [query_papers_db, query_db]
