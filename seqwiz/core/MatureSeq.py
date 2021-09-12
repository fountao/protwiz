#-*- coding: utf-8 -*-

#basic information
__appnm__='MatureSeq'
__appver__='1.0'
__appdesc__='Generate mature fasta sequences based on UniProt/SQPD database'

#load internal packages
import sys
import os
import re


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


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    #aparser.add_argument('-d','--dbfi',required=True,help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    aparser.add_argument('dbfi',help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-f','--fseq',action='store_true',help='Include full-length sequences')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #check input file
    dbfi=checkfile(argnms.dbfi)
    verdir=checkdir(os.path.join(os.path.dirname(dbfi),'..','..'))
    labn=argnms.labn
    opnm='Single_mature'
    if labn:
        opnm='%s_%s'%(opnm,labn)
    fseq=argnms.fseq
    os.chdir(verdir)
    #check output file
    optdir=checkdir(os.path.join('classic','fasta'))
    optfn=checkfile(os.path.join(optdir,'%s.fasta'%opnm),1)
    sqltmp='select uid, fval from features where fkey=?'
    atups=('UpProcessed',)
    ftlis=sql3_fch(dbfi,sqltmp,atups)
    ckunilis=[]
    with open(optfn,'w') as optobj:
        for ef in ftlis:
            tmpid,tmpft=ef
            tmpft=tmpft.strip()
            if tmpft=='':
                continue
            mtlis=re.findall('\((.+?)\)',tmpft)
            for em in mtlis:
                #start position, end positon, Controlled Vocabulary, type, description
                pclis=re.split('\|',em)
                if len(pclis)==5:
                    tmpsp,tmpep,tmpcv,tmptp,tmpds=pclis
                    tmptp=re.sub('\s','',tmptp.title())
                    tmpseq=fchseq(dbfi,tmpid)
                    flen='%s-%s'%(1,len(tmpseq))
                    if flen=='%s-%s'%(tmpsp,tmpep):
                        continue
                    tmpmid='%s:%s@%s-%s'%(tmpid,tmptp,tmpsp,tmpep)
                    tmpmseq=tmpseq[int(tmpsp)-1:int(tmpep)]
                    tmphd='>%s'%(tmpmid)
                    if tmpmid not in ckunilis:
                        optobj.write('%s\n%s\n'%(tmphd,tmpmseq))
                        ckunilis.append(tmpmid)
                    else:
                        pass
        loginfo('Mature sequences saved!')
        if fseq:
            seqlis=fchseqs(dbfi)
            for es in seqlis:
                tmpid,tmpseq=es
                tmpmid='%s:%s@%s-%s'%(tmpid,'Full',1,len(tmpseq))
                tmphd='>%s'%(tmpmid)
                if tmpmid not in ckunilis:
                    optobj.write('%s\n%s\n'%(tmphd,tmpseq))
                    ckunilis.append(tmpmid)
                else:
                    pass
            loginfo('Full length sequences saved!')
    loginfo('Mature sequence file saved successfully: %s'%optfn)
