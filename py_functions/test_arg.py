#!/usr/bin/python

import optparse

parser = optparse.OptionParser()
parser.add_option('-a',action='store_true',default=False)
parser.add_option('-b',action='store',dest='b')
parser.add_option('-c',action='store',dest='c')

pdict,remainder = parser.parse_args()

print pdict.a
print pdict.b
print pdict.c

