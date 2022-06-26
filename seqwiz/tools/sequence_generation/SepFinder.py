#-*- coding: utf-8 -*-

#basic information
__appnm__='SepFinder'
__appver__='1.0'
__appdesc__='Prediction of small-ORFs (sORFs) and their encoded peptides (SEPs) based on RNA transcript sequences'

#load internal packages
import sys
import os
import re


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

#PRDIC


def autocds(rseq):
    if 'U' in rseq:
        rseq=re.sub('U','T',rseq)
    return rseq

def sepfinder(rid,rseq,initlis,stoplis,cdsdic,initcls,minlen=6,maxlen=200,slabel='F',circ=0):
    #treate ambugious RNA sequence such as N
    rstlis=[]
    #farme shift: 0-2 -> F1-3
    ponu=0
    #rna type lable, L0 for liner RNA
    rtlab='L0'
    rlen0=len(rseq)
    #prepare pseudo rna seq for circRNA, rule: max additional loop=3
    if circ:
        rtlab0='C%d'
        rseq=rseq*4
    while ponu<3:
        #frame sequence
        fseq=rseq[ponu:]
        #walk position
        wnu=0
        tmppep=''
        tmporf=''
        #start position, 1-based corrected
        bnu=ponu+1
        #end position, 1-based corrected
        enu=ponu
        #label for new block of ORF
        block=1
        stdcds='S'
        while wnu+2<len(fseq):
            enu+=3
            tmpcds=fseq[wnu:wnu+3]
            if tmpcds in cdsdic.keys():
                tmpaa=cdsdic[tmpcds]
            else:
                tmpaa='X'
                stdcds='A'
            #check for ORF begin
            if block==1 and ((tmpcds in initlis) or (init=='A' and ambi)):
                block=0
                bnu+=wnu
            if tmpcds not in stoplis and block==0:
                tmppep+=tmpaa
                tmporf+=tmpcds
            elif tmpcds in stoplis and block==0:
                if tmppep!='' and len(tmppep)<=maxlen and len(tmppep)>=minlen:
                    tmporf+=tmpcds
                    #tmppep+=tmpaa
                    if (not ambi and stdcds=='S') or ambi:
                        initcds=''
                        if tmporf[:3] in CODONDIC['Default']['Initiation']['Canonical']:
                            initcds='C'
                        else:
                            if tmporf[:3] in CODONDIC['Default']['Initiation']['Near-Cognate']:
                                initcds='N'
                            else:
                                initcds='A'
                        if circ:
                            if bnu>rlen0:
                                break
                            circnu=int(enu/float(rlen0))
                            enu=enu-circnu*rlen0
                            rtlab=rtlab0%circnu
                        tmpid='%s:%s%s%s%s|%s@%s-%s'%(rid,slabel,ponu+1,initcds,stdcds,rtlab,bnu,enu)
                        rstlis.append([tmpid,tmporf,tmppep])
                block=1
                stdcds='S'
                tmppep=''
                tmporf=''
            wnu+=3
        ponu+=1
    return rstlis

labdic={'frame':{'F':'Forward','R':'Reverse'},
        'initial':{'C':'Canonical','N':'Near-Cognate','A':'Any'},
        'codon':{'S':'Standard','A':'Ambiguous'},
        'chain':{'L':'Linear','C':'Circular'}}

if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    aparser.add_argument('ipfi',help='Input fasta file (absoulte path) for transcripts')
    aparser.add_argument('-r','--paru',required=True,choices=PRDIC['UID']['RNA'].keys(),help='Parse rule for fasta/peff file')
    aparser.add_argument('-i','--init',default='N',choices=['C','N','A'],help='Level of initial codon usage: [C]anonical, [N]ear-cognate (default) and [A]ll possible initial condons')
    aparser.add_argument('-a','--ambi',action='store_true',help='Enable ambiguous DNA codons, will use X for ambiguous AA')
    aparser.add_argument('-c','--circ',action='store_true',help='Treat transcripts as circRNAs')
    aparser.add_argument('--minlen',default=6,type=int,help='Minimal length for SEP, default: %(default)s')
    aparser.add_argument('--maxlen',default=200,type=int,help='Maximal length for SEP, default: %(default)s')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    aparser.add_argument('--ckseq',action='store_true', help='Check mode to show the first parsed sequence')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    ipfi=checkfile(argnms.ipfi)
    fanm=getfn(ipfi)
    #check paru
    paru=argnms.paru
    if argnms.ckseq:
        seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['RNA'][paru],ldmethod=0,allup=1,rperror=1,ckmod=1)
        fstseq='''First parsed protein sequence:
Unique ID: "%s"
Header: "%s"
Sequence: "%s"'''%(idlis[0],seqdic[idlis[0]][1],seqdic[idlis[0]][0][:50]+' ...' if len(seqdic[idlis[0]][0])>50 else seqdic[idlis[0]][0][:50])
        loginfo(logcont=fstseq,logtit='Note',isexit=1,logloc='',msec=0)
    init=argnms.init
    initlis=[]
    if init=='C':
        initlis=CODONDIC['Default']['Initiation']['Canonical']
    elif init=='N':
        initlis=CODONDIC['Default']['Initiation']['Canonical']+CODONDIC['Default']['Initiation']['Near-Cognate']
    elif init=='A':
        #use 'All' key? 
        initlis=list(CODONDIC['Default']['Codons'].keys())
        for ec in CODONDIC['Default']['Stop']['Canonical']:
            initlis.remove(ec)
    ambi=argnms.ambi
    stoplis=CODONDIC['Default']['Stop']['Canonical']
    cdsdic=CODONDIC['Default']['Codons']
    initcls=init
    slabel='F'
    #rna type lable, L0 for liner RNA
    rtlab='L0'
    circ=argnms.circ
    if circ:
        rtlab0='C%d' 
    minlen=argnms.minlen
    maxlen=argnms.maxlen
    labn=argnms.labn
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    if minlen>maxlen or minlen<3:
        loginfo(logcont='Length range setting error!',logtit='Error',isexit=1,logloc='',msec=0)
    #load sequence
    seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['RNA'][paru],ldmethod=1,allup=1,rperror=1,ckmod=0)
    loginfo('Load sequences successfully: %s'%ipfi)
    loginfo('Total sequences: %s'%len(idlis))
    #check output file
    orffn=checkfile(chgfn(ipfi,'ORF%s'%labn),1)
    pepfn=checkfile(chgfn(ipfi,'PEP%s'%labn),1)
    tabfi='%s.tsv'%getfn(orffn)
    tabdir=os.path.dirname(orffn)
    tabfn=checkfile(os.path.join(tabdir,tabfi),1)
    #loop for SEPFinder
    with open(orffn,'w') as orfobj:
        with open(pepfn,'w') as pepobj:
            with open(tabfn,'w') as tabobj:
                tabobj.write(joinlis(['Combined sORF ID','Unique ID','Frame direction','Frame index','Initial codon','Initial codon type','Codon ambiguous','Satrt position (1-based)','End position (1-based)','Frame type','RNA length','ORF length','PEP length']))
                rstlis=[]
                for ei in idlis:
                    rid=ei
                    rseq=autocds(seqdic[rid][0])
                    rlen0=len(rseq)
                    if circ:
                        rseq=rseq*4
                    rlen=len(rseq)
                    #farme shift: 0-2 -> F1-3
                    ponu=0
                    while ponu<3:
                        #frame sequence
                        fseq=rseq[ponu:]
                        #walk position
                        wnu=0
                        tmppep=''
                        tmporf=''
                        #start position, 1-based corrected
                        bnu=ponu+1
                        #end position, 1-based corrected
                        enu=ponu
                        #label for new block of ORF
                        block=1
                        stdcds='S'
                        while wnu+2<len(fseq):
                            enu+=3
                            tmpcds=fseq[wnu:wnu+3]
                            if tmpcds in cdsdic.keys():
                                tmpaa=cdsdic[tmpcds]
                            else:
                                tmpaa='X'
                                stdcds='A'
                            #check for ORF begin
                            if block==1 and ((tmpcds in initlis) or (init=='A' and ambi)):
                                block=0
                                bnu=ponu+wnu+1
                            if tmpcds not in stoplis and block==0:
                                tmppep+=tmpaa
                                tmporf+=tmpcds
                            elif tmpcds in stoplis and block==0:
                                if tmppep!='' and len(tmppep)<=maxlen and len(tmppep)>=minlen:
                                    tmporf+=tmpcds
                                    #tmppep+=tmpaa
                                    if (not ambi and stdcds=='S') or ambi:
                                        initcds=''
                                        if tmporf[:3] in CODONDIC['Default']['Initiation']['Canonical']:
                                            initcds='C'
                                        else:
                                            if tmporf[:3] in CODONDIC['Default']['Initiation']['Near-Cognate']:
                                                initcds='N'
                                            else:
                                                initcds='A'
                                        if circ:
                                            if bnu>rlen0:
                                                break
                                            circnu=int(enu/float(rlen0))
                                            enu=enu-circnu*rlen0
                                            rtlab=rtlab0%circnu
                                        tmpid='%s:%s%s%s%s|%s@%s-%s'%(rid,slabel,ponu+1,initcds,stdcds,rtlab,bnu,enu)
                                        tmpftyp=labdic['chain'][rtlab[0]]
                                        if circ:
                                            tmpftyp='%s (with %s round(s) of junctions)'%(tmpftyp,circnu)
                                        tmptlis=[tmpid,rid,labdic['frame'][slabel],ponu+1,tmporf[:3],labdic['initial'][initcds],labdic['codon'][stdcds],bnu,enu,tmpftyp,rlen0,len(tmporf),len(tmppep)]
                                        rstlis.append([tmpid,tmporf,tmppep,tmptlis])
                                block=1
                                stdcds='S'
                                tmppep=''
                                tmporf=''
                            wnu+=3
                        ponu+=1
                for er in rstlis:
                    tabobj.write(joinlis(er[3]))
                    orfobj.write('>ORF|%s\n%s\n'%(er[0],er[1]))
                    pepobj.write('>PEP|%s\n%s\n'%(er[0],er[2]))
    loginfo('Total sORF/SEP: %s'%len(rstlis))
    loginfo('Save sORF table file successfully: %s'%tabfn)
    loginfo('Save sORF fasta file successfully: %s'%orffn)
    loginfo('Save SEP fasta file successfully: %s'%pepfn)




