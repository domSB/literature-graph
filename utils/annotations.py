# requires pip package pymupdf, BeautifulSoup4
import os
import fitz
from bs4 import BeautifulSoup
import re
from collections import defaultdict


def insert_annotations(pdf_path, html_notes):
    """
    This can be used to write the annotations from zotero back to the pdf. May be useful when moving the directory
    of papers when using zotfile.
    """
    doc = fitz.open(pdf_path)

    with open(html_notes, 'r') as file:
        soup = BeautifulSoup(file.read(), features="html.parser")

    snippets = defaultdict(list)

    paragraphen = soup.find_all('p')
    for paragraph in paragraphen:
        if link := paragraph.find('a'):

            p = int(re.search(r'page=\d+', paragraph.find('a').attrs['href']).group()[5:])
            text = paragraph.text.replace(f" ({link.text})", "")
            if not paragraph.find('i'):  # Highlights are enclosed by ""
                text = text[1:-1]
                snippets[p].append({'text': text})
            else:
                try:
                    snippets[p][-1]['comment'] = text
                except IndexError:
                    print('Wahrscheinlich ein Kommentar ohne Highlight. Überspringen den Ausschnitt.')

    for p, page_snippets in snippets.items():
        page = doc.load_page(p-1)  # Zotero starts counting from 1
        for snippet in page_snippets:
            text_instances = page.search_for(snippet['text'], quads=True)

            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                if comment := snippet.get('comment'):
                    info = annot.info
                    # info["title"] = "word_diffs"
                    info["content"] = comment
                    annot.set_info(info)
                annot.update()

    doc.saveIncr()
