#-*- coding: utf-8 -*-

import pydoc
import sys
import os
import subprocess

#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__basedir__=os.path.dirname(__rootpath__)
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)


if __name__=='__main__':
    #generate docks for all scripts in this module
    #pydoc.writedocs(__rootpath__)
    dirpath=os.path.dirname(__rootpath__)
    os.chdir(dirpath)
    #cmdlis=['python','-m','pydoc','-b',os.path.basename(__rootpath__)]
    cmdlis=['python','-m','pydoc','-b',dirpath]
    process = subprocess.Popen(cmdlis, stdout=subprocess.PIPE, encoding='utf-8',stderr=subprocess.STDOUT)
    while True:
        realtime_output = process.stdout.readline()
        if realtime_output == '' and process.poll() is not None:
            break
        if realtime_output:
            print(realtime_output.strip(), flush=True)
