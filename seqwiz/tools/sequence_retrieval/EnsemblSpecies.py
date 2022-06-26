#-*- coding: utf-8 -*-


#basic information
__appnm__='EnsemblSpecies'
__appver__='1.0'
__appdesc__='Species information management, based on Ensembl'


#load internal packages
import argparse
import re
import sys
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
    

#predefined parameters
baseurl='http://ftp.ensembl.org/pub/'
verpg=baseurl+'current_README'

taxurl_tmp='http://ftp.ensembl.org/pub/release-%s/species_EnsemblVertebrates.txt'



if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('-m','--mact',required=True,choices=['update','search','view'],help='Action type for management')
    aparser.add_argument('-s','--skey',help='Search keyword')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    mact=argnms.mact
    skey=argnms.skey
    #check ensembl dir
    ensdir=os.path.join(__rootpath__,'..','..','seqdbs','ensembl')
    if not os.path.exists(ensdir):
        os.makedirs(ensdir)
    #check species file
    spfi=os.path.join(ensdir,'species.ens.json')
    if not os.path.exists(spfi):
        currm=getcontent(verpg)
        curver=re.findall('Ensembl Release (\d+) Databases',currm)[0]
        updensdic(spfi,curver,taxurl_tmp)
    if mact=='update':
        #get current version
        cver=''
        cspdic=json2dic(spfi)
        cver=cspdic['version']
        #get latest version
        currm=getcontent(verpg)
        curver=re.findall('Ensembl Release (\d+) Databases',currm)[0]
        cverlb='release_%s'%curver
        if cverlb==cver:
            loginfo('It is already the latest version: [%s]!'%cverlb,'Note',isexit=1)
        else:
            #update species file
            updensdic(spfi,curver,taxurl_tmp)
    elif mact=='search':
        if not skey:
            loginfo('Keyword required: [-s/--skey]','Error',isexit=1)
            if len(skey)<3:
                loginfo('Keyword too short: <3 characters','Error',isexit=1)
        tmplis=[]
        spfi=checkfile(spfi)
        cspdic=json2dic(spfi)
        for ek,ev in cspdic['taxonomy'].items():
            tmpstr='\n'.join(ev)
            #schlis=re.findall('('+skey.lower()+')',tmpstr.lower())
            schlis=re.findall('('+skey+')',tmpstr)
            if len(schlis)>0:
                tmplis.append([ek,ev[0],ev[1]])
        if len(tmplis)>20:
            loginfo('Too many results: %s\nOnly show first 20 results\nTry a more precise keyword!'%len(tmplis),'Warrning')
        elif len(tmplis)==0:
            loginfo('No results.\nTry a more precise keyword!','Warrning')
        cn=1
        for et in tmplis[:20]:
            schrst='''>Match %s:
            Taxonomy ID: %s
            Name code: %s
            Directory name: %s'''%tuple([cn]+et)
            print(schrst)
            cn+=1
    elif mact=='view':
        spfi=checkfile(spfi)
        webbrowser.open(spfi)



