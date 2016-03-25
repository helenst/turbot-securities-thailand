from pyquery import PyQuery as pq


class CompanyIndex(object):
    def __init__(self, content, title, parents):
        self._content = pq(content)
        self._title = title
        self._parents = parents

    @property
    def rows(self):
        return self._content(
            '.rgMasterTable .rgMasterTable tr,'
            '.menub tr'
        )

    def get_link(self, row):
        cells = list(pq(row).items('td'))
        if len(cells) != 3:
            return

        a = cells[1].find('a')
        if a:
            return {
                'url': a[0].attrib['href'],
                'name': a[0].text,
            }

    @property
    def links(self):
        return (
            self.get_link(row)
            for row in self.rows
        )
