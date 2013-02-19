from tater.node import Node, matches
from tater.tokentype import Token


t = Token


class Source(Node):
    pass


class Citations(Node):
    pass


class HasSubdivisions(Node):
    '''This class can be mixed in to provide generic subdivisions
    path parsing.
    '''
    t = Token
    division_cls = None

    @matches(t.OpenParen, t.Enumeration, t.CloseParen)
    def handle_subdiv(self, *items):
        open_paren, enum, close_paren = items
        child = self.descend(self.__class__, enum)

        # Regardless of depth, keep a reference to the top-level
        # section this subdivision belongs to.
        child.majornode = getattr(self, 'majornode', self)
        return child


class Act(Node):

    class Division(HasSubdivisions):

        @matches(t.Comma)
        def handle_comma(self, *items):
            return self.majornode

    @matches(t.Enumeration)
    def handle_enum(self, *items):
        return self.descend(Act.Division, items)


class Stat(Node):

    class Chapter(Node):

        @matches(t.Enumeration)
        def handle_enum(self, *items):
            return self.descend(Stat.Page, items)

    class Page(Node):
        pass


class USC(Node):
    '''All USC citations will decsend from this node.'''

    class Title(Node):

        @matches(t.Enumeration)
        def handle_section(self, *items):
            return self.descend(USC.Section, items)

    class Section(Node):

        @matches(t.Note)
        def handle_note(self, *items):
            return self.extend(items)


class Publ(Node):

    class Congress(Node):
        pass

    class Number(Node):
        pass
