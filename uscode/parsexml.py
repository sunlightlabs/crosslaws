from os.path import join, expanduser
import re

from lxml import etree
import pdb

DATA = expanduser('~/data/uscode/xml/USC_TEST_XML/')

def title_filename(title):
    return join(DATA, '%02d.xml' % title)

def titledata(title):
	with open(title_filename(title)) as f:
		return f.read()



def quotes2text(element, join=''.join):
	'''
	Turn an element like this:
		'Blah blah <quote>More Blah</quote> blah'
	into a string like this:
		'Blah blah "More Blah" blah'
	'''
	quoted = [c.text for c in element.findall('quote')]
	text = [element.text]
	for child in element.getchildren():
		if child.tag in ['text', 'quote']:
			text.append(child.text)

	replacements = dict((q, '"%s"' % q) for q in quoted)
	res = []
	for t in text:
		res.append(replacements.get(t, t))
	return join(res)

class Notes(object):
	pass

		

class Node(object):

	def __init__(self, element):
		self.element = element
		self.find = element.find
		self.findall = element.findall
	
	@property
	def enum(self):
		e = self.element.find('enum').text
		return e.strip('.')

	@property
	def kids(self, types='subsection paragraph subparagraph'.split()):
		for t in types:
			kids = self.findall(t)
			if kids:
				return map(Node, kids)

	@property
	def text(self):
		return quotes2text(self.element)

	@property
	def inline(self):
		attrib = self.element.attrib
		return not attrib['display-inline'] == 'no-display-inline'



class RootNode(Node):

	@property
	def header(self):
		return quotes2text(self.find('header'))

	@property
	def ref_id(self):
		return self.element.attrib['ref_id']

	@property
	def id(self):
		return self.element.attrib['id']

	@property
	def notes(self):
		return Notes(self.element.find('usc-notes'))

	

class Section(RootNode):
	pass


class Chapter(RootNode):

	@property
	def sections(self):
		return map(Section, self.findall('section'))



class Title(RootNode):
	'''
	Has these top-level elements:
	- chapter
	- usc-title [garbage]
	- enacting-note
	- enum
	- title-num
	- header
	- id
	- usc-notes
	'''
	@classmethod
	def from_filename(cls, filename):
		with open(filename) as f:
			return cls(f.read())

	def __init__(self, string):

		element = etree.fromstring(string)
		self.element = element
		self.find = element.find
		self.findall = element.findall

	@property
	def sections(self):
		return map(Section, self.findall('chapter/section'))

	@property
	def text(self):
		pass

	@property
	def chapters(self):
		return map(Chapter, self.findall('chapter'))


			
	




if __name__ == "__main__":
	t9 = Title(data(9))
	ss = t9.sections
	sss = ss[9]
	hh = sss.find('header')
	import xml2dict
	x2d = xml2dict.xml2dict
	pdb.set_trace()