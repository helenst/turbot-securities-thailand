import re

from pyquery import PyQuery as pq

from utils import hungry_merge, iso_date, strip_whitespace


class InfoMatcher(object):
    @classmethod
    def attempt_match(cls, cell):
        text = strip_whitespace(cell.text())
        match = cls.regex.match(text)
        if match:
            return cls.process(cell, match)


class AddressMatcher(InfoMatcher):
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


class IncorporationDateMatcher(InfoMatcher):
    regex = re.compile(r'''
        Date\ of\ Incorporation\ :\ (?P<date>.+)
        Registered\ &\ Paid-Up\ Capital
        ''', re.VERBOSE
    )

    @staticmethod
    def process(cell, match):
        incorp_date = iso_date(strip_whitespace(match.group('date')))
        return dict(
            date_incorporated=incorp_date,
        )


class WebsiteMatcher(InfoMatcher):
    regex = re.compile(r'''
        \[Click\ HERE\ for\ History\ of\ Name\ Change\]\s
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

class RegisteredCapitalMatcher(InfoMatcher):
    regex = re.compile('- Registered (?P<capital>.+ Baht)')

    @staticmethod
    def process(cell, match):
        return dict(
            registered_capital=match.group('capital')
        )

class PaidUpCapitalMatcher(InfoMatcher):
    regex = re.compile('- Paid-Up Capital (?P<capital>.+ Baht)')

    @staticmethod
    def process(cell, match):
        return dict(
            paid_up_capital=match.group('capital')
        )

class AntiCorruptionMatcher(InfoMatcher):
    regex = re.compile(r'''
        Anti-corruption\ Progress\ Indicator\ :\s
        Level\ (?P<rating>\d\w?)\s+\(As\ of\s(?P<date>[\d/]+)\)
        ''', re.VERBOSE
    )

    DESCRIPTIONS = {
        '1': 'Committed',
        '2': 'Declared',
        '3': 'Established',
        '3A': 'Established by Declaration of Intent',
        '3B': 'Established by Committment and Policy',
        '4': 'Certified Level',
        '5': 'Extended',
    }

    @classmethod
    def process(cls, cell, match):
        return dict(
            anti_corruption = dict(
                rating = match.group('rating'),
                description = cls.DESCRIPTIONS.get(match.group('rating')),
                date = iso_date(match.group('date')),
            )
        )

INFO_MATCHERS = (
    AddressMatcher,
    IncorporationDateMatcher,
    WebsiteMatcher,
    RegisteredCapitalMatcher,
    PaidUpCapitalMatcher,
    AntiCorruptionMatcher,
)

class CompanyPage(object):
    def __init__(self, content):
        self._content = pq(content)
        self._last_heading = ''
        self._last_license_row = [''] * 6

    def _process_basic_data(self, row):
        for matcher in INFO_MATCHERS:
            data = matcher.attempt_match(row)
            if data:
                self._data.update({
                    k: strip_whitespace(v)
                    for (k, v) in data.items()
                })
                break

    def _process_license(self, row):
        cells = list(row.items('td'))
        if len(cells) == 6:
            self._last_license_row = hungry_merge(
                self._last_license_row,
                [cell.text() for cell in cells]
            )

            license_type, num, eff_date, business, start_date, remark = self._last_license_row

            self.data['licenses'].append({
                'number': num,
                'effective_date': iso_date(eff_date),
                'type': license_type,
                'business': business,
                'start_date': iso_date(start_date),
                'remark': remark,
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
                'approval_date': iso_date(approval.text()),
                'appointed_date': iso_date(appointed.text()),
                'training_deadline': iso_date(training.text()),
            })

    def _process_head_of_compliance(self, row):
        cells = list(row.items('td'))
        if len(cells) == 2:
            name, start_date = cells
            self.data['head_of_compliance'].append({
                'name': name.text().title(),
                'start_date': iso_date(start_date.text()),
            })

    def _process(self):
        self._data = {
            'name': self._content('.menub .ttr').eq(0).text(),
            'licenses': [],
            'major_shareholders': [],
            'executives': [],
            'fund_managers': [],
            'head_of_compliance': [],
        }

        PROCESSORS = (
            (self._data['name'], self._process_basic_data),
            ('Under the Securities & Exchange Act', self._process_license),
            ('Under the Derivatives Act', self._process_license),
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
