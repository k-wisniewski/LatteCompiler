#!/usr/bin/env python
import os
import sys
import re
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
import latc

def main(argv=None):
    for i in (x for x in os.listdir('lattests/good/') if re.match('.*\.lat', x)):
        if latc.main(['latc.py', 'lattests/good/%s' % i, '-j %s/lib/jasmin.jar' % parentdir, '-v']):
            print 'Error'

if __name__ == '__main__':
    sys.exit(main())
