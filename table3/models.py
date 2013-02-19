import re
import lxml.html

from tater.core import parse
from tater.tokentype import Token

from crosslaws.table3.ast import Citations
from crosslaws.table3.tokenize import Tokenizer
from crosslaws.table3.ast import *


class Page(object):

    def __init__(self, fn):
        self.fn = fn
        with open(fn) as f:
            self.html = f.read()
            self.doc = lxml.html.fromstring(self.html)

    def _publ(self):
        s = self.doc.xpath('//span[@class="act"]/text()').pop()
        return s.split(u'\u2013')

    @property
    def stat_chapter(self):
        text = self.doc.xpath('//a[@class="header"]/text()')[1]
        return re.search(r'\d+', text).group()

    @property
    def publ_congress(self):
        return self._publ()[0]

    @property
    def publ_number(self):
        return self._publ()[1]

    def entries(self):
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

            # Skip headers.
            if tr[0].tag == 'th':
                continue
            fields = {}

            # Add the raw fields.
            for td in tr.xpath('td'):
                fields[sane_keys[td.attrib['class']]] = td.text_content()
            yield Entry(fields, page=self)


class Entry(object):

    def __init__(self, fields, page):
        self.fields = fields
        self.page = page
        self.citations = Citations()

        tok = Tokenizer().tokenize
        self.fields['act_section_toks'] = list(tok(self.fields['act_section']))
        self.fields['stat_page_toks'] = list(tok(self.fields['stat_page']))
        self.fields['usc_section_toks'] = list(tok(self.fields['usc_section']))

    def stat(self):
        '''Return a Statutes at Large ast like:

         - Stat([])
           - Chapter([(None, Token.Stat.Chapter, '106')])
             - Page([(None, Token.Stat.Chapter, '106')])
        '''
        stat = Stat()
        items = [(None, t.Stat.Chapter, self.page.stat_chapter)]
        chapter = stat.descend(Stat.Chapter, items)
        page = chapter.descend(Stat.Page, self.fields['stat_page_toks'])
        return page.getroot()

    def publ(self):
        '''Return a Public Law ast, like:

        - Publ([])
          - Congress([(None, Token.Publ.Congress, u'102')])
            - Number([(None, Token.Publ.Number, u'391')])
        '''
        publ = Publ()

        items = [(None, t.Publ.Congress, self.page.publ_congress)]
        congress = publ.descend(Publ.Congress, items)

        items = [(None, t.Publ.Number, self.page.publ_number)]
        number = congress.descend(Publ.Number, items)

        return number.getroot()

    def uscode(self):
        '''Return a US Code ast node like:
         - USC([])
           - Title([(None, Token.USC.Title, '22')])
             - Section([(0, Token.Enumeration, '2151u')])
             - Section([(6, Token.Enumeration, 'nt')])
        '''
        title = parse(USC.Title, self.fields['usc_section_toks'])

        items = [(None, t.USC.Title, self.fields['usc_title'])]
        title.extend(items)

        return title.ascend(USC)

    def uscode_status(self):
        return self.fields['usc_status']

    def act(self):

        return parse(Act, self.fields['act_section_toks']).getroot()
