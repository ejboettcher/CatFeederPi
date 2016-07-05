#!/usr/bin/env python
"""
Usage: servo.py [--verbose] [--dry-run] 
                (--right|--left|--both|--donna|--marilyn)
                [PORTION-TIME]
       servo.py [PORTION-TIME]
                
       servo.py --help  

Arguments:
 PORTION-TIME          time allocated for each portion [1.0]

Options:
 -h --help             show this help message and exit
 -v --verbose          turn on verbose mode
 -d --dry-run          dry-run, print out actions, but don't act
 -r --right --marilyn  feed marilyn on right
 -l --left --donna     feed donna on left
 -b --both             feed both
"""
from docopt import docopt
docopt_args = docopt(__doc__)
print docopt_args

