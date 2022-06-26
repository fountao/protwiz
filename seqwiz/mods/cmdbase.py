#-*- coding: utf-8 -*-

#basic information
__appnm__='CMDBase'
__appver__='1.0'

#load internal packages
import sys
import os
import re
import json
import argparse
import datetime
import subprocess
from collections import OrderedDict

#template for numeric comparison
NPTDIC={'(min,max)':[2,'(%s>%s and %s<%s)','\((.+),(.+)\)'],
        '[min,max]':[2,'(%s>=%s and %s<=%s)','\[(.+),(.+)\]'],
        '(min,max]':[2,'(%s>%s and %s<=%s)','\((.+),(.+)\]'],
        '[min,max)':[2,'(%s>=%s and %s<%s)','\[(.+),(.+)\)'],
        '<=max':[1,'(%s<=%s)','<=(.+)'],
        '>=min':[1,'(%s>=%s)','>=(.+)'],
        '<max':[1,'(%s<%s)','<(.+)'],
        '>min':[1,'(%s>%s)','>(.+)'],
        '!=val':[1,'(%s!=%s)','!=(.+)'],
        '=val':[1,'(%s==%s)','=(.+)']}

#functions
#time format
def fmtime(dtobj='',dtpat='%m/%d/%Y, %H:%M:%S'):
    'dtpat: format date and time of datetime.datetime.now()'
    if not dtobj:
        dtobj=datetime.datetime.now()
    return dtobj.strftime(dtpat)

#log information
def loginfo(logcont='',logtit='Note',isexit=0,logloc='',msec=0):
    'report a log note'
    if msec==0:
        logtm=fmtime(dtpat='%x, %X')
    else:
        logtm=fmtime(dtpat='%x, %X, %f')
    if logloc:
        logtit='%s@%s'%(logtit,logloc)
    logtxt='>[%s] %s:\n%s\n'%(logtit,logtm,logcont)
    sys.stdout.write(logtxt)
    if isexit==1:
        sys.stdout.write('!Force exit')
        sys.exit(0)
    return


#absolute file and folder checking
def checkdir(adir,cktyp=0,getabs=1,logtit='Error',isexit=1,logloc=''):
    'check the existence and full path of a directory, 0: raise error if not exist, 1: raise error if already exist, 2: raise error if not abspath'
    if cktyp==2:
        if not os.path.isabs(adir):
            loginfo('Directory: "%s" is not an absolute path!\n' %adir,logtit,isexit,logloc)
    if getabs==1:
        adir=os.path.abspath(adir)
    if cktyp==0: 
        if not os.path.isdir(adir):
            loginfo('Directory: "%s" is not exist!\n' %adir,logtit,isexit,logloc)
    elif cktyp==1:
        if os.path.isdir(adir):
            loginfo('Directory: "%s" is already exist!\n' %adir,logtit,isexit,logloc)
    return adir

def checkfile(afile,cktyp=0,getabs=1,logtit='Error',isexit=1,logloc=''):
    'check the existence and full path of a file, 0: raise error if not exist, 1: raise error if already exist, 2: raise error if not abspath'
    if cktyp==2:
        if not os.path.isabs(afile):
            loginfo('File: "%s" is not an absolute path!\n' %afile,logtit,isexit,logloc)
    if getabs==1:
        afile=os.path.abspath(afile)
    if cktyp==0:
        if not os.path.isfile(afile):
            loginfo('File: "%s" is not exist!\n' %afile,logtit,isexit,logloc)
    elif cktyp==1:
        if os.path.isfile(afile):
            loginfo('File: "%s" is already exist!\n' %afile,logtit,isexit,logloc)
    return afile

#change file name
def chgfn(fina,prestr='',sufstr='',presym='_',sufsym='.', extsym='.',addstr='',extlel=1):
    dirnm=os.path.dirname(fina)
    finm=os.path.basename(fina)
    if extsym!='' and (extlel-1 in range(finm.count(extsym))):
        finm_rev=finm[::-1]
        revlis=re.split('[%s]'%extsym,finm_rev,extlel)
        revext=extsym.join(revlis[0:extlel])+extsym
        if sufstr:
            revext+=sufstr[::-1]+sufsym
        revfn=revlis[extlel]
        if prestr:
            revfn+=presym+prestr[::-1]
        chgedfn=(revext+revfn)[::-1]
        if addstr:
            chgedfn+=extsym+addstr
    else:
        chgedfn='%s%s%s%s%s%s'%(prestr,presym,finm,sufsym,sufstr,addstr)
    return os.path.join(dirnm,chgedfn)

def getfn(fina,extsym='.',extlel=1):
    #os.path.splitext()
    finm=os.path.basename(fina)
    if extsym!='' and (extlel-1 in range(finm.count(extsym))):
        finm_rev=finm[::-1]
        revlis=re.split('[%s]'%extsym,finm_rev,extlel)
        finm=revlis[-1][::-1]
    return finm

def json2dic(jsfina,odic=0):
    with open(jsfina,'r') as jsobj:
        if odic:
            jsdic=json.load(jsobj,object_pairs_hook=OrderedDict)
        else:
            jsdic=json.load(jsobj)
    return jsdic


def dic2json(adic,jsfina,pprt=0):
    with open(jsfina,'w') as jsobj:
        if pprt:
            json.dump(adic,jsobj,indent=4)
        else:
            json.dump(adic,jsobj)


def runcmd(cmdlis):
    'run cmd via subprocess with realtime output'
    process = subprocess.Popen(cmdlis, stdout=subprocess.PIPE, encoding='utf-8',stderr=subprocess.STDOUT)
    while True:
        realtime_output = process.stdout.readline()
        if realtime_output == '' and process.poll() is not None:
            break
        if realtime_output:
            print(realtime_output.strip(), flush=True)



