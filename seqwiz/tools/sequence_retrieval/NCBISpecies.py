#-*- coding: utf-8 -*-


#basic information
__appnm__='NCBISpecies'
__appver__='1.0'
__appdesc__='Species information management, based on NCBI Entrez API'


#load internal packages
import argparse
import re
import sys
import os
import webbrowser

#py3 specific modules
import requests
from requests.utils import requote_uri

#3rd-party modules
#import ncbi.datasets.openapi.api.taxonomy_api as taxapi
from Bio import Entrez


#get and add script path, replace module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__scpnm__=os.path.basename(__file__)
#os.chdir(__rootpath__)
sys.path.append(__rootpath__)
sys.path.append(os.path.join(__rootpath__,'..','..','mods'))


#load local packages
from cmdbase import *
from tabbase import *


#functions for http accession
def getcontent(qurl,bintyp=0):
    rstcont=''
    with requests.get(qurl) as qpg:
        if bintyp:
            rstcont=qpg.content
        else:
            rstcont=qpg.text
    return rstcont

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


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('email',help='use your NCBI email account, to avoid blcoking of NCBI server')
    aparser.add_argument('-s','--skey',required=True,help='Search keyword')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    email=argnms.email
    #use NCBI email account
    Entrez.email=email    
    skey=argnms.skey
    if len(skey)<3:
        loginfo('Keyword too short: <3 characters','Error',isexit=1)
    #using taxapi
    """
    tmpapi=taxapi.TaxonomyApi()
    arqst=tmpapi.tax_name_query(skey, async_req=True)
    #print(type(arqst.get()))
    rstlis=arqst.get().get('sci_name_and_ids')
    tmplis=[]
    for er in rstlis:
        tmplis.append([er.get('tax_id'),er.get('common_name'),er.get('sci_name')])
    if len(tmplis)>20:
        loginfo('Too many results: %s\nOnly show first 20 results\nTry a more precise keyword!'%len(tmplis),'Warrning')
    elif len(tmplis)==0:
        loginfo('No results.\nTry a more precise keyword!','Warrning')
    cn=1
    for et in tmplis[:20]:
        schrst='''>Match %s:
        Taxonomy ID: %s
        Common name: %s
        Scientific name: %s'''%tuple([cn]+et)
        print(schrst)
        cn+=1
    """
    #using Entrez
    tnu=schcount(skey,'taxonomy')
    if tnu==0:
        loginfo('TAXID:[%s] not found!'%skey,'Error',isexit=1)
    loginfo('Found %s TAXID!'%tnu,'Note')
    if tnu>20:
        loginfo('Too many results: %s\nOnly show first 20 results\nTry a more precise keyword!'%len(tmplis),'Warrning')
    taxids=getids(skey,20,'taxonomy')
    cn=1
    for ei in range(len(taxids)):
        et=taxids[ei]
        scinm,comnm=taxparse(fchone(et,'taxonomy','json','text'),0)
        schrst='''>Match %s:
        Taxonomy ID: %s
        Common name: %s
        Scientific name: %s'''%tuple([cn]+[et,comnm,scinm])
        print(schrst)
        cn+=1
    
    
    




