# -*- coding: utf-8 -*-

from datetime import date
from scraper import MainIndexCell, CompanyListing, CompanyPage


def test_main_index_cell_links():
    input_cell = u'''
    <td class="ms-rteTableOddCol-sec" valign="top">
<div><span>Brokerage</span></div>
<div><span>о</span><span>&nbsp;Sercurities Brokerage</span></div>
<div><span>&nbsp;&nbsp;&nbsp;</span><span lang="TH">•</span><span>&nbsp;<span lang="TH"><a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultl_new.php?lic_no=1&amp;ref_id=345"><span lang="EN-US">Securities Company and Other Financial</span><span> </span><span lang="EN-US">Institutions</span></a></span></span></div>
<div><span>&nbsp;&nbsp;&nbsp;</span><span lang="TH">•</span><span lang="TH"> <a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/seclicense/sls-viewcon1.php?act_type=1"><span lang="EN-US">Staff or Agent (individual) Acting as Investor Contact of the</span><span> </span><span lang="EN-US">Company</span></a></span></div>
<div><span>о</span><span>&nbsp;Derivatives<span lang="TH"> </span>Agent</span></div>
<div><span>&nbsp;&nbsp;&nbsp;</span><span lang="TH">•</span><span lang="TH"> <a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=12&amp;ref_id=352"><span lang="EN-US">Licensed Derivatives Broker</span></a></span></div>
<div><span>&nbsp;&nbsp;&nbsp;</span><span lang="TH">•</span><span lang="TH"> <a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=11&amp;ref_id=146"><span lang="EN-US">Registered Derivatives</span><span> </span><span lang="EN-US">Broker</span></a></span><span><span lang="TH"><span>​</span></span></span></div>
<div><span>о</span><span>&nbsp;<span lang="TH"><a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=31&amp;ref_id=203"><span lang="EN-US">Derivatives Advisors</span></a></span></span></div>
</td>
    '''

    links = MainIndexCell(input_cell).links

    assert list(links) == [
        {
            'title': 'Securities Company and Other Financial Institutions',
            'parents': ['Brokerage', 'Sercurities Brokerage'],
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultl_new.php?lic_no=1&ref_id=345',
        },
        {
            'title': 'Staff or Agent (individual) Acting as Investor Contact of the Company',
            'parents': ['Brokerage', 'Sercurities Brokerage'],
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/seclicense/sls-viewcon1.php?act_type=1',
        },
        {
            'title': 'Licensed Derivatives Broker',
            'parents': ['Brokerage', 'Derivatives Agent'],
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=12&ref_id=352',
        },
        {
            'title': 'Registered Derivatives Broker',
            'parents': ['Brokerage', 'Derivatives Agent'],
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=11&ref_id=146',
        },
        {
            'title': 'Derivatives Advisors',
            'parents': ['Brokerage'],
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/allow/comppf_new.php?ino=31&ref_id=203',
        },
    ]

def test_company_listing_get_link():
    row = '''
    <tr class="rgRow" id="ctl00_ContentPlaceHolder1_RadGrid1_ctl00_ctl04_RadGrid11_ctl00__0">
        <td align="center" style="width:5%;">
                                            1
                                        </td><td style="width:25%;"><a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultc_29032549.php?cno=0000000505">AEC SECURITIES PUBLIC CO.,LTD.</a></td><td style="width:70%;">63 , ATHENEE TOWER, 15TH, 17TH FL., WIRELESS RD., LUMPHINI, PATHUM WAN, Bangkok 10330 Tel.- Fax.-</td>
    </tr>
    '''
    index = CompanyListing('<body />', 'page title', ['level 1', 'level 2'])
    result = index.get_link(row)

    assert (
        result ==
        'http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultc_29032549.php?cno=0000000505'
    )

def test_company_page_data():
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
    assert data['date_incorporated'].date() == date(1993, 12, 15)
    assert data['registered_capital'] == '1,331.72 Million Baht'
    assert data['paid_up_capital'] == '1,009.74 Million Baht'
