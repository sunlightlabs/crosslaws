from os.path import expanduser
import pdb
import urllib2
import datetime

from lxml.html import fromstring

filename = expanduser('~/data/uscode/popularnames/popularnames.htm')
url = 'http://uscode.house.gov/popularnames/popularnames.htm'

def getdata():
    try:
      with open(filename) as f:
        return f.read()
    except IOError:
      return urllib2.urlopen(url).read()



#----------------------------------------
# try to parse the citations
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *

class CiteLexer(RegexLexer):
    '''
    'Pub. L. 95-272, title I, May 3, 1978, 92 Stat. 222 (20 U.S.C. 951 note)'
    '''
    publ = Token.PublicLaw
    stat = Token.StatutesAtLarge
    junk = Token.Junk
    usc  = Token.USCode
    date = Token.Date

    # I'm surely misusing pygments in one or more ways...
    tokens = {
        'root': [

            (r'Pub\. L\. (\d+)-(\d+)', bygroups(publ.Congress, publ.Law), 'publ'),
            (r'[A-Z][a-z]{2,3}\.? \d{,2}, \d{4}', date, ('#pop', 'stat')),
             (r'(\d+) U\.S\.C\. (\S+)', bygroups(usc.Title, usc.Section), 'usc'),
            (r', ', junk),
            ],

        'publ': [
            (r', ', junk),
            (r'div\. (\w+)', bygroups(publ.Division)),
            (r'title (\w+)', bygroups(publ.Title)),
            (r'part (\w+)', bygroups(publ.Part)),
            (r'subtitle (\w+)', bygroups(publ.Subtitle)),
            (r'\(Sec. (\S+)( et seq\.)?\)', bygroups(publ.Section, publ.EtSeq)),
            (r'Sec\. (\w+)', bygroups(publ.Section)),
            (r', ', junk),

            (r'as added Pub. L. (\d+)\-(\d+)', 
             bygroups(publ.AsAdded.Congress, publ.AsAdded.Law), ('#pop', 'as_added')),
        
            (r'[A-Z][a-z]{2,3}\.? \d{,2}, \d{4}', date, ('#pop', 'stat')),
            ],

       'as_added': [
            (r', ', junk),
            (r'div\. (\w+)', bygroups(publ.AsAdded.Division)),
            (r'title (\w+)', bygroups(publ.AsAdded.Title)),
            (r'part (\w+)', bygroups(publ.AsAdded.Part)),
            (r'subtitle (\w+)', bygroups(publ.AsAdded.Subtitle)),
            (r'\(Sec. (\S+)( et seq\.)?\)', bygroups(publ.AsAdded.Section, publ.AsAdded.EtSeq)),
            (r'Sec\. (\w+)', bygroups(publ.AsAdded.Section)),
            (r'[A-Z][a-z]{2,3}\.? \d{,2}, \d{4}', date, ('#pop', 'stat')),
          ],

       'stat': [ 
            (r', ', junk),
            (r'(\d+) Stat\. (\S+)', bygroups(stat.Volume, stat.Page)),
            (r'div\. (\w+)', bygroups(stat.Division)),
            (r'title (\w+)', bygroups(stat.Title)),
            (r'part (\w+)', bygroups(stat.Part)),
            (r'ch\. (\d+)', bygroups(stat.Chapter)),
            (r'\(Sec. (\S+)( et seq\.)?\)', bygroups(stat.Section, stat.EtSeq)),
            (r' \((\d+) U\.S\.C\. (\S+)', bygroups(usc.Title, usc.Section), ('#pop', 'usc')),
            ],
 
    'usc': [
            (r'et seq\.', usc.EtSeq),
            (r'note', usc.Note),
            (r'prec\. ([^)]+)', bygroups(usc.Prec)),
            (r' ', junk),
            (r'\)', junk),
            ]
        }



def parse(html):

    data = []
    doc = fromstring(html)
    entries = doc.xpath('//div[@class="popular-name-table-entry"]')

    paths = (('name', 'popular-name/text()'),
             ('info', 'p[@class="popular-name-information"]/text()'))
 
    for e in entries:
        res = {}
        res['name'] = e.xpath('popular-name/text()')[0]
        for child in e.xpath('p[@class="popular-name-information"]'):
            res[child.attrib['id']] = child.text
        data.append(res)

    return data


def regroup(tokens):
    junk = ('error', 'junk',)
    res = {}
    for pos, token, data in tokens:
        bits = str(token).lower().split('.')
        _res = res
        for key in bits[1:-1]:
            if key in junk:
                continue
            try:
                _res = _res[key]
            except KeyError:
                _res[key] = {}
                _res = _res[key]

        key = bits[-1]
        if key not in junk:
            _res[bits[-1]] = data

    try:
        date = res['date']
    except KeyError:
        print 'stupid date'
        print tokens
        pdb.set_trace()
        return 

    for x, y in (('Sept', 'Sep.'),
                 ('June', 'Jun.'),
                 ('July', 'Jul.'),
                 ('..', '.')):
        date = date.replace(x, y)
    
    try:
        res['date'] = datetime.datetime.strptime(date, '%b. %d, %Y')
    except ValueError:
        res['date'] = datetime.datetime.strptime(date, '%B %d, %Y')
    

    return res


def parsed():
    return parse(getdata())


cites = lambda: (x['cite'] for x in parsed() if 'cite' in x)

parse_citation = lambda c: list(CiteLexer().get_tokens_unprocessed(c))


if __name__ == "__main__":
  #data = parse()
  #for d in data:
  # if 'cite' in d:
  #   print d['cite']
    t = 'Pub. L. 106-450, title II, Nov. 7, 2000, 114 Stat. 1941 (16 U.S.C. 5721 et seq.)'
    import pprint
    for c in cites():
        #print c
        #pprint.pprint(parse_citation(c))
        #pprint.pprint(regroup(parse_citation(c)))
        regroup(parse_citation(c))
        #ans = raw_input('step?')
        if 0:
            p = parse_citation(c)
            pdb.set_trace()
            regroup(p)
    pdb.set_trace()

