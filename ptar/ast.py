from tater.node import Node, matches, matches_subtypes
from tater.tokentype import Token


t = Token


class Base(Node):
    '''Handles skippable metadata.
    '''
    @matches(t.PageBreak)
    def handle_pagebreak(self, *items):
        '''Skip this for now.'''
        return self


class Sources(Base):
    '''This will be the root node on the final data structure
    and is also the beginning state of the parse.
    '''
    @matches(t.USC.Title)
    def division_name(self, *items):
        title = self.ascend(USC.Title, items, related=False)
        usc = title.ascend(USC)
        usc.ascend(Sources)
        return title

    @matches((t.Heading, 'United States Statutes at Large\r\n'))
    def start_stat(self, *items):
        return self.descend(Stat)

    @matches((t.Heading, 'Public Laws\r\n'))
    def start_publ(self, *items):
        print 'STARTING PUBL'
        return self.descend(Publ)

    @matches((t.Heading, r'Presidential Documents:'))
    def start_presidential_docs(self, *items):
        print 'STARTING PRES DOCS'
        return self.descend(PresidentialDoc)

    @matches((t.Heading, r'Notices:'))
    def start_notices(self, *items):
        print 'STARTING NOTICES'
        return self.descend(Notices)

    @matches((t.Heading, r'Executive Orders:'))
    def start_exec_orders(self, *items):
        print 'STARTING EXEC ORDERS'
        return self.descend(ExecOrder)

    @matches((t.Heading, r'Determinations:'))
    def start_determinations(self, *items):
        print 'STARTING DETERMINATIONS'
        return self.descend(Determinations)

    @matches((t.Heading, r'Directives:'))
    def start_directives(self, *items):
        print 'STARTING DIRECTIVES'
        return self.descend(Directives)

    @matches((t.Heading, r'Memorandums:'))
    def start_memorandums(self, *items):
        print 'STARTING MEMORANDUMS'
        return self.descend(Memorandum)

    @matches((t.Heading, r'Proclamations:'))
    def start_proclamations(self, *items):
        print 'STARTING PROCLAMATIONS'
        return self.descend(Proclamations)

    @matches((t.Heading, r'Reorganization Plans:'))
    def start_reorg_plans(self, *items):
        print 'STARTING REORG PLANS'
        return self.descend(ReorgPlan)


class CFR(Base):

    class Title(Base):

        @matches(t.CFR.Part)
        def handle_title(self, *items):
            return self.descend(CFR.Part, items)

        @matches(t.CFR.Part)
        def handle_part(self, *items):
            return self.parent.descend(CFR.Part, items)

        @matches(t.CFR.Part, t.Range, t.CFR.Part)
        def handle_part_range(self, *items):
            part1, _, part2 = items
            range_ = self.descend(CFR.Range)
            range_.descend(CFR.Part, part1)
            range_.descend(CFR.Part, part2)
            return range_

        order = [handle_part_range,
                 handle_part]

    class Part(Base):
        '''CFR part'''

    class Range(Part):
        '''CFR range'''


class AuthorizesCFR(Base):
    '''A base class for nodes that provide authority for a
    CFR regulation.
    '''
    @matches(t.CFR.Title)
    def handle_part(self, *items):
        return self.descend(CFR.Title, items)


class USC(Base):
    '''All USC citations will decsend from this node.'''

    @matches(t.USC.Title)
    def handle_title(self, *items):
        print 'title', items[0][-1]
        return self.descend(USC.Title, items)

    @matches(t.USC.Title, t.USC.IRC.Year)
    def handle_title_irc(self, *items):
        print 'title', items[0][-1], 'IRC year', items[1][-1]
        return self.descend(USC.Title, items)

    class Title(Base):

        @matches(t.USC.Appendix)
        def handle_appendix(self, *items):
            return self.descend(USC.Appendix)

        @matches(t.USC.Section, t.Range, t.USC.Section)
        def handle_section_range(self, *items):
            sec1, _, sec2 = items
            range_ = self.descend(USC.Range)
            range_.descend(USC.Section, sec1)
            range_.descend(USC.Section, sec2)
            return range_

        @matches(t.USC.Section, t.Range, t.USC.Section, t.Note)
        def handle_section_range_note(self, *items):
            sec1, _, sec2, note = items
            range_ = self.descend(USC.Range)
            range_.descend(USC.Section, sec1)
            sec2 = range_.descend(USC.Section, sec2)
            sec2.extend(note)
            return range_

        @matches(t.USC.Section)
        def handle_section(self, *items):
            return self.descend(USC.Section, items)

        order = [handle_section_range,
                 handle_section]

    class Appendix(Title):
        '''USC Appendix, behaves just like title.'''
        pass

    class Section(AuthorizesCFR):

        @matches(t.EtSeq)
        def handle_etseq(self, *items):
            return self.extend(items)

        @matches(t.PrecedingNote)
        def handle_preceding_note(self, *items):
            return self.extend(items)

        @matches(t.Note)
        def handle_note(self, *items):
            return self.extend(items)

        @matches(t.USC.Appendix)
        def handle_appendix(self, *items):
            return self.extend(items)

    class Range(Section):
        '''USC range behaves like a section.'''


class Stat(Base):

    @matches(t.Stat.Chapter)
    def handle_chapter(self, *items):
        return self.descend(Stat.Chapter, items)

    class Chapter(Base):

        @matches(t.Stat.Page)
        def handle_page(self, *items):
            return self.descend(Stat.Page, items)

        @matches(t.Stat.Page, t.Range, t.Stat.Page)
        def handle_page_range(self, *items):
            page1, _, page2 = items
            range_ = self.descend(Stat.Range)
            range_.descend(Stat.Page, page1)
            page2 = range_.descend(Stat.Page, page2)
            return range_

        order = [handle_page_range, handle_page]

    class Page(AuthorizesCFR):

        @matches(t.EtSeq)
        def handle_etseq(self, *items):
            return self.extend(items)

    class Range(Page):
        pass


class Publ(Base):

    @matches(t.Publ.Congress, t.Publ.Number)
    def handle_publ(self, *items):
        congress, number = items
        congress = self.descend(Publ.Congress, congress)
        return congress.descend(Publ.Number, number)

    class Congress(Base):
        pass

    class Number(AuthorizesCFR):
        pass


class Year(Node):
    pass


class Month(Node):
    pass


class Day(AuthorizesCFR):
    pass


class HasDate(Base):

    @matches(t.Month, t.Day, t.Year)
    def handle_date(self, *items):
        month, day, year = items
        year = self.descend(Year, year)
        month = year.descend(Month, month)
        day = month.descend(Day, day)
        return day


class PresidentialDoc(HasDate):
    pass


class Notices(HasDate):
    pass


class Directives(HasDate):
    pass


class Memorandum(HasDate):
    pass


class DocumentNumber(AuthorizesCFR):
    pass


class NumberedDocument(AuthorizesCFR):

    class Range(DocumentNumber):
        pass

    @matches(t.DocumentNumber)
    def handle_number(self, *items):
        return self.descend(DocumentNumber, items)

    @matches(t.DocumentNumber, t.Range, t.DocumentNumber)
    def handle_number_range(self, *items):
        doc1, _, doc2 = items
        range_ = self.descend(NumberedDocument.Range)
        range_.descend(DocumentNumber, doc1)
        doc2 = range_.descend(DocumentNumber, doc2)
        return range_

    order = [handle_number_range, handle_number]


class ExecOrder(NumberedDocument):
    pass


class Determinations(NumberedDocument):
    pass


class Proclamations(HasDate, NumberedDocument):
    pass


class ReorgPlan(Base):

    @matches(t.Year)
    def handle_year(self, *items):
        return self.descend(ReorgPlan.Year, items)

    class Year(NumberedDocument):
        pass
