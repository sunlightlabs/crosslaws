import os
import pprint
from os.path import abspath, dirname, join

import lxml.html

from crosslaws.table3.tokenize import Tokenizer
from crosslaws.table3.utils import cd


HERE = dirname(abspath(__file__))


class Table3Page(object):

    def __init__(self, fn):
        self.fn = fn
        with open(fn) as f:
            self.html = f.read()
            self.doc = lxml.html.fromstring(self.html)

    def _chapter_page(self):
        s = self.doc.xpath('//span[@class="act"]/text()').pop()
        return s.split(u'\u2013')

    @property
    def chapter(self):
        return self._chapter_page()[0]

    @property
    def page(self):
        return self._chapter_page()[1]

    def rows(self):
        '''Generator of rows from the main table.
        '''
        sane_keys = dict(
            actsection='act_section',
            statutesatlargepage='stat_page',
            unitedstatescodetitle='usc_title',
            unitedstatescodesection='usc_section',
            unitedstatescodestatus='usc_status',
            )
        for tr in self.doc.xpath('//tr'):
            if tr[0].tag == 'th':
                continue
            fields = {}
            for td in tr.xpath('td'):
                fields[sane_keys[td.attrib['class']]] = td.text_content()
            yield fields


def main():

    with cd(join(HERE, 'uscode.house.gov', 'table3')):
        tokenizer = Tokenizer()
        for fn in os.listdir('.'):
            page = Table3Page(fn)
            for row in page.rows():
                tokenize = tokenizer.tokenize
                row['act_section_toks'] = list(tokenize(row['act_section']))
                row['stat_page_toks'] = list(tokenize(row['stat_page']))
                row['usc_section_toks'] = list(tokenize(row['usc_section']))
                pprint.pprint(row)
                import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
