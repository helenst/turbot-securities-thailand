# -*- coding: utf-8 -*-

import json
import string
import re

import requests
import turbotlib
from dateutil.parser import parse
from pyquery import PyQuery as pq

turbotlib.log("Starting run...")

def normalize_whitespace(text):
    return " ".join(map(strip_whitespace, text.split()))

def strip_whitespace(text):
    return text.strip(string.whitespace + u'\u200b\u00a0')

def find_js_redirect(doc):
    scripts = doc('script')
    for script in scripts:
        if script.text:
            m = re.match(r"document.location\s*=\s*'(?P<url>http://.+)'", script.text)
            if m:
                return m.group('url')


class MainIndex(object):
    def __init__(self, content):
        self._content = pq(content)

    @property
    def links(self):
        cells = self._content('.ms-rteTable-sec tr td:last')
        for td in cells:
            for link in MainIndexCell(td).extract_links():
                yield link


class MainIndexCell(object):
    def __init__(self, content):
        self._content = pq(content)

    @property
    def links(self):
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


class CompanyListing(object):
    def __init__(self, content, title, parents):
        self._content = pq(content)
        self._title = title
        self._parents = parents

    @property
    def rows(self):
        return self._content(
            '.rgMasterTable .rgMasterTable tr,'
            '.menub tr'
        )

    def get_link(self, row):
        cells = list(pq(row).items('td'))
        if len(cells) != 3:
            return

        a = cells[1].find('a')
        if a:
            return a[0].attrib['href']

    @property
    def links(self):
        return (
            self.get_link(row)
            for row in self.rows
        )

address_rx = re.compile(r'''
    Head\ office(?P<address>.+)
    (?:Tel.(?P<tel>.*))
    (?:Fax.(?P<fax>.*))
    \[Click\ HERE                   # next bit of text... ignore
    ''',
    re.VERBOSE
)

date_of_incorporation_rx = re.compile(r'''
    Date\ of\ Incorporation\ :\ (?P<date>.+)
    Registered\ &\ Paid-Up\ Capital
    ''',
    re.VERBOSE
)

class CompanyPage(object):
    def __init__(self, content):
        self._content = pq(content)

    def _process_address(self, match):
        self._data.update(
            address=strip_whitespace(match.group('address')),
            tel=strip_whitespace(match.group('tel')).strip('-'),
            fax=strip_whitespace(match.group('fax')).strip('-'),
        )

    def _process_incorporation_date(self, match):
        incorp_date = parse(strip_whitespace(match.group('date')))
        self._data.update(
            date_incorporated=incorp_date
        )

    def _process(self):
        self._data = {
            'name': self._content('.menub .ttr').eq(0).text()
        }

        for cell in self._content('.menub tr'):
            text = strip_whitespace(cell.text_content())
            match = re.match(address_rx, text)
            if match:
                self._process_address(match)

            match = re.match(date_of_incorporation_rx, text)
            if match:
                self._process_incorporation_date(match)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._process()
        return self._data

root_url = 'http://www.sec.or.th/EN/MarketProfessionals/Intermediaries/Pages/ListofBusinessOperators.aspx'

if __name__ == '__main__':
    for link in MainIndex(pq(url=root_url)).links:
        # Redirect if necessary
        url = link['url']
        url = find_js_redirect(pq(url=url)) or url

        for company_link in filter(None, CompanyListing(
            pq(url=url),
            title=link['title'],
            parents=link['parents'],
        ).links):
            page = CompanyPage(pq(url=company_link))
            page.data


#html = open('data/ListofBusinessOperators.aspx').read()
