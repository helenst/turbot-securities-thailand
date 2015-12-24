# -*- coding: utf-8 -*-

import json
import datetime
import string
import re

import requests
import turbotlib
from pyquery import PyQuery as pq

turbotlib.log("Starting run...")

def normalize_whitespace(text):
    return " ".join(map(strip_whitespace, text.split()))

def strip_whitespace(text):
    return text.strip(string.whitespace + u'\u200b\u00a0')


class MainIndex(object):
    def __init__(self, content):
        self._content = pq(content)

    def extract_links(self):
        """Extract links from one cell on the index"""
        divs = self._content.items('div')
        levels = []
        for div in divs:
            content = strip_whitespace(div.text())
            if content.startswith(u'\u043e'):
                level = 2
                content = strip_whitespace(content.strip(u'\u043e'))
            elif content.startswith(u'\u2022'):
                level = 3
                content = strip_whitespace(content.strip(u'\u2022'))
            else:
                level = 1

            if level == len(levels):
                levels = levels[:-1]
            elif level < len(levels):
                levels = levels[:level-1]

            link = div.find('a')
            if link:
                url = link[0].attrib['href']
                yield {
                    'title': content,
                    'parents': levels,
                    'url': url,
                }
            else:
                levels.append(content)


class CategoryIndex(object):
    def __init__(self, content, title, parents):
        self._content = pq(content)
        self._title = title
        self._parents = parents

    @staticmethod
    def find_js_redirect(doc):
        scripts = doc('script')
        for script in scripts:
            if script.text:
                m = re.match(r"document.location\s*=\s*'(?P<url>http://.+)'", script.text)
                if m:
                    return m.group('url')

    def process_row(self, row):
        cells = list(pq(row).items('td'))
        if len(cells) != 3:
            return

        _, name_cell, address_cell = cells

        address = address_cell.text()
        tel = ''
        fax = ''
        url = ''

        a = name_cell.find('a')
        if a:
            url = a[0].attrib['href']

        m = re.match('(?P<address>.*)Tel.(?P<tel>.*)Fax.(?P<fax>.*)', address)
        if m:
            address = m.group('address').strip()
            tel = m.group('tel').strip(string.whitespace + '-')
            fax = m.group('fax').strip(string.whitespace + '-')

        return {
            'name': name_cell.text(),
            'address': address,
            'url': url,
            'tel': tel,
            'fax': fax,
            'type': ': '.join(self._parents + [self._title]),
        }


    def get_rows(self):
        return self._content(
            '.rgMasterTable .rgMasterTable tr,'
            '.menub tr'
        )


root_url = 'http://www.sec.or.th/EN/MarketProfessionals/Intermediaries/Pages/ListofBusinessOperators.aspx'

if __name__ == '__main__':
    #html = open('data/ListofBusinessOperators.aspx').read()
    doc = pq(url=root_url)

    info_cells = doc('.ms-rteTable-sec tr td:last')
    for cell in info_cells:
        index = MainIndex(cell)
        for page in index.extract_links():
            url = page['url']
            # Redirect if necessary
            redirect_url = CategoryIndex.find_js_redirect(pq(url=url))
            if redirect_url:
                url = redirect_url

            category = CategoryIndex(
                pq(url=url),
                title=page['title'],
                parents=page['parents'],
            )
            for row in category.get_rows():
                print category.process_row(row)
