# -*- coding: utf-8 -*-

import json
import re
import time
from datetime import datetime

import turbotlib
from pyquery import PyQuery as pq


from company_index import CompanyIndex
from company_page import CompanyPage
from company_name_change_page import CompanyNameChangePage
from main_index import MainIndex

turbotlib.log("Starting run...")


def find_js_redirect(doc):
    scripts = doc('script')
    for script in scripts:
        if script.text:
            m = re.match(r"document.location\s*=\s*'(?P<url>http://.+)'", script.text)
            if m:
                return m.group('url')


root_url = 'http://www.sec.or.th/EN/MarketProfessionals/Intermediaries/Pages/ListofBusinessOperators.aspx'


def wait():
    time.sleep(0.5)

if __name__ == '__main__':
    processed_urls = set()

    turbotlib.log('Scraping main index %s' % root_url)
    for link in MainIndex(pq(url=root_url)).links:
        # Redirect if necessary
        url = link['url']

        turbotlib.log('Redirecting from %s' % url)
        url = find_js_redirect(pq(url=url)) or url

        wait()
        turbotlib.log('Scraping company index %s' % url)
        company_index = CompanyIndex(
            pq(url=url),
            title=link['title'],
            parents=link['parents'],
        )

        for company_link in filter(None, company_index.links):
            company_url = company_link['url'].replace("&flag=HD", "")
            if company_url in processed_urls:
                continue

            wait()
            turbotlib.log('Scraping company page %s' % company_url)
            page = CompanyPage(pq(url=company_url))
            data = page.data

            data['name'] = company_link['name']
            data['sample_date'] = datetime.now().isoformat()
            data['source_url'] = company_url
            processed_urls.add(company_url)

            name_change_link = re.sub(
                r'/resultc_\d+.php\?cno=(?P<id>\d+)',
                lambda m: '/showcomphist.php?cno=' + m.group('id'),
                company_url
            )

            wait()
            turbotlib.log('Scraping company name change page %s' % name_change_link)
            page = CompanyNameChangePage(pq(url=name_change_link))
            data['old_names'] = page.old_names

            print json.dumps(data)


#html = open('data/ListofBusinessOperators.aspx').read()
