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


def _gettext(element, recurse=True):
	'''
	Extract text from this element, any child element, and the tail.
	'''
	
	if element.tag == 'quote':
		yield '"%s"' % element.text
	else:
		yield element.text

	if recurse:
		for child in element.getchildren():
			for t in _gettext(child):
				yield t

	tail = element.tail
	if tail and tail.strip():
		yield tail

def gettext(element, recurse=True, join=''.join):
	return join(_gettext(element, recurse))
	

		
#----------------------------------------------------------------------------
#
class Node(object):

	def __init__(self, element):
		self.element = element
		self.find = element.find
		self.findall = element.findall

	@property
	def tag(self):
		'''paragraph, subsection, etc.'''
		return self.element.tag
	type_ = tag

	@property
	def enum(self):
		e = self.element.find('enum')
		if e is not None:
			return e.text.strip('.')

	@property
	def header(self):
		header = self.find('header')
		if header is not None:
			return gettext(header)
		
	@property
	def ref_id(self):
		return self.element.attrib['ref-id']
		
	@property
	def id(self):
		return self.element.attrib['id']

	@property
	def notes(self):
		return map(Note, self.element.find('usc-notes'))

	@property
	def text(self):
		return gettext(self.element)

	@property
	def inline(self):
		attrib = self.element.attrib
		try:
			return not attrib['display-inline'] == 'no-display-inline'
		except KeyError:
			return False
		


#----------------------------------------------------------------------------
#
class Note(Node):

	@property
	def paragraphs(self):
		return map(gettext, self.element.findall('note-text'))


class Section(Node):
	
	def _kids(self, types='text subsection paragraph subparagraph'.split()):
		kids = self.element.getchildren()
		if kids is not None:
			kids = kids[1:]
			for k in kids:
				if k.tag in types:
					yield classes[k.tag](k)

	@property
	def kids(self):
		return list(self._kids())

	def getnote(self, header_or_tag):
		for note in self.notes:
			if note.tag == header_or_tag:
				return note
			if note.header == header_or_tag:
				return note

class Subsection(Section):
	'''
	The Subsection won't recurse into its child notes when we get its text.
	'''
	@property
	def text(self):
		return gettext(self.element, recurse=False)

class Paragraph(Subsection):
	pass

class Subparagraph(Subsection):
	pass

class Text(Subsection):
	pass

classes = {
	'section': Section,
	'subsection': Subsection,
	'paragraph': Paragraph,
	'subparagraph': Subparagraph,
	'text': Text,
 	}

#----------------------------------------------------------------------------
#
class Chapter(Node):

	@property
	def sections(self):
		return map(Section, self.findall('section'))


#----------------------------------------------------------------------------
#
class Title(Node):
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
	t9 = Title(titledata(9))
	nn = t9.chapters[0].sections[1].notes
	ss = t9.sections
	sss = ss[9]
	xx = sss.kids
	hh = sss.find('header')
	pdb.set_trace()