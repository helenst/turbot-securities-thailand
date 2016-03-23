# -*- coding: utf-8 -*-

from main_index import MainIndexCell


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
