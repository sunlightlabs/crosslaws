import logbook

from .utils import CachedAttribute
from .schemes import Enum


logger = logbook.Logger()


class Stream(list):

    def __init__(self, iterable):
        self._stream = list(iterable)
        self.i = 0

    def __iter__(self):
        self.i = -1
        while True:
            self.i += 1
            try:
                yield self._stream[self.i]
            except IndexError:
                raise StopIteration

    def next(self):
        i = self.i + 1
        try:
            yield self._stream[i]
        except IndexError:
            raise StopIteration

    def this(self):
        return self[self.i]

    def ahead(self, n):
        return self[self.i + n]

    def behind(self, n):
        return self[self.i - n]


class Node(list):

    def __init__(self, enum, linedata, *kids):
        self.enum = enum
        self.extend(kids)
        self.logger = logbook.Logger(level='DEBUG')

    def __repr__(self):
        return 'Node(%r, %s)' % (self.enum, list.__repr__(self))

    @CachedAttribute
    def _new_child(self):
        '''Return a subclass of this class where the attribute `parent`
        points back to this class, enabling `append` to recursively
        move back up the tree structure if necessary.
        '''
        self_cls = self.__class__
        attrs = dict(parent=self)
        cls = type(self_cls.__name__, (self_cls,), attrs)
        return cls

    def _force_append(self, enum, text, linedata, listappend=list.append):
        '''Append a child node without attempting to judge whether it
        fits or propagating it back up the tree.'''
        new_node = self._new_child(enum, linedata, text)
        listappend(self, new_node)
        self.logger.warn('Append %r to %r' % (enum, self.enum))
        return new_node

    def append(self, enum, text, linedata, ambiguous_enums=map(Enum, 'iI')):

        self_enum = self.enum
        print '>', self_enum, enum, text

        try:
            is_root = self.is_root
        except AttributeError:
            pass
        else:
            if is_root:
                print 'isroot'
                if enum:
                    return self._force_append(enum, text, linedata)
                else:
                    list.append(self, [text, linedata])

        if enum is None:
            return self._force_append(enum, text, linedata)

        if enum.is_first_in_scheme():
            print 'f'
            return self._force_append(enum, text, linedata)

        if enum.was_nested:
            print 'n'
            return self._force_append(enum, text, linedata)

        if enum.could_be_next_after(self_enum):
            print 'c'
            if enum in ambiguous_enums:
                # Put disambiguation logic here.
                pass
            print self.parent
            import pdb;pdb.set_trace()
            return self.parent.append(enum, text, linedata)

        # If we get here, the previous append attempts all failed,
        # so propagate this node up to the current node's parent
        # and start over.
        print 'p'
        return self.parent.append(enum, text, linedata)


class Parser(object):

    def __init__(self, stream):
        stream = Stream(stream)
        node_cls = type('Node', (Node,), dict(stream=stream, parser=self))
        root = node_cls(None, None)
        root.is_root = True
        self.root = root
        self.stream = stream

    def parse(self):
        this = self.root
        for token in self.stream:
            this = this.append(*token)
        return self.root

