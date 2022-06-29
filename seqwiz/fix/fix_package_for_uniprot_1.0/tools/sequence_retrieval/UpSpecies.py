#-*- coding: utf-8 -*-


#basic information
__appnm__='UpSpecies'
__appver__='1.0'
__appdesc__='Species information management, based on UniProtKB'


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


#functions for http accession
def getcontent(qurl,bintyp=0):
    rstcont=''
    with requests.get(qurl) as qpg:
        if bintyp:
            rstcont=qpg.content
        else:
            rstcont=qpg.text
    return rstcont


spcurl='https://legacy.uniprot.org/docs/speclist.txt'
'''
Notification for speclist.txt file:
Copyrighted by the UniProt Consortium, see https://www.uniprot.org/terms
Distributed under the Creative Commons Attribution (CC BY 4.0) License
'''


spcdic={'version':'',
        'source':spcurl,
        'species':{},
        'taxonomy':{}}

#data structure for species dict
#unique code: [kingdom,taxonomy id,official name,common name, synonym]

if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('-m','--mact',required=True,choices=['update','search','view'],help='Action type for management')
    aparser.add_argument('-s','--skey',help='Search keyword')
    aparser.add_argument('-k','--kdom',choices=['A','B','E','V','O'],help='Taxonomic kingdom for searching a species: A=archaebacteria, B=prokaryota or eubacteria, E=eukarya, V=viridae, O=others')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    mact=argnms.mact
    skey=argnms.skey
    kdom=argnms.kdom
    spfi=os.path.join(__rootpath__,'..','..','data','species.json')
    if mact=='update':
        cver=''
        if os.path.isfile(spfi):
            cspdic=json2dic(spfi)
            cver=cspdic['version']
        spctxt=getcontent(spcurl)
        verlb=(re.findall('Release:\s+(.+)',spctxt)[0]).strip()
        spcdic['version']=verlb
        if verlb==cver:
            loginfo('It is already the latest version: [%s]!'%verlb,'Note',isexit=1)
        lilis=re.findall('.+',spctxt)
        stlb=0
        ckpat='(\w+)\s+(\w)\s+(\d+):\s+N=(.+)'
        addpat='\s+([C|S])=(.+)'
        tmpkey=''
        tmpval=[]
        for el in lilis:
            cklis=re.findall(ckpat,el)
            addlis=re.findall(addpat,el)
            if len(cklis)==1 and len(cklis[0])==4:
                #store taxonomy mapping
                spcdic['taxonomy'][cklis[0][2]]=cklis[0][0]
                if stlb==1 and tmpkey:
                    spcdic['species'][tmpkey]=tmpval
                stlb=1
                tmpkey=cklis[0][0]
                tmpval=list(cklis[0][1:])+['','']
            elif len(addlis)==1 and len(addlis[0])==2 and stlb==1:
                nmcls=addlis[0][0]
                if nmcls=='C':
                    tmpval[-2]=addlis[0][1]
                elif nmcls=='N':
                    tmpval[-1]=addlis[0][1]
        spcdic['species'][tmpkey]=tmpval
        dic2json(spcdic,spfi,1)
    elif mact=='search':
        if not skey:
            loginfo('Keyword required: [-s/--skey]','Error',isexit=1)
            if len(skey)<3:
                loginfo('Keyword too short: <3 characters','Error',isexit=1)
        if not kdom:
            loginfo('kingdom required: [-k/--kdom]','Error',isexit=1)
        tmplis=[]
        spfi=checkfile(spfi)
        cspdic=json2dic(spfi)
        for ek,ev in cspdic['species'].items():
            if kdom==ev[0]:
                tmpstr='\n'.join(ev[1:5])
                #schlis=re.findall('('+skey.lower()+')',tmpstr.lower())
                schlis=re.findall('('+skey+')',tmpstr)
                if len(schlis)>0:
                    tmplis.append([ek,ev[1],ev[2],ev[3],ev[4]])
        if len(tmplis)>20:
            loginfo('Too many results: %s\nOnly show first 20 results\nTry a more precise keyword!'%len(tmplis),'Warrning')
        elif len(tmplis)==0:
            loginfo('No results.\nTry a more precise keyword!','Warrning')
        cn=1
        for et in tmplis[:20]:
            schrst='''>Match %s:
            Name code: %s
            Taxonomy ID: %s
            Official name: %s
            Common name: %s
            Synonym: %s'''%tuple([cn]+et)
            print(schrst)
            cn+=1
    elif mact=='view':
        spfi=checkfile(spfi)
        webbrowser.open(spfi)



