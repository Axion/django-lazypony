#! /usr/bin/python
# -*- coding: utf-8 -*-
VERSION = (0, 0, 1, "alpha")
__author__="PyKaB"
__date__ ="$16.08.2010 12:29:27$"
__version_ = VERSION.split('.')


from pprint import pprint
import argparse
import os
import sys
from os.path import join as j

from libs import create_dirs, get_packages_list, check_yes_no, clean_packages_names


sys.path.insert(0, os.getcwd())
sys.path.insert(1, j(os.getcwd(), 'libs'))

DEBUG = True


if __name__ == "__main__":
    from libs.terminate.prompt import query
    query("Python rocks? ",(True, False))

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
        if not check_yes_no(var):
            args.output_dir = raw_input("Directory in which django file names will be created: ")


    """
    DEBUG
    """
    if DEBUG:
        from shutil import rmtree
        rmtree(j(os.getcwd(), 'testfolder'), True)
        args.output_dir = j(os.getcwd(), 'testfolder')


    if not create_dirs(args.output_dir):
        parser.error('Could\'t create directory "%s"' % args.output_dir)

    if args.install is None:
        for p in packages:
            if p == 'django': continue
            var = raw_input( "Install '%s'? [Y/N] " % p )
            if check_yes_no(var): ipackages.append(p)
    else:
        ipackages = args.install.split(" ")

    ipackages = clean_packages_names(ipackages)

    #Collect dependencies
    deps = {}
    deps_l = set()
    for p in ipackages:
        try:
            d = __import__('packages.%s.dependencies' % p, globals(), locals(), 'DEPENDENCIES', -1)
            deps[p] = d.DEPENDENCIES
            if not isinstance(d.DEPENDENCIES, str):
                for i in d.DEPENDENCIES:
                    deps_l.add(i)
                continue
            deps_l.add(d.DEPENDENCIES)
        except ImportError:
            parser.error('Could\'t find packages "%s"' % p)

    ipackages.insert(0, 'django')
    deps_l = [i for i in deps_l if i not in ipackages]

    print ""
    print "Installing:"
    print "------------------------------------------------------------------------------------------------------------------------------------"
    for p in ipackages:
        d = __import__('packages.%s.source' % p, globals(), locals(), 'SOURCE', -1)
        print "%-21s    %-20s    %s" % (p, d.SOURCE[3], d.SOURCE[1])

    if deps_l:
        print ""
        print "Installing for dependencies:"
        print "------------------------------------------------------------------------------------------------------------------------------------"
        for p in deps_l:
            d = __import__('packages.%s.source' % p, globals(), locals(), 'SOURCE', -1)
            print "%-21s    %-20s    %s" % (p, d.SOURCE[3], d.SOURCE[1])

    print ""
    print "Transaction Summary"
    print "===================================================================================================================================="
    print "Install      %s Package(s)" % (len(ipackages) + len(deps_l))
    var = raw_input( "Is this ok? [Y/N] " )
    if not check_yes_no(var):
        print "Aborted"
        sys.exit()