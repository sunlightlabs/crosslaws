'''
R01 - beginning of title title summary (chapter TOC, amendments, table)

I74 - heading (distinct chunk of info follows)


Tables


-------------------
Title Summary

- chapter-title concordance
 I93 "\u2003" - beginning of table
 I70 - left column heading
 I29 - right column heading
 I07 - left column value
 I08 - center column value
 I09 - right column value

-Amendments
 I21 - amendment

-Table (statutes at large)
 c* - column_count, ?, ?, ?, ?, ?
 I95 - beginning of rows
 H1 - column heading
 j - end of table header
 I1 - data like "{td1}\x07{td2}\x07 {td3}"
    ... basically, \x07 marks the column boundary


-Positive Law; Citation
 I21 - paragragh

-Repeals
 I21 - paragragh


---------------------
Chapter Summary

 R10 - beginning of chapter summary
 I81 - flat citation
 
-Table of section numbers, names
 I70 - heading "Sec." for first column
 I20 - row n, cell 0
 I46 - row n, cell 1

-Amendments
 I21 - amendment


--------------------
Section Data
 I80 - section number, like '\xa7 1'
 I89 - section name/title
 I53 - section "source"

- Derivation
 I21 - paragraph

- References in Text (I75)


----------------------
Statute Body
 I11 - root level text
 I12 - level 1
 Q04 - dedent
 


'''

import pdb
import os
from os.path import join, expanduser
from collections import defaultdict
import copy
import itertools

import gpolocator

USCODE_DIR = '~/data/uscode/gpolocator'

def title_filename(title, year_2_digits=10):
    args = map(int, (title, year_2_digits))
    return expanduser(join(USCODE_DIR, 'usc%02d.%02d' % tuple(args)))


class Document(dict):

    def finalize(self):
        '''
        '''
        #pdb.set_trace()
            
        
boundaries = {

    # title
    ('R', '01'): [('I', '93')], 

    # chapter
    ('R', '10'): [('I', '70')],

    # section
    ('I', '80'): [('I', '89'), ('I', '53')],
  
    }

def group(iterator, boundaries=boundaries):
    '''
    Regroup the GPOLocator lines into chunks relating to title, 
    chapters, and sections, each with internal sections grouped into
    'sub documents', for lack of a more imaginitive name. Each document
    contains a list of lines and mapping of code-argument tuples to
    lines with those codeargs. 

    This code is lengthy and convoluted in order to achieve the
    regrouping in a single pass. 
    '''

    I74 = ('I', '74')
    res = []

    lines = []
    subdocs = defaultdict(list)
    codemap = defaultdict(list)
    doc = {'lines': lines, 'docs': subdocs,
           'codemap': codemap} 
    in_subdoc = False
    sub_boundaries = [I74]


    while True:

        try:
            line = next(iterator)
        except StopIteration:
            break


        code, arg = codearg = line[:2]


        if codearg in boundaries:
            sub_boundaries = boundaries[codearg] + [I74]


        starting_complex_table = (code == 'c')


        if codearg in sub_boundaries:# or starting_complex_table:

            # If already in a subdoc, append it
            if in_subdoc:
                subdoc['codemap'] = dict(subdoc['codemap'])
                subdocs[subdoc_id].append(subdoc)

            # Start a new subdoc
            subdoc_lines = [line]
            subdoc_codemap = defaultdict(list, {codearg: [line]})
            if codearg == I74:
                subdoc_id = line.data.strip()
            else:
                subdoc_id = codearg
            subdoc = {'lines': subdoc_lines,
                      'codemap': subdoc_codemap}
            in_subdoc = True


        elif codearg in boundaries:

            if in_subdoc:
                subdoc['codemap'] = dict(subdoc['codemap'])
                subdocs[subdoc_id].append(subdoc)

            # append the current doc
            doc['codemap'] = dict(doc['codemap'])
            res.append(doc)

            # start a new one
            lines = [line]
            codemap = defaultdict(list, {codearg: [line]})
            subdocs = defaultdict(list)
            doc = {'lines': lines, 'docs': subdocs,
                   'codemap': codemap, 'id': codearg} 
            in_subdoc = False
        

        else:
            if in_subdoc:
                subdoc_lines.append(line)
                subdoc_codemap[codearg].append(line)
            else:
                lines.append(line)
                codemap[codearg].append(line)

    return res




if __name__ == "__main__":
    
    filename = title_filename(9, 10)
    fp = open(filename)
    lines = gpolocator.getlines(fp)
    gg = group(lines)

    #import chunks

    #tt = chunks.Title(gg[1])
    #xx = list(tt.chapter_section_toc())
    #xx = tt.amendments()

    pdb.set_trace()
