#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__="PyKaB"
__date__ ="$16.08.2010 12:29:27$"
__version__="0.1 pre-alpha"

from pprint import pprint
import argparse
import os
import sys
from os.path import join as j
import packages

sys.path.insert(0, os.getcwd())

def create_dirs(base_path):
    dirs = [
        'apps',
        'media',
        j('3rdparty', 'apps'),
        j('3rdparty', 'libs'),
        j('3rdparty', 'packages'),
    ]

    try:
        for dir in dirs:
            pass
            #os.makedirs( j(base_path, dir) )
    except:
        return False

    return True

def get_packages_list():
    modList = []
    modNames = {}
    _myDir = j(os.getcwd(), 'packages')

    for ii in os.walk(_myDir):
        if ii[0] == _myDir:
            modNames = ii[1]
            break

    for name in modNames:
        if os.path.exists(j(_myDir, name, '__init__.py')): modList.append(name)

    return modList

#TODO
def check_yes_no():
    pass

def clean_packages_names(p):

    return p


if __name__ == "__main__":
    packages = get_packages_list()
    ipackages = []

    parser = argparse.ArgumentParser(prog='LazyPony', description='Setting django environment with useful modules installed and integrated together')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-d', '--output-dir', help='Directory in which django file names will be created (default ".")', default='.', metavar='dest-dir')
    parser.add_argument('-i', '--install', help='List packegages to install', metavar='install-list')
    parser.add_argument('-p', '--show-packages', help='Show all available packages', action='version', version=" ".join(packages) )
    

    try:
        args = parser.parse_args()
    except IOError, msg:
        parser.error(str(msg))

    if args.output_dir == '.':
        var = raw_input("Create django project in '%s'? [Y/N] " % os.getcwd())
        if var.lower() != 'y':
            args.output_dir = raw_input("Directory in which django file names will be created: ")


    if not create_dirs(args.output_dir):
        parser.error('Could\'t create directory "%s"' % args.output_dir)


    if args.install is None:
        for p in packages:
            if p == 'django': continue
            var = raw_input( "Install '%s'? [Y/N] " % p )
            if var.lower() == 'y': ipackages.append(p)
    else:
        ipackages = args.install.split(" ")

    ipackages = clean_packages_names(ipackages)

    #Collect dependencies
    deps = {}
    for p in ipackages:
        try:
            d = __import__('packages.%s.dependencies' % p, globals(), locals(), 'DEPENDENCIES', -1)
            deps[p] = d.DEPENDENCIES
        except ImportError:
            parser.error('Could\'t find packages "%s"' % p)

    pprint(deps)




