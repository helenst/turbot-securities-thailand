import string

from dateutil.parser import parse


def normalize_whitespace(text):
    return " ".join(map(strip_whitespace, text.split()))


def strip_whitespace(text):
    if not isinstance(text, (str, unicode)):
        return text
    return text.strip(string.whitespace + u'\u200b\u00a0')


def parse_date(text):
    return parse(text, dayfirst=True).date()
