#!/usr/bin/python

"""Translates a string of whitespace-separated integers to CP437 characters"""

import sys
s = sys.stdin.read()
print ''.join(map(lambda x:chr(int(x)),s.split()))