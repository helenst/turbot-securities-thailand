import string

from dateutil.parser import parse


def normalize_whitespace(text):
    return " ".join(map(strip_whitespace, text.split()))


def strip_whitespace(obj):
    if isinstance(obj, (str, unicode)):
        return obj.replace(u'\xa0', ' ').strip(string.whitespace + u'\u200b\u00a0')
    elif isinstance(obj, dict):
        return {k: strip_whitespace(v) for (k, v) in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return map(strip_whitespace, obj)
    else:
        return obj


def parse_date(text):
    return parse(text, dayfirst=True).date()


def iso_date(text):
    try:
        return parse_date(text).isoformat()
    except ValueError:
        return ''


def hungry_merge(*lists):
    """
    This merge is hungry for data.

    (Maybe this is an actual thing and there's a better name for it!)

    It's an itemwise merge of multiple lists.

    Later entries are favoured over earlier ones.
    Non-empty values are favoured over empty ones.

    Given a set of items at the same position in their respective lists,
    we take the last non-empty one we find.
    """
    return [next((item for item in items[::-1] if item), '')
            for items in zip(*lists)]
