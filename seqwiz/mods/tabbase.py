#-*- coding: utf-8 -*-

#basic information
__appnm__='TabBase'
__appver__='1.0'

#load internal packages
import sys
import os
import re

#functions
#load data
def file2txt(fina,omod='r'):
    'read file to txt'
    tipf=open(fina,omod)
    rst=tipf.read()
    tipf.close()
    return rst

def file2lis(fina):
    'read file lines to a list, will ignore empty lines, based on file2txt()'
    #rst=re.findall('.+',re.sub('[\r\n]','\n',file2txt(fina)))
    rst=re.findall('.+',file2txt(fina))
    return rst

def file2tab(fina,etits=[],ktits=[],symb='\t'):
    'convert tab (or other symbols) separated text file to two-dimensional list data, based on file2lis()'
    rst=[]
    if etits==[] and ktits==[]:
        templis=file2lis(fina)
        for et in templis:
            rst.append(re.split(symb,et))
    else:
        tipf=open(fina,'r')
        eline=tipf.readline()
        #tmptits=re.split(symb,re.sub('[\r\n]','',eline))
        tmptits=re.split(symb,re.sub('[\n]','',eline))
        tmpidxlis=getlispos(etits+getkeystit(ktits,etits,tmptits),tmptits)
        while eline:
            #rst.append(selectlis(re.split(symb,re.sub('[\r\n]','',eline)),tmpidxlis))
            rst.append(selectlis(re.split(symb,re.sub('[\n]','',eline)),tmpidxlis))
            eline=tipf.readline()
        tipf.close()
    return rst

def file2dic(fina,sn=0,ckuni=0,rmkey=1,symb='\t'):
    'convert tab (or other symbols) separated text to dictionary, based on file2lis(), sn: the key index'
    #?add lis filter, comment issue
    rst={}
    templis=file2lis(fina)
    tnrows=len(templis)
    keylis=[]
    for et in templis:
        tmprlis=re.split(symb,et)
        tmpkey=tmprlis[sn]
        if tmpkey not in keylis:
            if rmkey==1:
                tmpidlis=range(len(tmprlis))
                tmpidlis.remove(sn)
                rst[tmpkey]=selectlis(tmprlis,tmpidlis)
            else:
                rst[tmpkey]=tmprlis
            keylis.append(tmpkey)
        else:
            if ckuni==1:
                #?logic wrong, better use raise
                #sys.stderr?
                assert tnrows==len(keylis),'The keys are not unique!'
            rst[tmpkey]=tmprlis
    return rst

def file2lis2(fina,kpept=0,strp=0,uni=0):
    '''read file lines (in universal newlines mode) to a list
    kpept: keep empty string ('')
    strp: remove space
    uni: remove redundant element'''
    #add to support one line data? add symb='\n'?
    tmplis=[]
    #default rU mode in py3.x
    with open(fina,'r') as iptobj:
        for el in iptobj.readlines():
            estr=re.sub('\n','',el)
            if strp:
                estr=estr.strip()
            if (not kpept) and (not estr):
                continue
            if uni and (estr in tmplis):
                continue
            tmplis.append(estr)
    return tmplis

def loadtab(fina,sn=0,keyerr=1,symb='\t'):
    'convert tab (or other symbols) separated text to two-dimensional list data, based on file2lis2(), sn: the key index'
    rst={}
    klis=[]
    templis=file2lis2(fina)
    #keylis=[]
    for et in templis:
        tmprlis=re.split(symb,et)
        tmpkey=tmprlis[sn]
        #if tmpkey not in keylis:
        if not tmpkey in klis:
            rst[tmpkey]=tmprlis
            klis.append(tmpkey)
            #keylis.append(tmpkey)
        else:
            if keyerr:
                #change to warnning
                #assert (EXP), (if err)
                raise KeyError('Key %s repeated!')
    return (rst,klis)


def unilis(alis):
    'remove redundancies in a list'
    rst=[]
    for ea in alis:
        if ea not in rst:
            rst.append(ea)
    return rst

def joinlis(alis,midstr='\t',endstr='\n'):
    'join a list with middle string (midstr) and end string (endstr)'
    tn=len(alis);jl='';i=0
    while i<tn:
        if i!=tn-1:
            jl+=str(alis[i])+midstr
        else:
            jl+=str(alis[i])+endstr
        i+=1
    return jl

def addlis(tlis,olis):
    'add elements of olis into tlis, non-redudant mode'
    for eo in olis:
        if eo not in tlis:
            tlis.append(eo)
    return tlis

def getpos(adat,alis,ckuni=1):
    'get the first position of adat in alis'
    if ckuni:
        assert alis.count(adat)==1,'The elements are not unique!'
    return alis.index(adat)

def getlispos(olis,tlis,ckuni=1):
    'get the first element positions of olis in tlis, based on getpos()'
    poslis=[]
    for eo in olis:
        poslis.append(getpos(eo,tlis,ckuni))
    return poslis

def getkeytit(keystr,extlis,titlis):
    'find elements with key string (keystr) in titlis, extlis: excluded elements list'
    rst=[]
    for et in titlis:
        if keystr in et and (not et in extlis):
            rst.append(et)
    return rst

def getkeycp(keystr,extlis,titlis):
    'find the complementary strings to keystr'
    rst=[]
    for et in titlis:
        if keystr in et and (not et in extlis):
            rst.append(re.sub(keystr,'',et))
    return rst

def getkeystit(keylis,extlis,titlis):
    'find elements with key strings in a list (substring), based on getkeytit()'
    rst=[]
    for et in titlis:
        for ek in keylis:
            if ek in et and (not et in extlis):
                rst.append(et)
    return rst

def getdickeys(aval,adic,vlis=0):
    'get the dict (list dict) key of a val, !first key'
    rst=[]
    for ea in adic.keys():
        if (vlis==1 and (aval in adic[ea])) or (vlis==0 and aval==adic[ea]):
            rst.append(ea)
    return rst

def checklis(tlis,olis):
    'check the existence of tlis in olis'
    for et in tlis:
        if et not in olis:
            raise Exception('Configuration file is not complete, dictionary key: "%s" is lost!' %et)

def selectlis(tlis,ilis):
    'select elements of tlis according to index numbers in ilis, will not check redundancy'
    #?add idxlis, klis, rlis; integrated to Tab class
    rst=[]
    tnu=len(tlis)
    for ei in ilis:
        if ei<=tnu-1 and ei>=0-tnu:
            rst.append(tlis[ei])
        else:
            raise IndexError('String index out of range')
    return rst

def removelis(tlis,olis):
    rlis=[]
    for et in tlis:
        if et not in olis and et not in rlis:
            rlis.append(et)
    return rlis

def lis2file(alis,fina):
    'write alis to fina, one element per line'
    topf=open(fina,'w')
    topf.writelines(joinlis(alis,'\n','\n'))
    topf.close()

def tab2file(atab,fina,transp=0):
    'write atab (2D list) to tsd (tab seperated data) file (fina), transp: transpose'
    if transp==1:
        atab=map(list,zip(*atab))
    topf=open(fina,'w')
    for et in atab:
        topf.writelines(joinlis(et))
    topf.close()
