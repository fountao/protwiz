#-*- coding: utf-8 -*-

#basic information
__appnm__='NCBIRetrieval'
__appver__='1.0'
__appdesc__='Retrieval of species specific protein sequences the NCBI database (based on Entrez)'


#load internal packages
import argparse
import re
import sys
import gzip
import json
import datetime
import shutil
import os
import webbrowser

#py3 specific modules
import requests
from requests.utils import requote_uri

#3rt-party modules
from Bio import Entrez

#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)
sys.path.append(os.path.join(__rootpath__,'..','..','mods'))

#load local packages
from cmdbase import *
from fastabase import *

#functions for gz uncompression
def ungzip(sfina,tfina):
    with gzip.open(sfina,'rb') as sobj:
        with open(tfina,'wb') as tobj:
            shutil.copyfileobj(sobj,tobj)


#check total number of ids
def schcount(sterm,dbnm='protein'):
    asearch=Entrez.esearch(db=dbnm, term=sterm,retmax=1)
    rcdsdic = Entrez.read(asearch)
    ctnu=rcdsdic['Count']
    asearch.close()
    return int(ctnu)

def getids(sterm,getnu,dbnm='protein'):
    asearch = Entrez.esearch(db=dbnm, term=sterm,retmax=getnu)
    rcdsdic = Entrez.read(asearch)
    idlis=rcdsdic['IdList']
    asearch.close()
    return idlis

def getdbver(dbnm='protein',ifkey='DbBuild'):
    #DbBuild  or LastUpdate
    ainfo=Entrez.einfo(db=dbnm)
    adic=Entrez.read(ainfo)
    ainfo.close()
    return adic['DbInfo'][ifkey]
    

def idfilter(idlis,pflis):
    rst=[]
    for ei in idlis:
        idpf=ei[:3]
        if idpf in pflis:
            rst.append(ei)
    return rst

def fchone(aid,dbnm='protein',rtyp='fasta',rmod='text'):
    afetch=Entrez.efetch(db=dbnm,id=aid,rettype=rtyp,retmode=rmod,retmax=1)
    fchrst=afetch.read()
    afetch.close()
    return fchrst
     
def taxparse(fchrst,mknm=1):
    scinm=re.findall('\d+\.\s(.+)',fchrst)[0]
    comnm=re.findall('\((.+)\)',fchrst)[0]
    if mknm:
        comnm=re.sub('\s+','_',comnm)
    return (scinm,comnm)

#for request timeout and retry times
dftwtime=10
dftretry=5

#predefined parameters
tx_tmp='txid%s[Organism:noexp]'
rf_tmp='txid%s[Organism:noexp] AND refseq[filter]'
#prefix for refseq 
rf_pflis=['NP_','XP_','AP_','YP_','WP_']
weburl_tmp='https://www.ncbi.nlm.nih.gov/protein/?term='


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('email',help='use your NCBI email account, to avoid blcoking of NCBI server')
    aparser.add_argument('-t','--taxid',help='Taxonomy ID for a specific species')
    aparser.add_argument('--refseq',action='store_true',help='Filter to include only RefSeq IDs')
    aparser.add_argument('-l','--dblab',help='Label for this database')
    aparser.add_argument('-b','--bsize',type=int,default=100,help='Block size for fetching sequences, Default: %(default)s, Range: [50,1000]')
    aparser.add_argument('--rwrite',action='store_true',help='Rewrite mode')
    aparser.add_argument('--manual',help='To manually download the sequences via local browser')
    aparser.add_argument('-s','--sqpd',action='store_true',help='Create SQPD sequence database using SeqConvert')
    aparser.add_argument('-a','--annot',action='store_true',help='Performing sequence annotation (calculating protein properties) using SeqAnnotate')
    #aparser.add_argument('-l','--lktime',type=int,default=5,help='Lock time (in seconds) to avoid too frequent connections, default: %(default)s')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #convert namespace to dict
    #argsdic=vars(argnms)
    email=argnms.email
    #use NCBI email account
    Entrez.email=email
    taxid=argnms.taxid
    refseq=argnms.refseq
    blksize=argnms.bsize
    if blksize<50 or blksize>1000:
        blksize=50
    #check taxid
    txnu=schcount('%s[uid]'%taxid,dbnm='taxonomy')
    if txnu!=1:
        loginfo('TAXID:[%s] not found!'%taxid,'Error',isexit=1)
    scinm,comnm=taxparse(fchone(taxid,'taxonomy','json','text'))
    loginfo('Check TAXID [%s]: [%s]!'%(taxid,scinm),'Note')
    #check total count    
    if refseq:
        schkey=rf_tmp%(taxid)
        tcn=schcount(schkey)
        if tcn==0:
            loginfo('No Refseq sequences found!','Error',isexit=1)
    else:
        schkey=tx_tmp%(taxid)
        tcn=schcount(schkey)
        if tcn==0:
            loginfo('No sequences found!','Error',isexit=1)
    loginfo('Found %s sequences!'%(tcn),'Note')
    manual=argnms.manual
    if manual:
        webbrowser.open_new(requote_uri(weburl_tmp+schkey))
    pids=getids(schkey,tcn)
    fchnu=len(pids)
    if fchnu!=tcn:
        loginfo('Fetched number error!\n Fetched: %s; Expected: %s'%(fchnu,tcn),'Error',isexit=1)
    #use rf_tmp instead, for not returnning protein ids
    #if refseq:
    #    pids=idfilter(pids,rf_pflis)
    #if len(pids)==0:
    #    loginfo('No RefSeq sequences found!','Error',isexit=1)
    sqpd=argnms.sqpd
    annot=argnms.annot
    #check NCBI dir
    ncbidir=os.path.join(__rootpath__,'..','..','seqdbs','ncbi')
    if not os.path.exists(ncbidir):
        os.makedirs(ncbidir)
    #get current release version
    curver=getdbver()
    verlab=curver.split('-')[0]
    #get database name
    #dbname=argnms.dbname
    dblab=argnms.dblab
    if not dblab:
        dblab='refseq' if refseq else 'full'
    rwrite=argnms.rwrite
    dbname='%s_%s_%s'%(comnm,taxid,dblab)
    sqpd=argnms.sqpd
    annot=argnms.annot
    #check seqdbs/species/ dir
    dbdir=os.path.join(__rootpath__,'..','..','seqdbs','ncbi',dbname)
    #create db dir
    if not os.path.exists(dbdir):
        os.makedirs(dbdir)
    #check version dir
    if not rwrite:
        verdir=checkdir(os.path.join(dbdir,verlab),1)
    else:
        verdir=os.path.join(dbdir,verlab)
        shutil.rmtree(verdir)
    #copy tmp files
    tmpdir=checkdir(os.path.join(__rootpath__,'..','..','data','dbdir'))
    shutil.copytree(tmpdir,verdir)
    loginfo('Database directory created.')
    #change to version dir
    #os.chdir(verdir)
    #fetch fasta sequences and save file
    loginfo('Start to save sequences ...')
    paru='Space'
    #seqfina=os.path.join('classic','fasta','sequences.fasta')
    seqfina=os.path.join(verdir,'classic','fasta','%s.fasta'%paru)
    with open(seqfina,'w') as optobj:
        for ebkl in range(0,fchnu,blksize):
            endnu=min(fchnu,ebkl+blksize)
            loginfo('Feching sequences from %s to %s ...'%(ebkl+1,endnu))
            if ebkl+blksize>fchnu:
                blksize=fchnu-ebkl
            #solution 1: using all ids with start and max numbers
            #afetch=Entrez.efetch(db="protein", id=pids,rettype='fasta', retmode="text",retstart=ebkl,retmax=blksize)
            #solution 2: using sliced ids with max numbers, this may be faster for larget list
            afetch=Entrez.efetch(db="protein", id=pids[ebkl:endnu],rettype='fasta', retmode="text",retmax=blksize)
            optobj.write(afetch.read())
            afetch.close()
    loginfo('Protein sequences saved: %s'%seqfina)
    #database information
    dbinfo={'species':taxid,
            'database name':dbname,
            'NCBI release':curver,
            'created date':datetime.date.today().strftime("%Y-%m-%d"),
            'source':'refseq' if refseq else 'full'
            }
    vifina=os.path.join(verdir,'version.json')
    dic2json(dbinfo,vifina)
    #write parsing rule
    #prules={'ID':PRDIC['UID']['PRO']['Space']}
    #prfina=os.path.join('classic','fasta','parser.json')
    #dic2json(prules,prfina)
    #write current label
    cvdic={'current':verlab}
    cvfi=os.path.join(dbdir,'current.json')
    dic2json(cvdic,cvfi)
    os.chdir(__rootpath__)
    if sqpd:
        cmdlis=['python','../sequence_conversion/SeqConvert.py',seqfina,'-t','fasta2sqpd','-r','Space']
        runcmd(cmdlis)
    if annot:
        cmdlis=['python','../sequence_analysis/SeqAnnotate.py',seqfina,'-t','fasta','-r','Space','-i','-g']
        runcmd(cmdlis)
    loginfo('All files are ready to use!')


