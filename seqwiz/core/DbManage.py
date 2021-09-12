#-*- coding: utf-8 -*-

#basic information
__appnm__='DbManage'
__appver__='1.0'
__appdesc__='Database management: create and update sequence database from other source'

#load internal packages
import sys
import os
import json
import argparse
import shutil

#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)
sys.path.append(os.path.join(__rootpath__,'..','mods'))

#load local packages
from cmdbase import *
from dbbase import *
from fastabase import *
from tabbase import *


if __name__=='__main__':
    # __rootpath__ 
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('dbnm',help='Database name')
    aparser.add_argument('dbver',help='Database version')
    aparser.add_argument('-m','--mact',required=True,choices=['create','update'],help='Management type')
    aparser.add_argument('-i','--ipfi',help='Input sequence file (absolute path)')
    aparser.add_argument('-f','--sfmt',choices=['fasta','peff'],help='Sequence file format')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta file')
    aparser.add_argument('-c','--cver',action='store_true',help='make this as the current version')
    aparser.add_argument('-s','--sqpd',action='store_true',help='Create SQPD sequence database using SeqConvert')
    aparser.add_argument('-a','--annot',action='store_true',help='Performing sequence annotation (calculating protein properties) using SeqAnnotate')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    argnms=aparser.parse_args()
    dbnm=argnms.dbnm
    dbver=argnms.dbver
    mact=argnms.mact
    ipfi=argnms.ipfi
    sfmt=argnms.sfmt
    paru=argnms.paru
    cver=argnms.cver
    sqpd=argnms.sqpd
    annot=argnms.annot
    pdir=checkdir(os.path.join(__rootpath__,'..','seqdbs','others'))
    tmpdir=checkdir(os.path.join(__rootpath__,'..','data','dbdir'))
    dbdir=os.path.join(pdir,dbnm)
    #check version dir
    verdir=os.path.join(dbdir,dbver)
    if mact=='create':
        verdir=checkdir(verdir,1)
    elif mact=='update':
        dbdir=checkdir(dbdir)
    #os.makedirs(verdir)
    #create tmp dir
    shutil.copytree(tmpdir,verdir)
    loginfo('Database directory created for %s (v%s)'%(dbnm,dbver))
    if ipfi:
        ipfi=checkfile(ipfi)
        if sfmt=='fasta':
            clsdir=os.path.join(verdir,'classic','fasta')
            if not paru:
                loginfo('Parser rule key required for fasta file: [%s]!'%ipfi,'Error',isexit=1)
        elif sfmt=='peff':
            paru='PEFF'
            clsdir=os.path.join(verdir,'classic','peff')
        clsfi=os.path.join(clsdir,'%s.%s'%(paru,sfmt))
        #clsfi=os.path.join(clsdir,'sequences.%s'%sfmt)
        shutil.copy(ipfi,clsfi)
        loginfo('Sequence file created: %s'%clsfi)
        #prules={'ID':PRDIC['UID']['PRO'][paru]}
        #prfina=os.path.join(clsdir,'parser.json')
        #dic2json(prules,prfina)
        if cver:
            cvdic={'current':dbver}
            cvfi=os.path.join(dbdir,'current.json')
            dic2json(cvdic,cvfi)
        os.chdir(__rootpath__)
        #convert to sqpd
        if sqpd:
            #sqdir=os.path.join(verdir,'next','sqpd')
            cmdlis=['python','SeqConvert.py',clsfi,'-t','%s2sqpd'%sfmt,'-r',paru]
            runcmd(cmdlis)
        #sequence annotation
        if annot:
            #tbdir=os.path.join(verdir,'classic','table')
            cmdlis=['python','../adds/SeqAnnotate.py',clsfi,'-t',sfmt,'-r',paru,'-i','-g']
            runcmd(cmdlis)



