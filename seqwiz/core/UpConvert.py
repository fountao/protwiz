#-*- coding: utf-8 -*-

#basic information
__appnm__='UpConvert'
__appver__='1.0'
__adddesc__='Format conversion for UniProt sequence database'

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
from tabbase import *

#functions for parsing UniProt data
def getfstpn(astr):
    if len(re.findall('[\(\)]',astr))==0:
        return astr
    cn=0
    lidx=-1
    ridx=-1
    eidx=-1
    tcn=0
    for ea in astr+' ':
        if ridx>-1 and ea==' ' and tcn==0 and astr[cn-1]==')':
            break
        if ea=='(':
            eidx=cn
            lidx=cn
            tcn+=1
        elif ea==')':
            ridx=cn
            tcn-=1
        cn+=1
    rst=re.sub('\(','<',astr[:eidx])
    rst=re.sub('\)','>',rst)
    return rst

def keydic(akdic):
    rst={}
    for ea in akdic.items():
        ek,ev=ea
        for evk in ev['keys']:
            rst[evk]=ek
    return rst

def makenm(astr,lispat='[a-zA-Z0-9]+'):
    rst=''
    tmplis=re.findall(lispat,astr)
    for et in tmplis:
        rst+=et.title()
    return rst

#uniport 2 peff headers
def up2peff(colval,valpat='',valcls='',seqlen=''):
    rst=colval
    colval+=' '
    if valpat!='':
        if valpat=='pnms':
            #unable/hard to solve complex names for example:
            #tRNA (guanine-N(7)-)-methyltransferase (EC 2.1.1.33) (Methyltransferase-like protein 1) (mRNA (guanine-N(7)-)-methyltransferase) (EC 2.1.1.-) (miRNA (guanine-N(7)-)-methyltransferase) (EC 2.1.1.-) (tRNA (guanine(46)-N(7))-methyltransferase) (tRNA(m7G46)-methyltransferase)
            rst=getfstpn(colval)
        elif valpat=='gnms':
            #warnning for names such as: TMEM98 UNQ536/PRO1079
            rst=re.split(' ',colval)[0]
        elif valpat=='mod':
            tmplis=re.findall('\S+ (\d+);\s+/note="(.+?)"',colval)
            rst=''
            for et in tmplis:
                if len(et)==2:
                    rst+='(%s||%s)'%(et[0],et[1])
        elif valpat=='var':
            #unable/hard to handle complex issues:
            #missing: VARIANT 147..385;  /note="Missing @D6RGH6
            #alternative: VARIANT 1;  /note="M -> MKAVLLALLM @O43653
            tmplis=re.findall('\S+ (\d+);\s+/note="(.+?) \(',colval)
            rst=''
            for et in tmplis:
                if len(et)==2:
                    if 'missing' in et[1]:
                        rst+='(%s|%s)'%(et[0],'*')
                    elif ' -> ' in et[1]:
                        chglis=re.split(' -> ',et[1])
                        if len(chglis)==2:
                            rst+='(%s|%s)'%(et[0],chglis[1])
        elif valpat=='pro':
            #Initiator methionine is actually duplicated with chian annotation?
            #if valcls=='Initiator methionine':
            #    tmplis=re.findall('\S+ (\d+);\s+/note="(.+?)"',colval)
            #    rst=''
            #    for et in tmplis:
            #        if len(et)==2:
            #            rst+='(%s|%s||%s|%s)'%(2,seqlen,tmpcls,et[1])
            #else:
                #tmplis=re.findall('(\S+) (\d+)\.\.(\d+);\s+/note="(.+?)"',colval)
                tmplis=re.findall('(\S+) (\d+)\.\.(\d+);?\s+',colval)
                rst=''
                for et in tmplis:
                    if len(et)==3:
                        tmpcls=et[0]
                        if valcls:
                            tmpcls=valcls.lower()
                        tmpnote=''
                        tmpnts=re.findall('%s %s\.\.%s;?\s+/note="(.+?)"'%(et[0],et[1],et[2]),colval)
                        if len(tmpnts)==1:
                            tmpnote=tmpnts[0]
                        rst+='(%s|%s||%s|%s)'%(et[1],et[2],tmpcls,tmpnote)
        elif valpat=='link':
            #in rare case: CROSSLNK O94880-2:648;
            tmplis=re.findall('(\S+) (\d+\S+?);\s+',colval)
            rst=''
            for et in tmplis:
                if len(et)==2:
                    tmpcls=et[0]
                    if valcls:
                        tmpcls=valcls.lower()
                    if '..' in et[1]:
                        poslis=re.split('\.\.',et[1])
                        rst+='(%s|%s|%s)'%(poslis[0],poslis[1],tmpcls)
                    else:
                        rst+='(%s||%s)'%(et[1],tmpcls)
        elif valpat=='conflict':
            #hanld single position and paired position
            tmplis=re.findall('(\S+) (\d+\S+?);\s+/note="(.+?)"',colval)
            rst=''
            for et in tmplis:
                if len(et)==3:
                    tmpant=et[2]
                    if 'Missing' in et[2]:
                        tmpant='Missing'
                    elif ' -> ' in et[2]:
                        tmpant=re.split(' \(',et[2])[0]
                        tmpant=re.split(' -> ',tmpant)[1]
                    if '..' in et[1]:
                        poslis=re.split('\.\.',et[1])
                        rst+='(%s|%s|%s)'%(poslis[0],poslis[1],tmpant)
                    else:
                        rst+='(%s||%s)'%(et[1],tmpant)
        else:
            rst=re.split('\(',colval)[0]
    return rst


if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #get demo sequence dir
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description='Format conversion for the next generation of sequence database')
    aparser.add_argument('ipfi',help='Fasta file (absolute path), must be in pre-defined directory of SeqDBs ')
    aparser.add_argument('-o','--ofmt',default='sqpd',choices=['peff','sqpd','all'],help='Output format [default: %(default)s]')
    #aparser.add_argument('-p','--pprt',action='store_true',help='Pretty print JSON format')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namspece
    argnms=aparser.parse_args()
    #get and check fasta file
    ipfi=checkfile(argnms.ipfi)
    verdir=checkdir(os.path.join(os.path.dirname(ipfi),'..','..'))
    #pprt=argnms.pprt
    #print(verdir)
    os.chdir(verdir)
    #get header parsing rule: to extract unique accession only
    #prfina=checkfile(os.path.join('classic','fasta','parser.json'))
    #prdic=json2dic(prfina)
    paru=PRDIC['UID']['PRO']['UniProt']
    vsfina=checkfile(os.path.join('version.json'))
    vsdic=json2dic(vsfina)
    #load sequence to seqdic
    #seqdic,idlis,rplis=loadfasta(ipfi,prdic['ID'])
    seqdic,idlis,rplis=loadfasta(ipfi,paru)
    loginfo('FASTA file Loaded successfully: %s'%ipfi)
    seqnu=len(idlis)
    loginfo('Total sequences: %s'%seqnu)
    #check feature file
    ftfina=checkfile(os.path.join('classic','table','features.tsv'),logtit='Warning',isexit=0)
    #load feature table
    ftdic={}
    ftlis=[]
    ftid=''
    if os.path.isfile(ftfina):
        ftdic,ftlis=loadtab(ftfina)
        ftid=ftlis[0]
        loginfo('Feature table file loaded successfully: %s'%ftfina)
    fasnm=getfn(ipfi)
    ofmt=argnms.ofmt
    tmpcvs='Conversion with %s (v%s) tool in SeqWiz'%(__appnm__,__appver__)
    tmpfix='up'
    tmpfsc='UniProt'
    bidx=1
    u2cvlis=['Ename','PName','GName','TaxName']
    u2cslis=['UpModRes','UpVariantSimple','UpProcessed','UpLinked','UpConflict']
    u2plis=u2cvlis+u2cslis
    u2pdic={'Ename':{'keys':['Entry name'],'valpat':''},
            'PName':{'keys':['Protein names'],'valpat':'pnms'},
            'GName':{'keys':['Gene names'],'valpat':'gnms'},
            'TaxName':{'keys':['Organism'],'valpat':'taxnm'},
            'UpModRes':{'keys':['Glycosylation','Lipidation','Modified residue'],'valpat':'mod','desc':'Modifications, annotated by UniProt'},
            'UpVariantSimple':{'keys':['Natural variant'],'valpat':'var','desc':'Natural variants, annotated by UniProt'},
            'UpProcessed':{'keys':['Chain','Peptide','Propeptide','Signal peptide','Transit peptide'],'valpat':'pro','desc':'Processed sequences, annotated by UniProt'},
            'UpLinked':{'keys':['Cross-link','Disulfide bond'],'valpat':'link','desc':'Linked residues, annotated by UniProt'},
            'UpConflict':{'keys':['Sequence conflict'],'valpat':'conflict','desc':'Sequence conflict, annotated by UniProt'}
                }
    u2kdic=keydic(u2pdic)
    dbdic=SQDIC['tablecont']
    if ofmt in ['peff','all']:
        #check peff dir and file
        optdir=checkdir(os.path.join('classic','peff'))
        #optfn=checkfile(os.path.join(optdir,'%s.peff'%fasnm),1)
        optfn=checkfile(os.path.join(optdir,'%s.peff'%'PEFF'),1)
        #generate comment files
        tmpcmt='''# PEFF 1.0
# //
# DbName=%s
# DbDescription=%s
# DbSource=%s
# DbVersion=%s
# DbDate=%s
# Prefix=%s
# NumberofEntries=%s
# Conversion=%s
# SequenceType=AA
# CustomKeyDef=(KeyName=UpModRes|Description="%s")
# CustomKeyDef=(KeyName=UpVariantSimple|Description="%s")
# CustomKeyDef=(KeyName=UpProcessed|Description="%s")
# CustomKeyDef=(KeyName=UpLinkded|Description="%s")
# CustomKeyDef=(KeyName=UpConflict|Description="%s")
# GeneralComment=(CommentName=FeatureSource|Description="UniProt:%s"|Source=%s)
# GeneralComment=(CommentName=Copyright|Description="Copyrighted by the UniProt Consortium, see http://www.uniprot.org/terms")
# GeneralComment=(CommentName=License|Description="Distributed under the Creative Commons Attribution-NoDerivs License")
# //
'''%(vsdic['database name'],
     'UniProt release: %s, species: %s, reference proteome: %s, reviewed sequences only: %s, remove fragment sequences: %s, remove isoform sequences: %s'%(vsdic['uniprot release'],vsdic['species'],vsdic['reference proteome'],vsdic['reviewed sequence only'],vsdic['remove fragment sequences'],vsdic['remove isoform sequences']),
     vsdic['fasta url'],vsdic['uniprot release'],vsdic['created date'],tmpfix,seqnu,tmpcvs,
     u2pdic['UpModRes']['desc'],u2pdic['UpVariantSimple']['desc'],u2pdic['UpProcessed']['desc'],u2pdic['UpLinked']['desc'],u2pdic['UpConflict']['desc'],','.join(u2plis),vsdic['table url'])
        with open(optfn,'w') as optobj:
            optobj.write(tmpcmt)
            for ei in idlis:
                tmphd='>%s:%s'%(tmpfix,ei)
                tmpsq=seqdic[ei][0]
                if ftid!='' and (ei in ftlis[1:]):
                    for eu in u2plis:
                        valpat=u2pdic[eu]['valpat']
                        tmpval=''
                        for ek in u2pdic[eu]['keys']:
                            ftidx=ftdic[ftid].index(ek)
                            tmpcolv=ftdic[ei][ftidx]
                            if tmpcolv:
                                #tmpval+=up2peff(tmpcolv,valpat,ek,len(tmpsq))
                                tmpval+=up2peff(tmpcolv,valpat,ek)
                        if tmpval:
                            tmphd+=' \\%s=%s'%(eu,tmpval)
                optobj.write('\n'.join([tmphd,tmpsq])+'\n')
        loginfo('PEFF file created: %s'%optfn)
    if ofmt in ['sqpd','all']:
        #check sqpd dir and file
        optdir=checkdir(os.path.join('next','sqpd'))
        #optfn=checkfile(os.path.join(optdir,'%s.db3'%fasnm),1)
        optfn=checkfile(os.path.join(optdir,'%s.db'%'SQPD'),1)
        #add comment table
        tbcmts=SQDIC['tablecmt']
        dbdic.update({'tablecmt':tbcmts})
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
        #write table annotation
        #tmpidx=1
        vallis=[]
        for dt in dbdic.items():
            dtkey,dtval=dt
            tmpflds=dtval['fields']
            tmpnts=dtval['notes']
            for efi in range(len(tmpflds)):
                #tbcmts['values'].append([tmpidx,dtkey,tmpflds[efi],tmpnts[efi][0],tmpnts[efi][1]])
                vallis.append((dtkey,tmpflds[efi],tmpnts[efi][0],tmpnts[efi][1]))
                #tmpidx+=1
        fldlis=dbdic['tablecmt']['fields'][1:]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('tablecmt',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,vallis,1)
        #write basic information
        fldlis=dbdic['basicinfo']['fields'][1:]
        vallis=[vsdic['database name'],vsdic['uniprot release'],vsdic['created date'],vsdic['fasta url'],'UniProt release: %s, species: %s, reference proteome: %s, reviewed sequences only: %s, remove fragment sequences: %s, remove isoform sequences: %s'%(vsdic['uniprot release'],vsdic['species'],vsdic['reference proteome'],vsdic['reviewed sequence only'],vsdic['remove fragment sequences'],vsdic['remove isoform sequences']),'up',seqnu,tmpcvs,'AA']
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('basicinfo',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,tuple(vallis))
        #write custom information
        fldlis=dbdic['custominfo']['fields'][1:]
        ftnms=ftdic[ftid][1:]
        vallis=[]
        ftkeys=[]
        for euk in ftnms:
            if euk in u2kdic:
                epk=u2kdic[euk]
                if epk not in ftkeys:
                    ftkeys.append(epk)
                    if epk in u2cslis:
                        vallis.append(('CustomKeyDef',epk,u2pdic[epk]['desc'],'',bidx))
            else:
                tmpnm=makenm(euk)
                if tmpnm not in ftkeys:
                    ftkeys.append(tmpnm)
                    vallis.append(('CustomKeyDef',tmpnm,euk,'',bidx))
        vallis+=[('GeneralComment','FeatureSource','%s:%s'%(tmpfsc,','.join(ftkeys)),'Source=%s'%vsdic['table url'],bidx),
                  ('GeneralComment','Copyright','Copyrighted by the UniProt Consortium, see http://www.uniprot.org/terms','',bidx),
                  ('GeneralComment','License','Distributed under the Creative Commons Attribution-NoDerivs License','',bidx)
            ]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('custominfo',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,vallis,1)
        #write sequences and features
        seqvallis=[]
        ftvallis=[]
        for ei in idlis:
            tmpseq=seqdic[ei][0]
            seqvallis.append((ei,tmpseq,bidx))
            if ftid!='' and (ei in ftlis[1:]):
                tmpfts=ftdic[ei][1:]
                for eidx in range(len(ftnms)):
                    tmpflis=[]
                    eft=tmpfts[eidx].strip()
                    if eft=='':
                        continue
                    euk=ftnms[eidx]
                    if euk in u2kdic:
                        epk=u2kdic[euk]
                        ftvallis.append((ei,epk,up2peff(eft,u2pdic[epk]['valpat'],euk),euk,tmpfsc,''))
                    else:
                        tmpnm=makenm(euk)
                        ftvallis.append((ei,tmpnm,eft,'',tmpfsc,''))
        fldlis=dbdic['sequences']['fields'][1:]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('sequences',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,seqvallis,1)
        fldlis=dbdic['features']['fields'][1:]
        sqltmp='INSERT INTO %s (%s) VALUES (%s)'%('features',','.join(fldlis),','.join(['?']*len(fldlis)))
        sql3_exe(optfn,sqltmp,ftvallis,1)
        loginfo('SQPD file created: %s'%optfn)





