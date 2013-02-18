# -*- coding: utf-8 -*-
import re
import logging

# from tater.node import Node, matches, matches_subtypes
from tater.core import RegexLexer, Rule, bygroups, include
from tater.tokentype import Token


class Tokenizer(RegexLexer):
    DEBUG = logging.INFO

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
            r(t.PageBreak, r'\s+\[\[Page (\d+)\]\]\s+'),
            r(t.Heading, r'Memorandums:', 'memorandums'),
            r(t.Heading, r'United States Statutes at Large\r\n',
                pop=2,
                push='stat'),
            r(t.Heading, r'Public Laws\r\n', pop=2, push='publ'),
            r(t.Heading, r'Presidential Documents:', 'presidential_documents'),
            r(t.Heading, r'Proclamations:', pop=True, push='proclamations'),
            r(t.Heading, r'Determinations:', pop=True, push='determinations'),
            r(t.Heading, r'Notices:', pop=True, push='notices'),
            r(t.Heading, r'Executive Orders:', pop=True, push='executive_orders'),
            r(t.Heading, r'Directives:', pop=True, push='directives'),
            r(t.Heading, r'Reorganization Plans:', 'reorganization_plans'),
            r(t.Heading, r'Memorandums:', 'memorandums'),
            ],

        'root': [
            include('meta'),
            include('usc'),
            ],


        'usc': [
            include('meta'),
            include('whitespace'),
            include('linebreaks'),
            r(bygroups(t.USC.Title, t.USC.IRC.Year),
              r'(26) U\.S\.C\. \((\d{4}) I\.R\.C\.\)', ['usc', 'usc.section']),
            r(bygroups(t.USC.Title), r'(\w+) U\.S\.C\.', ['usc', 'usc.section']),
            ],

        'usc.section': [
            include('meta'),

            # If encounter a new title, stay in this state.
            r(bygroups(t.USC.Title, t.USC.IRC.Year),
              r'(26) U\.S\.C\. \((\d{4}) I\.R\.C\.\)'),
            r(bygroups(t.USC.Title), r'(\w+) U\.S\.C\.'),

            # Phrases that occur after sections.
            r(bygroups(t.EtSeq), ' +(et seq)'),
            r(bygroups(t.PrecedingNote), ' +(preceding note)'),
            r(bygroups(t.Note), ' (note)'),

            # Section enumerations.
            r(bygroups(t.USC.Section), r'\x03?\r\n  ((?:\w+)(?:\-\w+)?)'),
            r(bygroups(t.USC.Section), r'  ((?:\w+)(?:\-\w+)?)'),
            r(t.USC.Section, r'((?:\w+)(?:\-\w+)?)'),
            r(t.Range, r'\-\-'),
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

            # Handle situations where's there a continuation on
            # a new line.
            r(bygroups(t.CFR.Title), r'\r\n {3,}(\d+) Parts?'),
            r(bygroups(t.CFR.Part), r'\r\n {3,}((?:\w+)(?:\-\w+)?)'),

            r(t.Range, r'\-\-\r\n\s+'),
            r(t.Range, r'\-\-'),

            # Don't pop if the partial line ends with a comma.
            r(t.Linebreak, r',\r\n'),

            # Otherwise, pop all the way out of cfr state.
            r(t.Linebreak, r'\r\n', pop=2),
            include('whitespace'),
            r(t.Comma, r','),

            # Handle idiot situation where "302-\r\na"
            r(t.CFR.Part, r'((?:\w+)\-\r\n\s+(?:\-\w+)?)'),

            # Handle common case.
            r(t.CFR.Part, '((?:\w+)(?:\-\w+)?)'),
            ],

        'stat': [
            include('meta'),
            r(bygroups(t.Stat.Chapter),
              r'(?:\x03\r\n)?(\w+) Stat\.', 'stat.section'),
            ],

        'stat.section': [
            include('meta'),
            r(bygroups(t.Stat.Chapter),
              r'(?:\x03\r\n)?(\w+) Stat\.'),
            r(bygroups(t.Stat.Page), r'\x03?\r\n  ((?:\w+)(?:\-\w+)?)'),
            r(bygroups(t.Stat.Page), r'\s*((?:\w+)(?:\-\w+)?)'),
            r(t.Range, r'\-\-'),
            r(bygroups(t.EtSeq), ' +(et seq)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],


        'publ': [
            include('meta'),
            r(bygroups(t.Publ.Congress, t.Publ.Number),
              r'(?:\x03\r\n)?(?:  )?(\w+)\-(\w+)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'presidential_documents': [
            include('meta'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'\r\n  (\w+\.?) (\d+), (\w{4})'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'notices': [
            include('meta'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'(?:\r\n)?  (\w+\.?) (\d+), (\w{4})'),
            r(t.Whitespace, ' {3,}', 'cfr'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'proclamations': [
            include('meta'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'(?:\r\n)?  (\w+\.?) (\d+), (\w{4})'),
            r(t.DocumentNumber, '(  )?\d+'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'executive_orders': [
            include('meta'),
            r(bygroups(t.DocumentNumber), '\r\n  ((?:\w+)(?:\-\w+)?)'),
            r(bygroups(t.DocumentNumber), '  ((?:\w+)(?:\-\w+)?)'),
            r(t.DocumentNumber, '((?:\w+)(?:\-\w+)?)'),
            r(t.Range, r'\-\-'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'determinations': [
            include('meta'),
            r(bygroups(t.DocumentNumber),
              '(?:\r\n)?(?:  )?((?:\d\w+)(?:\-\w+)?)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

       'directives': [
            include('meta'),
            include('whitespace'),
            include('linebreaks'),
            r(bygroups(t.Month, t.Day, t.Year), r'(\w+\.?) (\d+), (\w{4})'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'memorandums': [
            include('meta'),
            r(bygroups(t.Month, t.Day, t.Year),
              r'(?:\r\n)?  (\w+\.?) (\d+), (\w{4})'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],

        'reorganization_plans': [
            include('meta'),
            r(bygroups(t.Year, t.DocumentNumber),
              r'(?:\r\n)?(?:  )?(\d{4}) Plan No. (\w+)'),
            r(t.Dots, r'\.{2,}', 'cfr'),
            ],
        }


t = Token


class Ptar(object):

    def __init__(self, text):
        self.text = text

    def raw(self):
        # return self.text[self.text.index('\r\nReorganization Plans:\r\n'):]
        # return self.text[self.text.index('\r\nUnited States Statutes at Large\r\n'):]
        _, text = re.split(r'\[\[Page \d+\]\]', self.text, 1)
        return text


def main():
    with open('ptar/data/parallel_table.txt') as f:
        text = f.read()

    text = Ptar(text).raw()
    tokenizer = Tokenizer()
    for item in tokenizer.tokenize(text):
        print item
        pos, token, text = item
        # import pdb; pdb.set_trace()
        # if 'Determinations' in text:
        #     import pdb; pdb.set_trace()


if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
