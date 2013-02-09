# -*- coding: utf-8 -*-
import re
import logging

# from tater.node import Node, matches, matches_subtypes
from tater.core import RegexLexer, Rule, bygroups, include
from tater.tokentype import Token
from tater.common import re_divisions, re_enum


class Tokenizer(RegexLexer):
    DEBUG = logging.DEBUG

    # re_skip = r'[,\s]+'

    r = Rule
    t = Token
    dont_emit = (t.Whitespace, t.Linebreak, t.Comma, t.Dots)

    tokendefs = {

        'whitespace': [
            r(t.Whitespace, r'[ ]+'),
            ],

        'linebreaks': [
            r(t.Linebreak, r'\r\n'),
            ],

        'meta': [
            r(t.PageBreak, r'\[\[Page (\d+)\]\]'),
            ],

        'root': [

            include('usc'),
            include('stat'),
            include('publ'),
            include('presidential_documents'),
            include('notices'),
            include('proclamations'),
            include('executive_orders'),
            include('determinations'),
            include('memorandums'),
            include('reorganization_plans'),
            ],

        'usc': [
            include('meta'),
            include('whitespace'),
            include('linebreaks'),
            r(bygroups(t.USC.Title, t.USC, t.USC.IRC.Year),
              r'(26) (U\.S\.C\.) \((\d{4}) I\.R\.C\.\)', 'usc.section'),
            r(bygroups(t.USC.Title, t.USC), r'(\w+) (U\.S\.C\.)', 'usc.section'),
            ],

        'usc.section': [
            include('meta'),
            r(bygroups(t.EtSeq), ' +(et seq)'),
            r(bygroups(t.PrecedingNote), ' +(preceding note)'),
            r(bygroups(t.Note), ' (note)'),
            r(bygroups(t.USC.Section), r'\x03?\r\n  ((?:\w+)(?:\-\w+)?)'),
            r(t.USC.Section, r'((?:\w+)(?:\-\w+)?)'),
            r(t.USC.Section.Range, r'\-\-'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            r(bygroups(t.USC.Appendix), '\s+(Appendix)'),
            ],

        'cfr': [
            include('meta'),
            r(bygroups(t.CFR.Title), '(\d+) Parts?', 'cfr.parts'),
            r(bygroups(t.CFR.Title), '(\d+) Par', 'cfr.parts'),
            r(bygroups(t.CFR.Title), '\s{3,}(\d+) Parts?', 'cfr.parts'),

            # Kooky continuation of previous line.
            r(t.Whitespace, '\s{3,}', 'cfr.parts'),
            ],

        'cfr.parts': [

            include('meta'),
            # Return to cfr on hitting a line break.
            r(bygroups(t.Month, t.Day, t.Notice.Year),
              r'\r\n  (\w+\.?) (\d+), (\w{4})', pop=2),
            r(bygroups(t.USC.Section), r'\r\n  ((?:\w+)(?:\-\w+)?)', pop=2),
            r(t.CFR.Part.Range, r'\-\-\r\n\s+'),
            r(t.CFR.Part.Range, r'\-\-'),
            include('whitespace'),
            r(t.Comma, r','),

            # Handle idiot situation where "302-\r\na"
            r(t.CFR.Part, '((?:\w+)\-\r\n\s+(?:\-\w+)?)'),

            # Handle common case.
            r(t.CFR.Part, '((?:\w+)(?:\-\w+)?)'),
            ],

        'stat': [
            include('meta'),
            r(t.Heading, r'United States Statutes at Large'),
            r(bygroups(t.Stat.Chapter),
              r'(?:\x03\r\n)?(\w+) Stat\.', 'stat.section'),
            ],

        'stat.section': [
            include('meta'),
            r(bygroups(t.Stat.Page), r'\x03?\r\n  ((?:\w+)(?:\-\w+)?)'),
            r(bygroups(t.Stat.Page), r'((?:\w+)(?:\-\w+)?)'),
            r(t.Stat.Page.Range, r'\-\-'),
            r(bygroups(t.EtSeq), ' +(et seq)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],


        'publ': [
            include('meta'),
            r(t.Heading, r'Public Laws', 'publ'),
            r(bygroups(t.Publ.Congress, t.Publ.Number),
              r'(?:\x03\r\n)?(\w+)\-(\w+)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'presidential_documents': [
            r(t.Heading, r'Presidential Documents:',
              push='presidential_documents'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'\r\n  (\w+\.?) (\d+), (\w{4})'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'notices': [
            include('meta'),
            r(t.Heading, r'Notices:', 'notices'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'\r\n  (\w+\.?) (\d+), (\w{4})'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'proclamations': [
            include('meta'),
            r(t.Heading, r'Proclamations:', 'proclamations'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'\r\n  (\w+\.?) (\d+), (\w{4})'),
            r(t.Proclamation.Number, '\d+'),
            r(t.Dots, r'\.{2,}', ['proclamations', 'cfr']),
            ],

        'executive_orders': [
            include('meta'),
            r(t.Heading, r'Executive Orders:', 'executive_orders'),
            ],

        'determinations': [
            include('meta'),
            r(t.Heading, r'Determinations:', 'determinations'),
            ],

        'memorandums': [
            include('meta'),
            r(t.Heading, r'Memorandums:', 'memorandums'),
            ],

        'reorganization_plans': [
            include('meta'),
            r(t.Heading, r'Reorganization Plans:', 'reorganization_plans'),
            ],
        }


t = Token


class Ptar(object):

    def __init__(self, text):
        self.text = text

    def raw(self):
        return self.text[self.text.find('\r\nPresidential Documents:\r\n'):]
        _, text = re.split(r'\[\[Page \d+\]\]', self.text, 1)
        return text

    def iterpages(self):
        return iter(re.split(r'\[\[Page \d+\]\]', self.text)[1:])

    def itersources(self):
        for page in self.iterpages():
            import pdb; pdb.set_trace()




def main():
    with open('ptar/data/parallel_table.txt') as f:
        text = f.read()

    text = Ptar(text).raw()
    for item in Tokenizer().tokenize(text):
        print item
        pos, token, text = item
        # import pdb; pdb.set_trace()
        # if token is t.USC:
        #     import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
