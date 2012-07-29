import sys

from gpolocator.parser import getlines
from gpolocator.grouper import group
from gpolocator.utils import title_filename
from gpolocator.structure import Parser

def main():
    filename = title_filename(11, 11)
    fp = open(filename)
    lines = getlines(fp)
    gg = group(lines)

    ss = gg[int(sys.argv[1])].instance
    bb = ss.body_lines()
    xx = Parser(bb)
    qq = xx.parse()

    import pdb;pdb.set_trace()
    for doc in gg:
        x = doc.instance
        print x
        import pdb;pdb.set_trace()


if __name__ == '__main__':
    main()
