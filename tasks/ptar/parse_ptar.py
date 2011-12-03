import sys, re, itertools

# figure out what kind of line it is
LINE_TYPES = {
    'title_line': re.compile("^\d+ U.S.C.$"),
    'section_line': re.compile(r"^  (?P<section>[\w-]+)\.+(?P<cfr>\d+) Part(?P<plural_parts>s?) (?P<cfr_sections>[0-9a-z ,-]+)$"),
    'part_line': re.compile("^   [ ]*(?P<cfr>\d+) Part(?P<plural_parts>s?) (?P<cfr_sections>[0-9a-z ,-]+)$"),
    'part_line_ctd': re.compile("^   [ ]*(?P<cfr_sections>[0-9a-z ,-]+)$"),
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
    parsed = {}
    
    for line in lines:
        if not line.strip():
            continue
        
        classified = classify(line)
        print line, classified
        if classified['title_line']:
            parsed[line] = {}
            current_title = line
        elif classified['section_line']:
            print 'section_line', classified['section_line'].groupdict()
        elif classified['part_line']:
            print 'part_line', classified['part_line'].groupdict()
        elif classified['part_line_ctd']:
            print 'part_line_ctd', classified['part_line_ctd'].groupdict()
        else:
            print 'uh-oh', line
            print parsed
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_ptar(open(sys.argv[1], 'r'))
    else:
        print "Please specify a file to import."
        sys.exit(1)