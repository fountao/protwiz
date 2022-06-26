#-*- coding: utf-8 -*-

#basic information
__appnm__='SeqWindow'
__appver__='1.0'
__appdesc__=''

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


def getseqwin(aseq,spos,epos,ulen,dlen,outs='_'):
    rspos=spos-1
    repos=epos-1
    tmpseq=aseq[rspos:epos]
    useq=''
    dseq=''
    cn=1
    while cn<=ulen:
        if rspos-cn<0:
            useq=outs+useq
        else:
            useq=aseq[rspos-cn]+useq
        cn+=1
    cn=1
    while cn<=dlen:
        if repos+cn>=len(aseq):
            dseq=dseq+outs
        else:
            dseq=dseq+aseq[repos+cn]
        cn+=1
    preaa=useq[-1]
    nxtaa=dseq[0]
    return [len(tmpseq),preaa,tmpseq,nxtaa,useq,useq+tmpseq+dseq,dseq]



if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description='Search for sequence window based on position table')
    #input data file
    #aparser.add_argument('-d','--dbfi',required=True,help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    aparser.add_argument('dbfi',help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    #input format: fasta jspd sqpd tab
    #aparser.add_argument('-p','--pofi',required=True,help='position table file (absolute path)')
    aparser.add_argument('pofi',help='position table file (absolute path), with header :UID<tab>START<tab>END ')
    #output table file name
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-o','--odir',help='Output dir')
    aparser.add_argument('--ulen',type=int,default=6,help='Upstream sequence length')
    aparser.add_argument('--dlen',type=int,default=6,help='Downstream sequence length')
    aparser.add_argument('-s','--sout',default='_',help='Symbol for outlier position')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #check input file
    dbfi=checkfile(argnms.dbfi)
    labn=argnms.labn
    odir=argnms.odir
    verdir=checkdir(os.path.join(os.path.dirname(dbfi),'..','..'))
    pofi=checkfile(argnms.pofi)
    podir=checkdir(os.path.dirname(pofi))
    ponm=getfn(pofi)
    ofnm='%s_SeqWindow'%ponm
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    if odir:
        odir=checkdir(odir)
    else:
        #os.chdir(verdir)
        #check output file
        odir=checkdir(os.path.join(verdir,'classic','table'))
    #os.chdir(podir)
    #check output file
    optfn=checkfile(os.path.join(odir,'%s%s.tsv'%(ofnm,labn)),1)
    ulen=argnms.ulen
    dlen=argnms.dlen
    sout=argnms.sout
    #first row as title
    potab=file2tab(pofi)[1:]
    #loop for each position
    addtits=['Range length','Previous AA','Range sequence','Next AA','Upstream sequence (-%s)'%(ulen),'Sequence window','Downstream sequence (+%s)'%(dlen)]
    with open(optfn,'w') as optobj:
        tits=['UID','Start position (1-based)','End position (1-based)']+addtits
        optobj.write(joinlis(tits))
        for ep in potab:
            uid,spos,epos=ep[:3]
            spos=int(spos)
            epos=int(epos)
            aseq=fchseq(dbfi,uid)
            if aseq:
                tmplis=[uid,spos,epos]+getseqwin(aseq,spos,epos,ulen,dlen,sout)
            else:
                tmplis=[uid,spos,epos]+['']*len(addtits)
            optobj.write(joinlis(tmplis))
    loginfo('Sequence window table file saved: %s'%optfn)



