#-*- coding: utf-8 -*-

#basic information
__appnm__='TabFilter'
__appdesc__='Table filter to generate a set of ID list'
__appver__='1.0'

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
    aparser.add_argument('tbfi',help='Table file (absolute path), must be in pre-defined directory of SeqDBs ')
    megp=aparser.add_mutually_exclusive_group(required=True)
    megp.add_argument('-c','--cidx',type=int,help='Column index for filtering (1-based)')
    megp.add_argument('-s','--sfts',action='store_true',help='Show table header and first row')
    #better handle this in set file
    #aparser.add_argument('-a','--uant',default='exlude',choices=['include','exclude'],help='Selection for entries with unannotated or ambiguous features  [default: %(default)s]')
    aparser.add_argument('-o','--odir',help='Output dir')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('-u','--uidx',default=1,type=int,help='UID index (1-based)')
    #use to select -e " " to select empty values
    aparser.add_argument('-e','--exps',help='Expression string/condition for filtering')
    aparser.add_argument('-t','--ftyp',choices=['exact','pattern','numeric'],help='Condition type')
    #change to auto recognize
    aparser.add_argument('-n','--numt',choices=['(min,max)','[min,max]','(min,max]','[min,max)','<=max','>=min','<max','>min','!=val','=val'],help='Template class for numerical condition')
    aparser.add_argument('-m','--fmod',default='select',choices=['select','remove'],help='Filter mode [default: %(default)s]')
    aparser.add_argument('-r','--refi',help='Reference entries list for multiple selection')
    aparser.add_argument('-i','--imod',choices=['union','intersection','complement'],help='Integration mode for multiple selection')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    #check table file
    tbfi=checkfile(argnms.tbfi)
    #load tab data
    stab=file2tab(tbfi)
    loginfo('Source table file [%s] loaded successfully!'%tbfi)
    tits=stab[0]
    sdat=stab[1:]
    loginfo('Total feature records: %s (Column: %s)'%(len(sdat),len(tits)))
    cidx=argnms.cidx
    sfts=argnms.sfts
    if sfts:
        #show table title and first row
        cnu=0
        print('#[Index] Title: First row value ...')
        for et in tits:
            print('[%s] %s: %s ...'%(cnu+1,tits[cnu],sdat[0][cnu]))
            cnu+=1
        sys.exit()
    cidx=cidx-1
    if cidx<0 or cidx>len(tits)-1:
        loginfo('Index ID out of range: %s not in [%s,%s]'%(cidx+1,1,len(tits)),'Error',isexit=1)
    coln=tits[cidx]
    tbnm='%s_filter'%getfn(tbfi)
    odir=argnms.odir
    if not odir:
        verdir=checkdir(os.path.join(os.path.dirname(tbfi),'..','..'))
        #os.chdir(verdir)
        #check output file
        odir=checkdir(os.path.join(verdir,'next','sets'))
    else:
        odir=checkdir(odir)
    labn=argnms.labn
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    optdir=odir
    optfn=checkfile(os.path.join(optdir,'%s%s.json'%(tbnm,labn)),1)
    #uant=argnms.uant
    exps=argnms.exps
    if not exps:
        loginfo('Filter expression required: [-e/--exps]','Error',isexit=1)
    else:
        exps=exps.strip()
    uidx=argnms.uidx-1
    #check uidx or select uidx
    if uidx<0 or uidx>len(tits)-1:
        loginfo('Index ID for UID out of range: %s not in [%s,%s]'%(uidx+1,1,len(tits)),'Error',isexit=1)
    ftyp=argnms.ftyp
    if not ftyp:
        loginfo('Condition type required: [-t/--ftyp]','Error',isexit=1)
    numt=argnms.numt
    if ftyp=='numeric' and not numt:
        loginfo('Numerical template required: [-n/--numt]','Error',isexit=1)
    fmod=argnms.fmod
    refi=argnms.refi
    reflis=[]
    if refi:
        refdic=json2dic(checkfile(refi))
        if 'selected' not in refdic:
            loginfo('Reference entries list error: uid not found!','Error',isexit=1)
        reflis=refdic['selected']
        loginfo('Reference set file [%s] loaded successfully!'%refi)
    imod=argnms.imod
    sltlis=[]
    ualis=[]
    ablis=[]
    for er in sdat:
        uid=er[uidx]
        fidx=getpos(coln,tits)
        eft=er[fidx].strip()
        if eft=='':
            ualis.append(uid)
        sltid=0
        if ftyp=='exact':
            if eft==exps:
                sltid=1
        elif exps!='' and ftyp=='pattern':
            #avoid pattern with empty or non-significant results, eg. '()'
            if len(re.findall(exps,eft))>0:
                sltid=1
        elif exps!='' and eft!='' and ftyp=='numeric':
            try:
                eft=float(eft)
            except Exception as em:
                loginfo('Feature content is not suitable for numerical comarison: %s!'%eft,'Warnning')
                ablis.append(uid)
                continue
            vnum,vexp,vpat=NPTDIC[numt]
            tmplis=re.findall(vpat,exps)
            if len(tmplis)!=1:
                loginfo('Numeric condition or template error %s : %s!'%(numt,exps),'Error',isexit=1)
            tmpvals=tmplis[0]
            if not isinstance(tmpvals,tuple):
                tmpvals=(tmpvals,)
            if len(tmpvals)!=vnum:
                loginfo('Numeric condition expression error: too many values?!\n %s : %s!'%(numt,exps),'Error',isexit=1)
            if len(tmpvals)==2:
                if float(tmpvals[1])<float(tmpvals[0]):
                    loginfo('Numeric condition expression error: min>max?!\n %s : %s!'%(numt,exps),'Error',isexit=1)
                numexp=vexp%(eft,tmpvals[0],eft,tmpvals[1])
            else:
                numexp=vexp%(eft,tmpvals[0])
            if eval(numexp):
                sltid=1
        if fmod=='remove':
            if sltid==1:
                sltid=0
            elif sltid==0:
                sltid=1
        if sltid==1:
            sltlis.append(uid)
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






