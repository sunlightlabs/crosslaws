import sys, re, itertools, unicodedata
from collections import OrderedDict

# figure out what kind of line it is
# subexpressions
SUBEXPRESSIONS = {
    'part_label':  r'Part?(?P<plural_parts>s?),?',
    'cfr_sections': r'(?P<cfr_sections>[0-9A-Za-z ,-]+)',
    'cfr': r'(?P<cfr>\d+)',
    'usc_section': r'(?P<usc_section>\w[\w -]*)',
    'usc_title': r'^\d+ U.S.C.[\(\)\w\. ]*$',
}
LINE_TYPES = {
    'title_line': re.compile(r"{usc_title}".format(**SUBEXPRESSIONS)),
    'section_line': re.compile(r"^  [ ]*{usc_section}\.\.+{cfr} {part_label} {cfr_sections}\x03?$".format(**SUBEXPRESSIONS)),
    'part_line': re.compile(r"^   [ ]*{cfr} {part_label} {cfr_sections}$".format(**SUBEXPRESSIONS)),
    'part_line_ctd': re.compile(r"^   [ ]*{cfr_sections}$".format(**SUBEXPRESSIONS)),
}
def classify(line):
    return dict([
        (type, expr.match(line))
    for type, expr in LINE_TYPES.items()])

# actually do work
def parse_ptar(file):
    full_contents = file.read()
    pages = re.compile(r'\[\[[\w\s]+\]\]').split(full_contents)[1:]
    lines = re.compile(r"[\r\n]+").split("\n".join(pages))
    del full_contents, pages
    
    # line types
    
    current_title = None
    current_section = None
    current_cfr = None
    parsed = OrderedDict()
    
    for line in lines:
        if not line.strip():
            continue
        
        classified = classify(line)
        line_data = None

        if classified['title_line']:
            current_title = line
            parsed[current_title] = OrderedDict()
            continue
        
        if classified['section_line']:
            line_data = classified['section_line'].groupdict()
            current_section = line_data['usc_section']
            parsed[current_title][current_section] = OrderedDict()
        
        if classified['section_line'] or classified['part_line']:
            if not line_data:
                line_data = classified['part_line'].groupdict()
            current_cfr = line_data['cfr']
            parsed[current_title][current_section][current_cfr] = []
        
        if any([classified['section_line'], classified['part_line'], classified['part_line_ctd']]):
            if not line_data:
                line_data = classified['part_line_ctd'].groupdict()
            sections_raw = line_data['cfr_sections']
            sections_split = [ref.strip() for ref in sections_raw.split(",")]
            sections = [ref for ref in sections_split if ref]

            parsed[current_title][current_section][current_cfr].extend(sections)
        
        if line == "United States Statutes at Large":
            print 'done for now'
            return parsed
        
        if not any(classified):
            print 'uh-oh', line
            print parsed
            sys.exit(1)

# borrowed from Django
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def add_to_db(parsed):
    from pymongo.connection import Connection
    db = Connection().laws

    for title_name, title in parsed.items():
        for section_name, section in title.items():
            usc_id = '%s:%s' % (slugify(unicode(title_name)), slugify(unicode(section_name)))
            usc_search = list(db.uscs.find({'usc_id': usc_id}))
            
            if usc_search:
                usc = usc_search[0]
            else:
                usc = {
                    'usc_id': usc_id,
                    'title': title_name,
                    'section': section_name,
                    'cfs_ids': []
                }
                db.uscs.save(usc, safe=True)
            
            for cfr_name, cfr in section.items():
                for cfr_part in cfr:
                    cfr_id = '%s:%s' % (slugify(unicode(cfr_name)), slugify(unicode(cfr_part)))
                    cfr_search = list(db.cfrs.find({'cfr_id': cfr_id}))

                    if cfr_search:
                        c = cfr_search[0]
                    else:
                        c = {
                            'cfr_id': cfr_id,
                            'chapter': cfr_name,
                            'section': cfr_part,
                            'usc_ids': []
                        }
                        db.cfrs.save(c, safe=True)
                    
                    db.cfrs.update({'cfr_id': cfr_id}, {'$addToSet': {'usc_ids': usc_id}}, safe=True)
                    db.uscs.update({'usc_id': usc_id}, {'$addToSet': {'cfr_ids': cfr_id}}, safe=True)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parsed = parse_ptar(open(sys.argv[1], 'r'))
        add_to_db(parsed)
    else:
        print "Please specify a file to import."
        sys.exit(1)