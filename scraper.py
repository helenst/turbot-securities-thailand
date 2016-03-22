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
    if not isinstance(text, (str, unicode)):
        return text
    return text.strip(string.whitespace + u'\u200b\u00a0')

def find_js_redirect(doc):
    scripts = doc('script')
    for script in scripts:
        if script.text:
            m = re.match(r"document.location\s*=\s*'(?P<url>http://.+)'", script.text)
            if m:
                return m.group('url')

def parse_date(text):
    return parse(text, dayfirst=True).date()


class MainIndex(object):
    def __init__(self, content):
        self._content = pq(content)

    @property
    def links(self):
        cells = self._content('.ms-rteTable-sec tr td:last')
        for td in cells:
            for link in MainIndexCell(td).links:
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


class CompanyIndex(object):
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


class Matcher(object):
    @classmethod
    def attempt_match(cls, cell):
        text = strip_whitespace(cell.text())
        match = cls.regex.match(text)
        if match:
            return cls.process(cell, match)


class AddressMatcher(Matcher):
    regex = re.compile(r'''
        Head\ office(?P<address>.+)
        (?:Tel.\s*(?P<tel>[-0-9]*)\s*)
        (?:Fax.\s*(?P<fax>[-0-9]*)\s*)
        \[Click\ HERE                   # next bit of text... ignore
        ''', re.VERBOSE
    )

    @staticmethod
    def process(cell, match):
        return dict(
            address=match.group('address'),
            tel=match.group('tel').strip('-'),
            fax=match.group('fax').strip('-'),
        )

class IncorporationDateMatcher(Matcher):
    regex = re.compile(r'''
        Date\ of\ Incorporation\ :\ (?P<date>.+)
        Registered\ &\ Paid-Up\ Capital
        ''', re.VERBOSE
    )

    @staticmethod
    def process(cell, match):
        incorp_date = parse(strip_whitespace(match.group('date')))
        return dict(
            date_incorporated=incorp_date
        )

class WebsiteMatcher(Matcher):
    regex = re.compile(r'''
        \[Click\ HERE\ for\ History\ of\ Name\ Change\]\ 
        \[Click\ HERE\ for\ Company\ Website\]
        ''', re.VERBOSE
    )

    @staticmethod
    def process(cell, match):
        a = cell.find('a')
        if a:
            return dict(
                website=a[1].attrib['href']
            )

class RegisteredCapitalMatcher(Matcher):
    regex = re.compile('- Registered (?P<capital>.+ Baht)')

    @staticmethod
    def process(cell, match):
        return dict(
            registered_capital=match.group('capital')
        )

class PaidUpCapitalMatcher(Matcher):
    regex = re.compile('- Paid-Up Capital (?P<capital>.+ Baht)')

    @staticmethod
    def process(cell, match):
        return dict(
            paid_up_capital=match.group('capital')
        )


MATCHERS = (
    AddressMatcher,
    IncorporationDateMatcher,
    WebsiteMatcher,
    RegisteredCapitalMatcher,
    PaidUpCapitalMatcher,
)

class CompanyPage(object):
    def __init__(self, content):
        self._content = pq(content)
        self._last_heading = ''

    def _process_basic_data(self, row):
        for matcher in MATCHERS:
            data = matcher.attempt_match(row)
            if data:
                self._data.update({
                    k: strip_whitespace(v)
                    for (k, v) in data.items()
                })
                break

    def _process_securities_license(self, row):
        cells = list(row.items('td'))
        if len(cells) == 6:
            _, _, _, license_type, start_date, _ = cells
            self.data['licenses']['securities'].append({
                'type': license_type.text(),
                'start_date': parse_date(start_date.text())
            })

    def _process_derivatives_license(self, row):
        cells = list(row.items('td'))
        if len(cells) == 6:
            _, _, _, license_type, start_date, _ = cells
            self.data['licenses']['derivatives'].append({
                'type': license_type.text(),
                'start_date': parse_date(start_date.text())
            })

    def _process_major_shareholder(self, row):
        cells = list(row.items('td'))
        if len(cells) == 3:
            _, name, percent = cells
            self.data['major_shareholders'].append({
                'name': name.text().title(),
                'percentage': float(percent.text().strip('%'))
            })

    def _process_executive(self, row):
        cells = list(row.items('td'))
        if len(cells) == 4:
            _, name, position, nationality = cells
            self.data['executives'].append({
                'name': name.text().title(),
                'position': position.text(),
                'nationality': nationality.text().title(),
            })

    def _process_fund_manager(self, row):
        cells = list(row.items('td'))
        if len(cells) == 7:
            _, name, is_mf, is_df, approval, appointed, training = cells
            self.data['fund_managers'].append({
                'name': name.text().title(),
                'type': 'mutual' if is_mf.text() else 'derivative',
                'approval_date': parse_date(approval.text()),
                'appointed_date': parse_date(appointed.text()),
                'training_deadline': parse_date(training.text()),
            })

    def _process_head_of_compliance(self, row):
        cells = list(row.items('td'))
        if len(cells) == 2:
            name, start_date = cells
            self.data['head_of_compliance'].append({
                'name': name.text().title(),
                'start_date': parse_date(start_date.text())
            })

    def _process(self):
        self._data = {
            'name': self._content('.menub .ttr').eq(0).text(),
            'licenses': {
                'securities': [],
                'derivatives': [],
            },
            'major_shareholders': [],
            'executives': [],
            'fund_managers': [],
            'head_of_compliance': [],
        }

        PROCESSORS = (
            (self._data['name'], self._process_basic_data),
            ('Under the Securities & Exchange Act', self._process_securities_license),
            ('Under the Derivatives Act', self._process_derivatives_license),
            ('Approved Major shareholder', self._process_major_shareholder),
            ('Executives', self._process_executive),
            ('Register of persons qualified to be Fund Manager', self._process_fund_manager),
            ('Head of Compliance', self._process_head_of_compliance)
        )

        for row in self._content.items('.menub tr'):
            if row.attr['class'] == 'ttr':
                # main headings
                self._last_heading = row.text()

            elif row.attr['class'] == 'ttr01':
                # subheadings
                pass

            else:
                for heading, process in PROCESSORS:
                    if self._last_heading.startswith(heading):
                        process(row)
                        break
    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._process()
        return self._data

root_url = 'http://www.sec.or.th/EN/MarketProfessionals/Intermediaries/Pages/ListofBusinessOperators.aspx'

if __name__ == '__main__':
    turbotlib.log('Scraping main index %s' % root_url)
    for link in MainIndex(pq(url=root_url)).links:
        # Redirect if necessary
        url = link['url']

        turbotlib.log('Redirecting from %s' % url)
        url = find_js_redirect(pq(url=url)) or url

        turbotlib.log('Scraping company index %s' % url)
        company_index = CompanyIndex(
            pq(url=url),
            title=link['title'],
            parents=link['parents'],
        )
        for company_link in filter(None, company_index.links):
            turbotlib.log('Scraping company page %s' % company_link)
            page = CompanyPage(pq(url=company_link))
            print page.data
            import sys
            sys.exit(0)


#html = open('data/ListofBusinessOperators.aspx').read()
