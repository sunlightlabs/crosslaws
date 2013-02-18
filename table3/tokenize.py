# -*- coding: utf-8 -*-
import logging

# from tater.node import Node, matches, matches_subtypes
from tater.core import RegexLexer, Rule, include
from tater.tokentype import Token


class Tokenizer(RegexLexer):
    DEBUG = logging.INFO

    r = Rule
    t = Token
    dont_emit = (t.Whitespace,)

    tokendefs = {

        'root': [
            include('enumeration'),
            include('subdivs'),
            include('punctuation'),
            include('whitespace'),
            ],

        'punctuation': [
            r(t.Comma, ',')
            ],

        'whitespace': [
            r(t.Whitespace, '\s+'),
            ],

        'enumeration': [
            r(t.Enumeration, u'((?:\w+)(?:\u2013\w+)?)'),
            r(t.Note, 'nt'),
            ],

        'subdivs': [
            r(t.OpenParen, '\(', 'enumeration'),
            r(t.CloseParen, '\)'),
            ]

        }


t = Token

