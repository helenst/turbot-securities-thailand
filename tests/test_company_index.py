from company_index import CompanyIndex


def test_company_index_get_link():
    row = '''
    <tr class="rgRow" id="ctl00_ContentPlaceHolder1_RadGrid1_ctl00_ctl04_RadGrid11_ctl00__0">
        <td align="center" style="width:5%;">
                                            1
                                        </td><td style="width:25%;"><a href="http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultc_29032549.php?cno=0000000505">AEC SECURITIES PUBLIC CO.,LTD.</a></td><td style="width:70%;">63 , ATHENEE TOWER, 15TH, 17TH FL., WIRELESS RD., LUMPHINI, PATHUM WAN, Bangkok 10330 Tel.- Fax.-</td>
    </tr>
    '''
    index = CompanyIndex('<body />', 'page title', ['level 1', 'level 2'])
    result = index.get_link(row)

    assert (
        result == {
            'url': 'http://capital.sec.or.th/webapp/en/infocenter/intermed/comprofile/resultc_29032549.php?cno=0000000505',
            'name': 'AEC SECURITIES PUBLIC CO.,LTD.',
        }
    )
