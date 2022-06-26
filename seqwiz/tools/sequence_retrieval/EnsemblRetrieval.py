#-*- coding: utf-8 -*-

#basic information
__appnm__='EnsemblRetrieval'
__appver__='1.0'
__appdesc__='Retrieval of species specific protein sequences and annotations from the Ensembl database'


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


#functions for http accession
def getheader(qurl,sltkeys=[]):
    rstdic={}
    with requests.get(qurl) as qpg:
        #check status
        if qpg.status_code!=200:
            #retry or raise error
            loginfo('Connection or url error: [%s]!'%qpg.status_code,'Error',isexit=1)
        else:
            rspdic=qpg.headers
            if not sltkeys:
                rstdic=rspdic
            else:
                for ek in hdkeys:
                    if ek not in rspdic.keys():
                        rstdic[ek]=None
                    else:
                        rstdic[ek]=rspdic[ek]
    return rstdic

def getcontent(qurl,bintyp=0):
    rstcont=''
    with requests.get(qurl) as qpg:
        if bintyp:
            rstcont=qpg.content
        else:
            rstcont=qpg.text
    return rstcont

#update species dict for species_EnsemblVertebrates
def updensdic(spfi,sltver,urltmp):
    spcdic={'version':'',
        'source':'',
        'species':{},
        'taxonomy':{}}
    spcdic['version']='release_%s'%sltver
    spcdic['source']=urltmp%sltver
    taxcont=getcontent(spcdic['source'])
    spcdic['species']=tabcont2dic(taxcont,1,[0,3])
    spcdic['taxonomy']=tabcont2dic(taxcont,3,[0,1])
    dic2json(spcdic,spfi,1)
    loginfo('Ensembl species file saved: \n %s'%spfi,'Note')
    return

#down load ensembl sequence
def ensdownload(durl,dfina,cksize=5*1024):
    with requests.get(durl,stream=True) as dpg:
        #check connection status
        #dpg.raise_for_status()
        #if dpg.status_code!=200:
        #    #retry or raise error
        #    loginfo('Connection or url error: [%s]!'%qpg.status_code,'Error',isexit=1)
        #rewrite all files to avoid inconsistence
        tmpfina=dfina+'.gz'
        with open(tmpfina,'wb') as dobj:
            for eck in dpg.iter_content(chunk_size=cksize):
                dobj.write(eck)
    ungzip(tmpfina,dfina)
    os.remove(tmpfina)
    return 

#for request timeout and retry times
dftwtime=10
dftretry=5

#predefined parameters
baseurl='http://ftp.ensembl.org/pub/'
verpg=baseurl+'current_README'

taxurl_tmp=baseurl+'release-%s/species_EnsemblVertebrates.txt'

pepurl_tmp=baseurl+'release-%s/fasta/%s/pep/'

faurl_tmp=baseurl+'release-%s/fasta/%s/pep/%s'



if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('-t','--taxid',help='Taxonomy ID for a specific species')
    aparser.add_argument('-l','--dblab',help='Label for this database')
    aparser.add_argument('--rwrite',action='store_true',help='Rewrite mode')
    aparser.add_argument('--source',default='all',choices=['all','abinitio'],help='To download pep.all or pep.abinitio [default: %(default)s]')
    aparser.add_argument('-s','--sqpd',action='store_true',help='Create SQPD sequence database using SeqConvert')
    aparser.add_argument('-a','--annot',action='store_true',help='Performing sequence annotation (calculating protein properties) using SeqAnnotate')
    #aparser.add_argument('-l','--lktime',type=int,default=5,help='Lock time (in seconds) to avoid too frequent connections, default: %(default)s')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #convert namespace to dict
    #argsdic=vars(argnms)
    taxid=argnms.taxid
    source='pep.'+argnms.source
    sqpd=argnms.sqpd
    annot=argnms.annot
    #check Ensembl dir
    ensdir=os.path.join(__rootpath__,'..','..','seqdbs','ensembl')
    if not os.path.exists(ensdir):
        os.makedirs(ensdir)
    #check species file
    spfi=os.path.join(ensdir,'species.ens.json')
    if not os.path.exists(spfi):
        currm=getcontent(verpg)
        curver=re.findall('Ensembl Release (\d+) Databases',currm)[0]
        updensdic(spfi,curver,taxurl_tmp)
    #get current release version
    currm=getcontent(verpg)
    curver=re.findall('Ensembl Release (\d+) Databases',currm)[0]
    verlab='release_%s'%curver
    #check taxid
    spdic=json2dic(spfi)
    if taxid not in spdic['taxonomy']:
        loginfo('Taxonomy ID not found in species data: %s!'%taxid,'Error',isexit=1)
    else:
        seqdirnm=spdic['taxonomy'][taxid][1]
    #get database name
    #dbname=argnms.dbname
    dblab=argnms.dblab
    if not dblab:
        dblab=source
    rwrite=argnms.rwrite
    dbname='%s_%s_%s'%(seqdirnm,taxid,dblab)
    sqpd=argnms.sqpd
    annot=argnms.annot
    #check seqdbs/species/ dir
    dbdir=os.path.join(__rootpath__,'..','..','seqdbs','ensembl',dbname)
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
    #check sequence file
    peppg=getcontent(pepurl_tmp%(curver,seqdirnm))
    peplis=re.findall('href="(.+.fa.gz?)"',peppg)
    tarfi=''
    for ep in peplis:
        if source in ep:
            tarfi=ep
            break
    if tarfi=='':
        loginfo('%s sequence not available the species: %s!'%(source,spdic['taxonomy'][taxid][0]),'Error',isexit=1)
    dlurl=faurl_tmp%(curver,seqdirnm,tarfi)
    #save fasta file
    paru='Space'
    #seqfina=os.path.join('classic','fasta','sequences.fasta')
    seqfina=os.path.join(verdir,'classic','fasta','%s.fasta'%paru)
    ensdownload(dlurl,seqfina)
    loginfo('Protein sequences saved: %s'%seqfina)
    #database information
    dbinfo={'species':taxid,
            'database name':dbname,
            'ensembl release':curver,
            'created date':datetime.date.today().strftime("%Y-%m-%d"),
            'fasta url':dlurl
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


