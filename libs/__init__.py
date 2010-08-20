# -*- coding: utf-8 -*-
__author__="PyKaB"
__date__ ="$16.08.2010 17:24:56$"
import os
from os.path import join as j

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

def check_yes_no(var):
    if var.lower() == 'y' or var.lower() == '':
        return True
    return False

def clean_packages_names(p):
    return [r.lower().strip() for r in p]