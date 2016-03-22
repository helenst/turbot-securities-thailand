# -*- coding: utf-8 -*-

import json
import re

import requests
import turbotlib
from pyquery import PyQuery as pq


from company_index import CompanyIndex
from company_page import CompanyPage
from main_index import MainIndex
from utils import strip_whitespace

turbotlib.log("Starting run...")


def find_js_redirect(doc):
    scripts = doc('script')
    for script in scripts:
        if script.text:
            m = re.match(r"document.location\s*=\s*'(?P<url>http://.+)'", script.text)
            if m:
                return m.group('url')




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
