#!/usr/bin/env python
import sys,os
sys.path.append(os.path.abspath("../"))
from twisted.scripts.twistd import run
from os.path import join, dirname
from sys import argv
#import scrapyd


def main():
    argv[1:1] = ['-n', '-y', join(dirname(__file__), 'txapp.py')]
    run()

if __name__ == '__main__':
    #StartServices()
    main()
