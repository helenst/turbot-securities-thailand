# -*- coding: utf-8 -*-

from datetime import date

from company_page import CompanyPage


def test_company_page_basic_data():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert data['name'] == 'AEC SECURITIES PUBLIC COMPANY LIMITED'
    assert data['address'] == (
        '63 , ATHENEE TOWER, 15TH, 17TH FL., WIRELESS RD., '
        'LUMPHINI, PATHUM WAN, Bangkok 10330'
    )
    assert data['tel'] == ''
    assert data['fax'] == ''
    assert data['website'] == 'http://www.aecs.com'
    assert data['date_incorporated'] == date(1993, 12, 15)
    assert data['registered_capital'] == '1,331.72 Million Baht'
    assert data['paid_up_capital'] == '1,009.74 Million Baht'


def test_company_page_licenses():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    for entry in [
        {
            'type': '',
            'number': u'ลก-0061-01',
            'business': 'Securities Brokerage',
            'effective_date': date(2014, 1, 31),
            'start_date': date(2014, 1, 31),
            'remark': '',
        },
        {
            'type': '',
            'number': u'ลก-0061-01',
            'business': 'Investment Advisory Services',
            'effective_date': date(2014, 1, 31),
            'start_date': date(2014, 1, 31),
            'remark': '',
        },
        {
            'type': '',
            'number': u'ลก-0061-01',
            'business': 'Securities Borrowing and Lending (Principal Only)',
            'effective_date': date(2014, 1, 31),
            'start_date': date(2014, 5, 20),
            'remark': '',
        },
        {
            'type': '',
            'number': u'ส1-0061-01',
            'business': 'Derivatives Broker',
            'effective_date': date(2014, 2, 20),
            'start_date': date(2014, 2, 20),
            'remark': '',
        },
    ]:
        assert entry in data['licenses']

def test_company_page_shareholders():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert data['major_shareholders'] == [{
        'name': 'Praphol Milindachinla',
        'percentage': 25.06,
    }]

def test_company_page_executives():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert len(data['executives']) == 10

    for entry in [
        {
            'name': 'Mrs. Amporn Jiammunjit',
            'position': 'Manager',
            'nationality': 'Thai',
        },
        {
            'name': 'Mr. Vichya Krea-Ngam',
            'position': 'Director',
            'nationality': 'Thai',
        },
        {
            'name': 'Mr. Paisit Kaenchan',
            'position': 'Independent Director',
            'nationality': 'Thai',
        },
    ]:
        assert entry in data['executives']

def test_company_page_fund_managers():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert data['fund_managers'] == [{
        'name': 'Mr. Anupon Sriard',
        'type': 'mutual',
        'approval_date': date(2013, 9, 20),
        'appointed_date': date(2014, 8, 1),
        'training_deadline': date(2017, 12, 31),
    }]

def test_company_page_head_of_compliance():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert data['head_of_compliance'] == [{
        'name': 'Mr. Kasidit Nuchtan',
        'start_date': date(2015, 5, 6),
    }]

def test_company_page_anti_corruption():
    html = open('data/company.html').read()
    data = CompanyPage(html).data
    assert data['anti_corruption'] == {
        'rating': '3A',
        'description': 'Established by Declaration of Intent',
        'date': date(2016, 3, 17),
    }

