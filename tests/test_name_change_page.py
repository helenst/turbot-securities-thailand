from datetime import date

from company_name_change_page import CompanyNameChangePage


def test_name_change_page():
    html = open('data/namechange.html').read()
    data = CompanyNameChangePage(html).old_names

    assert data == [
        {
            'name': 'United Securites Public Company Limited',
            'until': date(2013, 6, 17),
        },
        {
            'name': 'United Securites Company Limited',
            'until': date(1993, 12, 15),
        }
    ]
