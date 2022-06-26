#-*- coding: utf-8 -*-

#basic information
__appnm__='SeqDecoy'
__appver__='1.0'
__appdesc__='Create decoy fasta sequences'

#load internal packages
import sys
import os
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



if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('ipfi',help='Souce sequence file (absolute path)')
    aparser.add_argument('-t','--dtyp',required=True,choices=['sqpd','fasta','peff','set'],help='Data format')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta/peff file')
    aparser.add_argument('-o','--odir',help='Output dir')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-p','--pfix',default='DECOY',help='Prefix symbol for unique ID')
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
    dbnm=getfn(ipfi)
    odir=argnms.odir
    labn=argnms.labn
    pfix=argnms.pfix
    ofnm='Single_decoy'
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
        odir=checkdir(os.path.join(verdir,'classic','fasta'))
    #check output file  
    optfn=checkfile(os.path.join(odir,'%s%s.fasta'%(ofnm,labn)),1)
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
    loginfo('Load sequences successfully: %s'%ipfi)
    loginfo('Total sequences: %s'%len(seqlis))
    #loop for each sequence
    with open(optfn,'w') as optobj:
        for es in seqlis:
            tmpid,tmpseq=es
            tmphd='>%s_%s'%(pfix,tmpid)
            optobj.write('%s\n%s\n'%(tmphd,tmpseq[::-1]))
    loginfo('Decoy fasta file saved: %s'%optfn)

