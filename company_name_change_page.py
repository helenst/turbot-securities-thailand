
from pyquery import PyQuery as pq

from utils import parse_date, strip_whitespace


class CompanyNameChangePage(object):

    def __init__(self, content):
        self._content = pq(content)

    @staticmethod
    def _process_row(row):
        name, change_date = row.findall('td')
        return {
            'name': strip_whitespace(name.text).title(),
            'until': parse_date(change_date.text).isoformat(),
        }

    def _process(self):
        name_rows = self._content('.menub tr')[2:]
        self._old_names = [
            self._process_row(row)
            for row in name_rows
        ]

    @property
    def old_names(self):
        if not hasattr(self, '_old_names'):
            self._process()
        return self._old_names
