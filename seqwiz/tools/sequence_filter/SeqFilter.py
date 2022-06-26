#-*- coding: utf-8 -*-

#basic information
__appnm__='SeqFilter'
__appver__='1.0'
__appdesc__='Sequence filter based on SQPD database'

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
sys.path.append(os.path.join(__rootpath__,'..','..','mods'))

#load local packages
from cmdbase import *
from dbbase import *
from fastabase import *
from tabbase import *

def intesets(aset,bset,imod='u'):
    rlis=[]
    if imod=='u':
        rlis=aset
        for eb in bset:
            if eb not in rlis:
                rlis.append(eb)
    elif imod=='i':
        for ea in aset:
            if ea in bset and ea not in rlis:
                rlis.append(ea)
    elif imod=='c':
        for ea in aset:
            if ea not in bset and ea not in rlis:
                rlis.append(ea)
        for eb in bset:
            if eb not in aset and eb not in rlis:
                rlis.append(eb)
    return rlis

if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #get demo sequence dir
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    #aparser.add_argument('-d','--dbfi',required=True,help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    aparser.add_argument('dbfi',help='Database file (absolute path), must be in pre-defined directory of SeqDBs ')
    megp=aparser.add_mutually_exclusive_group(required=True)
    megp.add_argument('-s','--sfts',action='store_true',help='Show feature list (in sequence and feature table)')
    megp.add_argument('-f','--ftnm',help='Feature name')
    #aparser.add_argument('-a','--uant',default='exlude',choices=['include','exclude'],help='Select for entries with unannotated features [default: %(default)s]')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-e','--exps',help='Expression string/condition for filtering')
    aparser.add_argument('-t','--ftyp',choices=['exact','pattern','numeric'],help='Condition type')
    aparser.add_argument('-n','--numt',choices=['(min,max)','[min,max]','(min,max]','[min,max)','<=max','>=min','<max','>min','!=val','=val'],help='Template class for numerical condition')
    aparser.add_argument('-m','--fmod',default='select',choices=['select','remove'],help='Filter mode [default: %(default)s]')
    aparser.add_argument('-r','--refi',help='Reference entries list for multiple selection')
    aparser.add_argument('-i','--imod',choices=['union','intersection','complement'],help='Integration mode for multiple selection')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    #get and check seq database
    dbfi=checkfile(argnms.dbfi)
    dbnm='%s_%s'%(getfn(dbfi),'filter')
    labn=argnms.labn
    if labn:
        dbnm='%s_%s'%(dbnm,labn)
    verdir=checkdir(os.path.join(os.path.dirname(dbfi),'..','..'))
    os.chdir(verdir)
    optdir=checkdir(os.path.join('next','sets'))
    optfn=checkfile(os.path.join(optdir,'%s.json'%dbnm),1)
    sfts=argnms.sfts
    ftnm=argnms.ftnm
    #uant=argnms.uant
    exps=argnms.exps
    ftyp=argnms.ftyp
    numt=argnms.numt
    if ftyp=='numeric' and not numt:
        loginfo('Numerical template required: [-n/--numt]','Error',isexit=1)
    fmod=argnms.fmod
    refi=argnms.refi
    imod=argnms.imod
    reflis=[]
    if refi:
        refdic=json2dic(checkfile(refi))
        if 'selected' not in refdic:
            loginfo('Reference entries list error: uid not found!','Error',isexit=1)
        reflis=refdic['selected']
    #check main cmd
    if sfts:
        print('[Index] Table: Feature name ...')
        print('[1] sequences: uid ...')
        print('[2] sequences: sequence ...')
        cnu=0
        ftlis=sql3_unicol(dbfi,'fkey','features')
        for eu in ftlis:
            cnu+=1
            print('[%s] %s: %s ...'%(cnu,'features',eu[0]))
        sys.exit()
    elif ftnm:
        if not exps:
            loginfo('Filter expression required: [-e/--exps]','Error',isexit=1)
        else:
            exps=exps.strip()
    #load database
    if ftnm=='uid':
        tmpscn='uid'
        tmptab='sequences'
    elif ftnm=='sequence':
        tmpscn='sequence'
        tmptab='sequences'
    else:
        tmpscn='fval'
        tmptab='features'
    sltlis=[]
    ualis=[]
    ablis=[]
    uids=fchids(dbfi)
    loginfo('Total records: %s (Table: %s)'%(len(uids),tmptab))
    if ftnm in ['uid','sequence']:
        sqltmp='select uid, %s from %s'%(tmpscn,tmptab)
        atups=()
    else:
        sqltmp='select uid, %s from %s where %s=?'%(tmpscn,tmptab,'fkey')
        atups=(ftnm,)
    ftlis=sql3_fch(dbfi,sqltmp,atups)
    loginfo('Total feature records: %s (Column: %s, Table: %s)'%(len(ftlis),ftnm,tmptab))
    ualis=removelis([eu[0] for eu in uids],[eu[0] for eu in ftlis])
    for ef in ftlis:
        sltid=0
        eu=ef[0]
        if eu in sltlis:
            continue
        eft=ef[1].strip()
        if eft=='':
            if eu not in ualis:
                ualis.append(eu)
        if ftyp=='exact':
            if eft==exps:
                sltid=1
        elif exps!='' and ftyp=='pattern':
            #avoid pattern with empty or non-significant results, eg. '()'
            if len(re.findall(exps,eft))>0:
                sltid=1
        #should check if column is suitable or allowed for numerical comparison
        elif exps!='' and eft!='' and ftyp=='numeric':
            try:
                eft=float(eft)
            except Exception as em:
                loginfo('Feature content is not suitable for numerical comarison: %s!'%eft,'Warnning')
                ablis.append(eu)
                continue
            vnum,vexp,vpat=NPTDIC[numt]
            tmplis=re.findall(vpat,exps)
            if len(tmplis)!=1:
                loginfo('Numeric condition or template error %s : %s!'%(numt,exps),'Error',isexit=1)
            tmpvals=tmplis[0]
            if not isinstance(tmpvals,tuple):
                tmpvals=(tmpvals,)
            if len(tmpvals)!=ntdic[numt][0]:
                loginfo('Numeric condition expression error: too many values?!\n %s : %s!'%(numt,exps),'Error',isexit=1)
            if len(tmpvals)==2:
                if float(tmpvals[1])<float(tmpvals[0]):
                    loginfo('Numeric condition expression error: min>max?!\n %s : %s!'%(numt,exps),'Error',isexit=1)
                numexp=ntdic[numt][1]%(eft,tmpvals[0],eft,tmpvals[1])
            else:
                numexp=ntdic[numt][1]%(eft,tmpvals[0])
            if eval(numexp):
                sltid=1
        if fmod=='remove':
            if sltid==1:
                sltid=0
            elif sltid==0:
                sltid=1
        if sltid==1:
            sltlis.append(eu)
    #check for id integration
    if reflis:
        if imod=='union':
            sltlis=intesets(sltlis,reflis,'u')
        elif imod=='intersection':
            sltlis=intesets(sltlis,reflis,'i')
        elif imod=='complement':
            sltlis=intesets(sltlis,reflis,'c')
    loginfo('Selected entries: %s'%(len(sltlis)))
    loginfo('Unannoated entries: %s'%(len(ualis)))
    loginfo('Ambiguous entries: %s'%(len(ablis)))
    #save to json file
    #print(vars(argnms))
    fidic={'args':vars(argnms),
           'selected':sltlis,
           'unannotated':ualis,
           'ambiguous':ablis}
    #print(verdir)
    #print(optfn)
    dic2json(fidic,optfn)
    loginfo('Set file [%s] saved successfully!'%optfn)






