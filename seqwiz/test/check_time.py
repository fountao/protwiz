#-*- coding: utf-8 -*-

import time
import os
import sys

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

def checkfa(ipfi,paru):
    stm=time.time()
    seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['PRO'][paru])
    etm=time.time()
    return (etm-stm)/60
    

def checkdb(dbfi):
    stm=time.time()
    seqlis=fchseqs(dbfi)
    etm=time.time()
    return (etm-stm)/60

def checkset(stfi):
    stm=time.time()
    sdic=json2dic(stfi)
    if 'dbfi' in sdic['args']:
        dbfi=checkfile(sdic['args']['dbfi'])
    else:
        dbfi=checkfile(sdic['args']['tbfi'])
        dbfi=checkfile(os.path.join(os.path.dirname(dbfi),'..','..','next','SQPD','SQPD.db'))
    seqlis=fchseqs(dbfi)
    etm=time.time()
    return (etm-stm)/60

os.chdir(os.path.join(__rootpath__,'..','seqdbs','uniprot'))

dblis=[r'CAEEL_6239/2021_03/next/sqpd/SQPD.db',
       r'DROME_7227/2021_03/next/sqpd/SQPD.db',
       r'MOUSE_10090/2021_03/next/sqpd/SQPD.db']

peflis=[r'CAEEL_6239/2021_03/classic/peff/PEFF.peff',
       r'DROME_7227/2021_03/classic/peff/PEFF.peff',
       r'MOUSE_10090/2021_03/classic/peff/PEFF.peff']

falis=[r'MOUSE_10090/2021_03/classic/fasta/Single_proteome.fasta',
       r'MOUSE_10090/2021_03/classic/fasta/Single_small.fasta',
       r'MOUSE_10090/2021_03/classic/fasta/Single_motif.fasta']

setlis=[r'MOUSE_10090/2021_03/next/sets/SQPD_filter_proteome.json',
       r'MOUSE_10090/2021_03/next/sets/properties_filter_small.json',
       r'MOUSE_10090/2021_03/next/sets/SQPD_filter_motif.json']

for ed in dblis:
    print(ed,checkdb(ed))

for ep in peflis:
    print(ep,checkfa(ep,'PEFF'))

for ef in falis:
    print(ef,checkfa(ef,'Single'))

for es in setlis:
    print(es,checkset(es))
