#-*- coding: utf-8 -*-

#basic information
__appnm__='MotifCount'
__appver__='1.0'
__appdesc__='Motif count for protein sequences'


#load internal packages
import argparse
import sys
import os
import json
import re


#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)
sys.path.append(os.path.join(__rootpath__,'..','..','mods'))

#load local packages
from cmdbase import *
from dbbase import *
from fastabase import *
from tabbase import *



if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    #input data file
    aparser.add_argument('ipfi',help='Souce sequence file (absolute path)')
    aparser.add_argument('-t','--dtyp',required=True,choices=['sqpd','fasta','peff','peplis','set'],help='Data format')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta/peff file')
    megp=aparser.add_mutually_exclusive_group(required=True)
    megp.add_argument('-m','--mtfi',help='A file with a list of motif (absolute path)')
    megp.add_argument('-p','--mtpt',nargs='*',help='A pattern string for a single motif')
    aparser.add_argument('-o','--odir',help='Output dir')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #check input file
    ipfi=checkfile(argnms.ipfi)
    dtyp=argnms.dtyp
    paru=argnms.paru
    if dtyp in ['fasta','peff']:
        if not paru:
            loginfo('Parser rule required for fasta or peff file!','Error',isexit=1)
        if dtyp=='peff':
            paru='PEFF'
    mtfi=argnms.mtfi
    mtpt=argnms.mtpt
    if mtfi:
        mtfi=checkfile(argnms.mtfi)
        mtlis=file2lis(mtfi)
    if mtpt:
        mtlis=[mtpt]
    #mtdir=checkdir(os.path.dirname(mtfi))
    #os.chdir(mtdir)
    dbnm=getfn(ipfi)
    odir=argnms.odir
    labn=argnms.labn
    ofnm='MotifCount'
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    if odir:
        odir=checkdir(odir)
    else:
        verdir=checkdir(os.path.join(os.path.dirname(ipfi),'..','..'))
        #os.chdir(verdir)
        #check output file
        odir=checkdir(os.path.join(verdir,'classic','table'))
    #check output file  
    optfn=checkfile(os.path.join(odir,'%s%s.tsv'%(ofnm,labn)),1)
    #load sequence data
    if dtyp=='sqpd':
        sqltmp='select uid, sequence from sequences'
        atups=()
        seqlis=sql3_fch(ipfi,sqltmp,atups)
    elif dtyp in ['fasta','peff']:
        seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['PRO'][paru])
        seqlis=[]
        for ei in idlis:
            seqlis.append((ei,seqdic[ei][0]))
    elif dtyp=='set':
        sdic=json2dic(ipfi)
        dbfi=checkfile(sdic['args']['dbfi'])
        idlis=sdic['selected']
        seqlis=[]
        for et in fchseqs(dbfi):
            if et[0] in idlis:
                seqlis.append((et[0],et[1]))
    elif dtyp=='peplis':
        seqlis=[]
        peplis=file2lis(ipfi)
        for ep in peplis:
            seqlis.append((ep,ep))
    loginfo('Load sequences successfully: %s'%ipfi)
    loginfo('Total sequences: %s'%len(seqlis))
    #loop for each sequence
    with open(optfn,'w') as optobj:
        optobj.write(joinlis(['UID']+mtlis))
        for es in seqlis:
            tmpid,tmpseq=es
            tmplis=[tmpid]
            for em in mtlis:
                tmplis.append(len(re.findall(em,tmpseq)))
            optobj.write(joinlis(tmplis))
    loginfo('Motif count result file saved: %s'%optfn)



