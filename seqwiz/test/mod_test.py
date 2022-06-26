#-*- coding: utf-8 -*-

import sys
import os
import time


#get and add script path, add module paths
__rootpath__=os.path.dirname(os.path.abspath(__file__))
__basedir__=os.path.dirname(__rootpath__)
__scpnm__=os.path.basename(__file__)
os.chdir(__rootpath__)
sys.path.append(__rootpath__)
sys.path.append(os.path.join(__rootpath__,'..','mods'))

#load local packages
from fastabase import *

if __name__=='__main__':
    print('>>>start timer for SQPD')
    stm=time.time()
    asqpd='DROME_7227_SQPD.db'
    print('>>>choose a SQPD file: %s'%asqpd)
    print('>>>get all ids')
    uidlis=fchids(asqpd)
    print('>>>count IDs')
    print('>>>Total sequences: %s'%len(uidlis))
    '''
    #show first 10 IDs
    print('>>>show first 10 IDs')
    print(uidlis[:10])
    '''
    print('>>>get sequence of first ID')
    aid=uidlis[0][0]
    aseq=fchseq(asqpd,aid)
    print('>>>>%s\n%s'%(aid,aseq))
    print('>>>get gene name of first ID')
    print(fchfts(asqpd,aid,'GName'))
    '''
    #format sequence
    print('>>>format sequence')
    print('>>>>%s\n%s'%(aid,formatseq(aseq)))
    #get taxonomy name
    print('>>>get taxonomy name')
    print(fchfts(asqpd,aid,'TaxName'))
    #get entry name
    print('>>>get entry name')
    print(fchfts(asqpd,aid,'EName'))
    #get protein name of first ID
    print('>>>get protein name of first ID')
    print(fchfts(asqpd,aid,'PName'))
    #get sequence process information
    print('>>>get sequence process information')
    print(fchfts(asqpd,aid,'UpProcessed'))
    #get modification information
    print('>>>get modification information')
    print(fchfts(asqpd,aid,'UpModRes'))
    '''
    print('>>>show all avaliable feature keys')
    print(fchkeys(asqpd,aid))
    '''
    #show SQPD data structure for sequences
    #print('>>>show SQPD data structure for sequences')
    #print(json.dumps(SQDIC['tablecont']['sequences'],indent=4))
    #show SQPD data structure for features
    #print('>>>show SQPD data structure for features')
    #print(json.dumps(SQDIC['tablecont']['features'],indent=4))
    '''
    print('>>>end timer for SQPD')
    etm=time.time()
    print('>>>count timer')
    print('>>>The above processes take [%s] seconds'%(etm-stm))
    print('>>>start timer for a traditional FASTA/PEFF file')
    stm=time.time()
    afas='DROME_7227_PEFF.peff'
    print('>>>choose a FASTA/PEFF file: %s'%afas)
    '''
    #show build-in paser dic
    print('>>>show build-in paser dic')
    print(json.dumps(PRDIC['UID']['PRO'],indent=4))
    '''
    print('>>>load PEFF sequence file')
    print('>>>time consumming process ...')
    seqdic,idlis,rplis=loadfasta(afas,PRDIC['UID']['PRO']['PEFF'])
    print('>>>count sequences')
    print(len(idlis))
    print('>>>show first ID')
    print(idlis[0])
    print('>>>show first sequence')
    print(seqdic[idlis[0]][0])
    print('>>>show first header')
    print(seqdic[idlis[0]][1])
    print('>>>end timer for FASTA/PEFF')
    etm=time.time()
    print('>>>count timer')
    print('>>>The above processes take [%s] seconds'%(etm-stm))
    
    
    
    
    
    
    
    
    
