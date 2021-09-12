#-*- coding: utf-8 -*-

#basic information
__appnm__='SeqConvert'
__appver__='1.0'
__appdesc__='Simple format conversion between sqpd and fasta'

#load internal packages
import sys
import os
import json
import argparse
from contextlib import closing


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
    #get demo sequence dir
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    #aparser.add_argument('-i','--ipfi',required=True,help='Input data file')
    aparser.add_argument('ipfi',help='Input data file')
    aparser.add_argument('-t','--ctyp',required=True,choices=['fasta2sqpd','peff2sqpd','sqpd2fasta','set2fasta'],help='Conversion mode')
    aparser.add_argument('-o','--odir',help='Output dir')
    #aparser.add_argument('odir',help='Output dir')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta file')
    aparser.add_argument('-p','--pprt',action='store_true',help='Pretty print fasta format')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    ipfi=checkfile(argnms.ipfi)
    ipnm=getfn(ipfi)
    ctyp=argnms.ctyp
    ofmt=re.split('2',ctyp)[1]
    fiext=ofmt
    dirlb=''
    if ofmt=='sqpd':
        ipnm='SQPD'
        fiext='db'
        dirlb='next'
    elif ofmt=='fasta':
        ipnm='Single'
        dirlb='classic'
    odir=argnms.odir
    if odir:
        odir=checkdir(odir)
        #if ctyp=='set2fasta':
        #    loginfo('Not allowed to specified output directory for set2fasta!',isexit=1)
    else:
        #odir=os.path.dirname(ipfi)
        padir=os.path.dirname(ipfi)
        odir=os.path.join(padir,'..','..',dirlb,ofmt)
    labn=argnms.labn
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    paru=argnms.paru
    #check the existence of paru or treat paru as pattern -> papt?
    if ctyp in ['fasta2sqpd']:
        if not paru:
            loginfo('Parser rule key required for fasta file: [%s]!'%ipfi,'Error',isexit=1)
    elif ctyp in ['peff2sqpd']:
        paru='PEFF'
    optfn=checkfile(os.path.join(odir,'%s%s.%s'%(ipnm,labn,fiext)),1)
    pprt=argnms.pprt
    if ctyp=='fasta2sqpd':
        seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['PRO'][paru])
        loginfo('Source file Loaded successfully: %s'%ipfi)
        loginfo('Total sequences: %s'%len(idlis))
        dbdic=SQDIC['tablecont']
        dbdic.update({'tablecmt':SQDIC['tablecmt']})
        bidx=1
        #create db file
        with closing(sql3.connect(optfn)) as dbcn:
            with closing(dbcn.cursor()) as dbcs:
                for dt in dbdic.items():
                    dtkey,dtval=dt
                    tmpflds=dtval['fields']
                    tmpnts=dtval['notes']
                    tmplis=[]
                    for efi in range(len(tmpflds)):
                        tmplis.append('%s %s'%(tmpflds[efi],tmpnts[efi][1]))
                    dbcs.execute('CREATE TABLE %s (%s)'%(dtkey,', '.join(tmplis)))
            dbcn.commit()
        #self description for sqpd
        vallis=[]
        for dt in dbdic.items():
            dtkey,dtval=dt
            tmpflds=dtval['fields']
            tmpnts=dtval['notes']
            for efi in range(len(tmpflds)):
                vallis.append((dtkey,tmpflds[efi],tmpnts[efi][0],tmpnts[efi][1]))
        fldlis=dbdic['tablecmt']['fields'][1:]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('tablecmt',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,vallis,1)
        #write basic information
        fldlis=dbdic['basicinfo']['fields'][1:]
        vallis=['%s_%s'%(ipnm,labn),'','','','','',len(idlis),ctyp,'AA'] 
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('basicinfo',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,tuple(vallis))
        #write sequence
        seqvallis=[]
        for ei in idlis:
            seqvallis.append((ei,seqdic[ei][0],bidx))
        fldlis=dbdic['sequences']['fields'][1:]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('sequences',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,seqvallis,1)
        loginfo('SQPD file created successfully: %s'%optfn)
    elif ctyp=='sqpd2fasta':
        seqlis=fchseqs(ipfi)
        loginfo('Fetch sequences successfully: %s'%ipfi)
        loginfo('Total sequences: %s'%len(seqlis))
        with open(optfn,'w') as optobj:
            for ei in seqlis:
                tmpseq=ei[1]
                if pprt:
                    tmpseq=formatseq(tmpseq)
                optobj.write('>%s\n%s\n'%(ei[0],tmpseq))
        loginfo('FASTA file created successfully: %s'%optfn)
    elif ctyp=='set2fasta':
        sdic=json2dic(ipfi)
        loginfo('Load SET sucessfully: %s'%ipfi)
        if 'dbfi' in sdic['args']:
            dbfi=checkfile(sdic['args']['dbfi'])
        else:
            dbfi=checkfile(sdic['args']['tbfi'])
            dbfi=checkfile(os.path.join(os.path.dirname(dbfi),'..','..','next','SQPD','SQPD.db'))
        seqlis=fchseqs(dbfi)
        idlis=sdic['selected']
        loginfo('Total IDs: %s'%len(idlis))
        with open(optfn,'w') as optobj:
            for ei in seqlis:
                if ei[0] in idlis:
                    tmpseq=ei[1]
                    if pprt:
                        tmpseq=formatseq(tmpseq)
                    optobj.write('>%s\n%s\n'%(ei[0],tmpseq))
        loginfo('FASTA file created successfully: %s'%optfn)






