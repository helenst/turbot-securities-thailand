from datetime import date

from company_name_change_page import CompanyNameChangePage


def test_name_change_page():
    html = open('data/namechange.html').read()
    data = CompanyNameChangePage(html).old_names

    assert data == [
        {
            'name': 'UNITED SECURITES PUBLIC COMPANY LIMITED',
            'until': '2013-06-17',
        },
        {
            'name': 'UNITED SECURITES COMPANY LIMITED',
            'until': '1993-12-15',
        }
    ]
