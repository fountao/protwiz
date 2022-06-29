#-*- coding: utf-8 -*-

#basic information
__appnm__='UpRetrieval'
__appver__='1.0'
__appdesc__='Retrieval of species specific protein sequences and annotations from the UniProtKB database'

#Programmatic access to UniProtKB:
'''
Reference:
How can I access resources on this website programmatically?
https://www.uniprot.org/help/api
'''

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

def ukdownload(durl,dfina,gzcps=1,cksize=5*1024):
    with requests.get(durl) as dpg:
        #check connection status
        if dpg.status_code!=200:
            #retry or raise error
            loginfo('Connection or url error: [%s]!'%qpg.status_code,'Error',isexit=1)
        rcdnum=int(dpg.headers['X-Total-Results'])
        #check records number
        if rcdnum==0:
            loginfo('Find no records: [%s]!'%qpg.status_code,'Error',isexit=1)
            #raise error
        #antpg.headers['Content-Disposition']
        #antftyp=antpg.headers["Content-Type"])
        #!no size information: antpg.headers["Content-Length"]
        ukver=dpg.headers['X-UniProt-Release']
        if gzcps==1:
            tmpfina=dfina+'.gz'
        else:
            tmpfina=dfina
        #rewrite all files to avoid inconsistence
        with open(tmpfina,'wb') as dobj:
            for eck in dpg.iter_content(chunk_size=cksize):
                dobj.write(eck)
    if gzcps==1:
        ungzip(tmpfina,dfina)
        os.remove(tmpfina)
    return (ukver,rcdnum)

#predefined parameters
baseurl='https://legacy.uniprot.org/'
qryurl=baseurl+'uniprot/'
refurl=baseurl+'proteomes/'
#Reference: UniProtKB column names for programmatic access
#https://www.uniprot.org/help/uniprotkb_column_names
#please use Column names as displayed in URL
dftfts=['id','entry name','protein names','genes','organism','proteome','created','last-modified','sequence-modified','reviewed','existence','fragment','comment(ALTERNATIVE PRODUCTS)','feature(NATURAL VARIANT)','feature(CHAIN)','feature(CROSS LINK)','feature(DISULFIDE BOND)','feature(GLYCOSYLATION)','feature(INITIATOR METHIONINE)','feature(LIPIDATION)','feature(MODIFIED RESIDUE)','feature(PEPTIDE)','feature(PROPEPTIDE)','feature(SIGNAL)','feature(TRANSIT)','feature(SEQUENCE CONFLICT)']

#for request timeout and retry times
dftwtime=10
dftretry=5


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    megp=aparser.add_mutually_exclusive_group(required=True)
    megp.add_argument('-t','--taxid',help='Taxonomy ID for a specific species')
    megp.add_argument('-b','--bcols',action='store_true',help='Browse UniProtKB column names for --addfts')
    aparser.add_argument('-l','--dblab',default='customize',help='Label for this database [default: %(default)s]')
    aparser.add_argument('--rwrite',action='store_true',help='Rewrite mode')
    #aparser.add_argument('-n','--dbname',default='default',help='A short name for sequence database')
    aparser.add_argument('-r','--refset',action='store_true',help='To search for a reference proteome')
    aparser.add_argument('-c','--curate',action='store_true',help='Select only curated proteins (reviewed by Swiss-Prot)')
    aparser.add_argument('-f','--rmfrag',action='store_true',help='Remove fragment sequences')
    aparser.add_argument('-i','--rmisof',action='store_true',help='Remove isoform sequences')
    aparser.add_argument('--addfts',nargs='*',help='Additional column features for sequence annotation, the build-in features are: %s.'%('; '.join(dftfts)))
    aparser.add_argument('-s','--sqpd',action='store_true',help='Create SQPD sequence database using UpConvert')
    aparser.add_argument('-a','--annot',action='store_true',help='Performing sequence annotation (calculating protein properties) using SeqAnnotate')
    #aparser.add_argument('-l','--lktime',type=int,default=5,help='Lock time (in seconds) to avoid too frequent connections, default: %(default)s')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    #convert namespace to dict
    #argsdic=vars(argnms)
    bcols=argnms.bcols
    if bcols:
        webbrowser.open('https://www.uniprot.org/help/uniprotkb_column_names')
        sys.exit()
    #get dblab
    dblab=argnms.dblab
    rwrite=argnms.rwrite
    #get taxonomy id
    taxid=argnms.taxid
    #check taxid or selected from table
    spfi=os.path.join(__rootpath__,'..','..','data','species.json')
    spdic=json2dic(spfi)
    if taxid not in spdic['taxonomy']:
        loginfo('Taxonomy ID not found in species data: %s!'%taxid,'Error',isexit=1)
    codenm=spdic['taxonomy'][taxid]
    #get database name
    #dbname=argnms.dbname
    #dbname='%s_%s'%(codenm,taxid)
    dbname='%s_%s_%s'%(codenm,taxid,dblab)
    loginfo('Database name: %s'%dbname)
    #get boolean for a reference proteome
    refset=argnms.refset
    #get boolean for curated proteins
    curate=argnms.curate
    #get boolean for remove fragments
    rmfrag=argnms.rmfrag
    #get boolean for remove isoforms
    rmisof=argnms.rmisof
    #update column parameters for table features
    #check feature names, use "" to package names with space
    clmlis=dftfts
    if argnms.addfts:
        for ea in addfts:
            if ea not in clmlis:
                clmlis.append(ea)
    clmstr='columns='+','.join(clmlis)
    sqpd=argnms.sqpd
    annot=argnms.annot
    #for query parameter
    fldlis=[]
    #search for reference proteome or check organism id
    if refset:
        refurl+='?query=taxonomy:%s%%20AND%%20reference:yes&columns=id&format=tab'%taxid
        refhds=getheader(refurl)
        rcdnum=int(refhds['X-Total-Results'])
        if rcdnum==0:
            loginfo('Find no reference proteome!','Error',isexit=1)
        elif rcdnum>1:
            loginfo('Find reference proteome error, more than one records?','Error',isexit=1)
        else:
            #note: content for binary string
            #refid=re.findall('.+',str(refpg.content,'utf-8'))[1]
            refid=re.findall('.+',getcontent(refurl))[1]
            ukver=refhds['X-UniProt-Release']
        fldlis.append('proteome:%s'%refid)
    else:
        basehds=getheader(baseurl)
        ukver=basehds['X-UniProt-Release']
        fldlis.append('organism:%s'%taxid)
    #curated sequences
    if curate:
        fldlis.append('reviewed:yes')
    #remove fragments
    if rmfrag:
        fldlis.append('fragment:no')
    #treat space as "%20"
    qrystr='query='+'%20AND%20'.join(fldlis)
    #for overall parameters
    seqpars=[]
    antpars=[]
    #remove isoforms
    if rmisof:
        seqpars.append('include=no')
    else:
        seqpars.append('include=yes')
    #sequence format
    seqpars.append('format=fasta')
    #annotation format
    antpars.append('format=tab')
    #compression to speed-up download
    seqpars.append('compress=yes')
    antpars.append('compress=yes')
    #generate combined url for RESTFUL API
    #use requote_url to encode url string
    anturl=requote_uri(qryurl+'?'+'&'.join([qrystr,clmstr]+antpars))
    sequrl=requote_uri(qryurl+'?'+'&'.join([qrystr]+seqpars))
    #test mode: limit=10&format=tab
    #check seqdbs/species/ dir
    dbdir=os.path.join(__rootpath__,'..','..','seqdbs','uniprot',dbname)
    #create db dir
    if not os.path.exists(dbdir):
        os.makedirs(dbdir)
    #check version dir
    if not rwrite:
        verdir=checkdir(os.path.join(dbdir,ukver),1)
    else:
        verdir=os.path.join(dbdir,ukver)
        shutil.rmtree(verdir)
    #copy tmp files
    tmpdir=checkdir(os.path.join(__rootpath__,'..','..','data','dbdir'))
    shutil.copytree(tmpdir,verdir)
    loginfo('Database directory created.')
    #change to version dir
    #os.chdir(verdir)
    #save annotation table
    antfina=os.path.join(verdir,'classic','table','features.tsv')
    ckaver,ckanum=ukdownload(anturl,antfina)
    loginfo('Feature table saved: %s'%antfina)
    #save fasta file
    paru='UniProt'
    #seqfina=os.path.join('classic','fasta','sequences.fasta')
    seqfina=os.path.join(verdir,'classic','fasta','%s.fasta'%paru)
    cksver,cksnum=ukdownload(sequrl,seqfina)
    loginfo('Protein sequences saved: %s'%seqfina)
    #database information
    dbinfo={'species':taxid,
            'database name':dbname,
            'uniprot release':ukver,
            'reference proteome':'yes' if refset else 'no',
            'reviewed sequence only':'yes' if curate else 'no',
            'remove fragment sequences':'yes' if rmfrag else 'no',
            'remove isoform sequences':'yes' if rmisof else 'no',
            'column features':clmlis,
            'canonical record number':ckanum,
            'created date':datetime.date.today().strftime("%Y-%m-%d"),
            'table url':anturl,
            'fasta url':sequrl
            }
    vifina=os.path.join(verdir,'version.json')
    dic2json(dbinfo,vifina)
    #write parsing rule
    #prules={'ID':PRDIC['UID']['PRO']['UniProt']}
    #prfina=os.path.join('classic','fasta','parser.json')
    #dic2json(prules,prfina)
    #write current label
    cvdic={'current':ukver}
    cvfi=os.path.join(dbdir,'current.json')
    dic2json(cvdic,cvfi)
    os.chdir(__rootpath__)
    if sqpd:
        cmdlis=['python','../sequence_conversion/UpConvert.py',seqfina,'-o','sqpd']
        runcmd(cmdlis)
    if annot:
        cmdlis=['python','../sequence_analysis/SeqAnnotate.py',seqfina,'-t','fasta','-r','UniProt','-i','-g']
        runcmd(cmdlis)
    loginfo('All files are ready to use!')


