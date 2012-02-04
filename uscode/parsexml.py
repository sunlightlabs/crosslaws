from os.path import join, expanduser

from lxml import etree
import pdb

DATA = '~/data/uscode/xml/USC_TEST_XML/'

def title_filename(title):
    return expanduser(join(DATA, '%02d.xml' % title))

def data(title):
	with open(title_filename(title)) as f:
		return f.read()



if __name__ == "__main__":
	t9 = data(9)
	pdb.set_trace()