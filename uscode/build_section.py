'''
R01 - beginning of title title summary (chapter TOC, amendments, table)
R10 - beginning of chapter summary (i.e., 9 USC ch 1)
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

 R10 - beginning of new section
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

import gpolocator

USCODE_DIR = '~/data/uscode/gpolocator'

def title_filename(title, year_2_digits=10):
    args = map(int, (title, year_2_digits))
    return expanduser(join(USCODE_DIR, 'usc%02d.%02d' % tuple(args)))




if __name__ == "__main__":
    
    filename = title_filename(9, 10)
    fp = open(filename)
    lines = gpolocator.getlines(fp)
    pdb.set_trace()
