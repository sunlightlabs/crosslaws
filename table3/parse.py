'''Next, handle revised stats pages in a way that makes sense.
'''
import os
from os.path import abspath, dirname, join

from crosslaws.table3 import models
from crosslaws.table3.utils import cd


HERE = dirname(abspath(__file__))


def main():

    with cd(join(HERE, 'uscode.house.gov', 'table3')):
        for fn in os.listdir('.'):
            page = models.Page(fn)
            for entry in page.entries():
                import pprint
                pprint.pprint(entry.fields)
                entry.stat().printnode()
                entry.publ().printnode()
                entry.uscode().printnode()
                entry.act().printnode()
                # import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
