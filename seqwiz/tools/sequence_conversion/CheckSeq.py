#-*- coding: utf-8 -*-

#basic information
__appnm__='CheckSeq'
__appver__='1.0'
__appdesc__='Check parsing rule (for fasta/peff files) or sequence file (including sqpd, set and peplis)'

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
from tabbase import *


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('ipfi',help='Input file')
    aparser.add_argument('-t','--dtyp',required=True,choices=['fasta','peff','sqpd','set','peplis'],help='Data format')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta/peff file')
    aparser.add_argument('-f','--fsnu',type=int,default=5,help='Show first ? number of entries (default:%(default)s)')
    aparser.add_argument('-s','--dseq',action='store_true',help='Display sequence')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    ipfi=checkfile(argnms.ipfi)
    fanm=getfn(ipfi)
    dtyp=argnms.dtyp
    paru=argnms.paru
    if dtyp in ['fasta','peff']:
        if not paru:
            loginfo('Parser rule required for fasta or peff file!','Error',isexit=1)
        if dtyp=='peff':
            paru='PEFF'
    fsnu=argnms.fsnu
    dseq=argnms.dseq
    dsptmp='''> Index [%s]:
Unique ID: "%s"
'''
    dsptxt=''
    seqlis=[]
    if dseq:
        dsptmp+='Sequence: "%s"\n'
    if dtyp in ['fasta','peff']:
        seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['PRO'][paru],ldmethod=0,allup=1,rperror=1,ckmod=1,fstn=fsnu)
        for ei in idlis:
            seqlis.append(['%s"\nHeader:"%s'%(ei,seqdic[ei][1]),seqdic[ei][0]])
    elif dtyp=='set':
        sdic=json2dic(ipfi)
        dbfi=checkfile(sdic['args']['dbfi'])
        loginfo('Database file found: %s'%dbfi)
        idlis=sdic['selected']
        for ei in idlis[:fsnu]:
            seqlis.append([ei,fchseq(dbfi,ei)])
    elif dtyp=='peplis':
        tmplis=file2lis(ipfi)
        for et in tmplis[:fsnu]:
            #seqlis.append(['-',et])
            seqlis.append([et,et])
    elif dtyp=='sqpd':
        sqltmp='select uid, sequence from sequences LIMIT %s'%fsnu
        atups=()
        tmplis=sql3_fch(ipfi,sqltmp,atups)
        for et in tmplis:
            seqlis.append([et[0],et[1]])
    if len(seqlis)==0:
        loginfo('NO entries found!','Warnning',isexit=1)
    else:
        cn=1
        for ei in seqlis:
            tmplis=[cn]+ei
            tmptup= tuple(tmplis[:3] if dseq else tmplis[:2])
            dsptxt+=dsptmp%tmptup
            cn+=1
    loginfo(logcont=dsptxt,logtit='Note',isexit=1,logloc='',msec=0)





