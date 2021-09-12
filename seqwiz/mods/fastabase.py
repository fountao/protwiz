#-*- coding: utf-8 -*-

#basic information
__appnm__='FastaBase'
__appver__='1.0'

#load internal packages
import sys
import os
import re
import json

#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__basedir__=os.path.dirname(__rootpath__)
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)


#load local packages
from cmdbase import *
from dbbase import *



#load dict for parsing rules

PRFINA=checkfile(os.path.join(__basedir__,'data','parser.json'))
AASFINA=checkfile(os.path.join(__basedir__,'data','aas.json'))
#CODONFINA=checkfile(os.path.join(__rootpath__,'..','data','codon.json'))
CODONFINA=checkfile(os.path.join(__basedir__,'data','codon.json'))
SQFINA=checkfile(os.path.join(__basedir__,'data','sqpd.json'))
PRDIC=json2dic(PRFINA)
AASDIC=json2dic(AASFINA)
CODONDIC=json2dic(CODONFINA)
SQDIC=json2dic(SQFINA)

#functions
def formatseq(tmpseq,linenu=80):
    tmptxt=''
    cn=0
    seqlen=len(tmpseq)
    while cn<seqlen:
        tmptxt+=tmpseq[cn:cn+linenu]+'\n'
        cn+=linenu
    return tmptxt


def loadfasta(fina,idpat,ldmethod=1,allup=1,rperror=1,ckmod=0,fstn=5):
    '''load fasta sequences, also support peff data
#return data structure: seqdic(id:[seq,header]),idlis,rplis
#seqdic structure: {id: [sequence, header], ...}'''
    seqdic={}
    idlis=[]
    rplis=[]
    #python3 newline mode
    tipf=open(fina,'r')
    if ckmod:
        ldmethod=0
    if ldmethod==0:
        #get sequence line by line
        snu=0
        while True:
            eline=tipf.readline()
            #skip comments
            if eline[0]=="#":
                continue
            if not eline:
                break
            if eline[0]=='>':
                if ckmod:
                    if snu>fstn-1:
                        return seqdic,idlis,rplis
                snu+=1
                tmpid=re.findall(idpat,eline)[0]
                seqdic[tmpid]=['',re.findall('>(.+)',re.sub('\t',' ',eline))[0]]
                if tmpid in idlis:
                    if tmpid not in rplis:
                        rplis.append(tmpid)
                    if rperror==1:
                        raise Exception('Repeated identity')
                else:
                    idlis.append(tmpid)
            else:
                tmpseq=re.sub('\s','',eline)
                if allup==1:
                    tmpseq=tmpseq.upper()
                seqdic[tmpid][0]+=tmpseq
        tipf.close()
    else:
        #get sequence using greedy method (reading once)
        tmpseqs=tipf.read()
        tipf.close()
        #remove comments line
        tmpseqs=re.sub('^#.+\n?','',tmpseqs,flags=re.M)
        #should not use \t in the header
        tmpseqs=re.sub('\t',' ',tmpseqs)
        #Newline character of different sysytems
        tmpseqs=re.sub('[\r\n]','\t',tmpseqs)
        tmplis=re.split('\t>','\t'+tmpseqs)[1:]
        for et in tmplis:
            tmpseq=re.split('\t',et,1)
            tmpid=re.findall(idpat[1:],tmpseq[0])[0]
            tmpseq1=re.sub('\s','',tmpseq[1])
            if allup==1:
                tmpseq1=tmpseq1.upper()
            seqdic[tmpid]=[tmpseq1,re.findall('(.+)',tmpseq[0])[0]]
            if tmpid in idlis:
                if tmpid not in rplis:
                    rplis.append(tmpid)
                if rperror==1:
                    #print(tmpid)
                    raise Exception('Repeated identity')
            else:
                idlis.append(tmpid)
    return seqdic,idlis,rplis


def fchseq(dbfi,uid):
    sqltmp='select sequence from sequences where uid=?'
    atups=(uid,)
    seqlis=sql3_fch(dbfi,sqltmp,atups)
    tmpseq=''
    if len(seqlis)==1:
        tmpseq=seqlis[0][0]
    return tmpseq

def fchids(dbfi):
    sqltmp='select uid from sequences'
    atups=()
    seqlis=sql3_fch(dbfi,sqltmp,atups)
    return seqlis

def fchseqs(dbfi):
    sqltmp='select uid, sequence from sequences'
    atups=()
    seqlis=sql3_fch(dbfi,sqltmp,atups)
    return seqlis

def fchfts(dbfi,uid,fkey=''):
    sqltmp='select fval from features where uid=? and fkey=?'
    atups=(uid,fkey)
    ftlis=sql3_fch(dbfi,sqltmp,atups)
    tmpfts=[]
    if len(ftlis)>=1:
        for ef in ftlis:
            tmpfts.append(ef[0])
    return tmpfts
