#-*- coding: utf-8 -*-

#basic information
__appnm__='SeqAnnotate'
__appver__='1.0'
__appdesc__='Statistics of sequence composition and prediction of physicochemical properties (based on Biopython module)'

#load internal packages
import argparse
import sys
import os
import json
import re


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


#check third-party module
try:
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    from Bio.Data import IUPACData
except Exception as em:
    loginfo(str(em),logtit='Error',isexit=1)

stdaas=IUPACData.protein_letters

#from fastabase
aasgp=AASDIC['Properties']['Chemistry']

#functions
def predpp(aseq,ndec=2,iaas=0,gaas=0):
    #check standard aas
    valfmt='%0.'+str(ndec)+'f'
    aseq=re.sub('\s','',aseq)
    aseq=aseq.upper()
    aalis=list(set(aseq))
    adic={
        'ResidueCount':len(aseq),
        'NonStandardAAs':'',
        'AverageMass':'',
        'MonoisotopicMass':'',
        'IsoelectricPoint':'',
        'PhysilogicalCharge(PH7.4)':'',
        'ReducedMolarExtinction':'',
        'CystinesMolarExtinction':'',
        'Aromaticity(%)':'',
        'Instability':'',
        'GrandAverageOfHydropathy':''
        }
    for ea in aalis:
        if ea not in stdaas and ea not in adic['NonStandardAAs']:
            adic['NonStandardAAs']+=ea
    seqobj=ProteinAnalysis(aseq)
    mseq=ProteinAnalysis(aseq,True)
    if iaas:
        for ea in stdaas:
            adic['AminoAcidCount(%s)'%ea]=seqobj.count_amino_acids()[ea]
            adic['AminoAcidPercent(%s)'%ea]=valfmt%(100*(seqobj.get_amino_acids_percent()[ea]))
    if gaas:
        #for egk in aasgp.keys():
        for egk in aasgp:
            adic['AAsGroupCount(%s:%s)'%(egk,aasgp[egk])]=0
            adic['AAsGroupPercent(%s%%:%s)'%(egk,aasgp[egk])]=0
            for eaa in aasgp[egk]:
                adic['AAsGroupCount(%s:%s)'%(egk,aasgp[egk])]+=seqobj.count_amino_acids()[eaa]
                adic['AAsGroupPercent(%s%%:%s)'%(egk,aasgp[egk])]+=seqobj.get_amino_acids_percent()[eaa]
            adic['AAsGroupPercent(%s%%:%s)'%(egk,aasgp[egk])]=valfmt%(100*(adic['AAsGroupPercent(%s%%:%s)'%(egk,aasgp[egk])]))
    if not adic['NonStandardAAs'] or adic['NonStandardAAs'] in ['U','O','OU','UO']:
        #adic['ResidueCount']=seqobj.length
        adic['AverageMass']=valfmt%(seqobj.molecular_weight())
        adic['MonoisotopicMass']=valfmt%(mseq.molecular_weight())
        adic['IsoelectricPoint']=valfmt%(seqobj.isoelectric_point())
        adic['PhysilogicalCharge(PH7.4)']=valfmt%(seqobj.charge_at_pH(7.4))
        molec=seqobj.molar_extinction_coefficient()
        adic['ReducedMolarExtinction']=valfmt%(molec[0])
        adic['CystinesMolarExtinction']=valfmt%(molec[1])
        adic['Aromaticity(%)']=valfmt%(seqobj.aromaticity())
    if adic['NonStandardAAs']:
        return adic
    adic['Instability']=valfmt%(seqobj.instability_index())
    adic['GrandAverageOfHydropathy']=valfmt%(seqobj.gravy())
    return adic

if __name__=='__main__':
    #change to script dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #cmd arguments
    appnm='%s %s'%(__appnm__,__appver__)
    aparser=argparse.ArgumentParser(prog=appnm,description=__appdesc__)
    #input data file
    aparser.add_argument('ipfi',help='Souce file (absolute path)')
    aparser.add_argument('-t','--dtyp',required=True,choices=['sqpd','fasta','peff','peplis','set'],help='Data format')
    aparser.add_argument('-r','--paru',choices=PRDIC['UID']['PRO'].keys(),help='Parse rule for fasta/peff file')
    aparser.add_argument('-o','--odir',help='Output dir')
    aparser.add_argument('-l','--labn',help='Label name for output file')
    #show statistical results for individual amino acid
    aparser.add_argument('-i','--iaas',action='store_true',help='Show statistical results for individual AA')
    #show statistical results for grouped aminio acids
    aparser.add_argument('-g','--gaas',action='store_true',help='Show statistical results for grouped AAs')
    #number of decimal places: 2
    aparser.add_argument('-n','--ndec',type=int,default=2,help='Number of decimals [Default:%(default)s]')
    aparser.add_argument('-v','--version', action='version', version=__appver__)
    #get argument namespace
    argnms=aparser.parse_args()
    dtyp=argnms.dtyp
    paru=argnms.paru
    if dtyp in ['fasta','peff']:
        if not paru:
            loginfo('Parser rule required for fasta or peff file!','Error',isexit=1)
        if dtyp=='peff':
            paru='PEFF'
    #aas stat
    iaas=argnms.iaas
    gaas=argnms.gaas
    #check input file
    ipfi=checkfile(argnms.ipfi)
    dbnm=getfn(ipfi)
    odir=argnms.odir
    labn=argnms.labn
    ofnm='properties'
    if not labn:
        labn=''
    else:
        labn='_%s'%labn
    if odir:
        odir=checkdir(odir)
    else:
        verdir=checkdir(os.path.join(os.path.dirname(ipfi),'..','..'))
        #os.chdir(verdir)
        #check output file
        odir=checkdir(os.path.join(verdir,'classic','table'))
    optfn=checkfile(os.path.join(odir,'%s%s.tsv'%(ofnm,labn)),1)
    #number of decimals
    ndec=argnms.ndec
    valfmt='%0.'+str(ndec)+'f'
    #generate table header
    otits=['UniqueID','ResidueCount','NonStandardAAs']
    if iaas:
        for ea in stdaas:
            otits.append('AminoAcidCount(%s)'%ea)
            otits.append('AminoAcidPercent(%s%%)'%ea)
    if gaas:
        for egk in aasgp:
            otits.append('AAsGroupCount(%s:%s)'%(egk,aasgp[egk]))
            otits.append('AAsGroupPercent(%s%%:%s)'%(egk,aasgp[egk]))
    otits+=['AverageMass','MonoisotopicMass','IsoelectricPoint','PhysilogicalCharge(PH7.4)','ReducedMolarExtinction','CystinesMolarExtinction','Aromaticity(%)','Instability','GrandAverageOfHydropathy']
    #load sequence data
    if dtyp=='sqpd':
        sqltmp='select uid, sequence from sequences'
        atups=()
        seqlis=sql3_fch(ipfi,sqltmp,atups)
    elif dtyp in ['fasta','peff']:
        seqdic,idlis,rplis=loadfasta(ipfi,PRDIC['UID']['PRO'][paru])
        seqlis=[]
        for ei in idlis:
            seqlis.append((ei,seqdic[ei][0]))
    elif dtyp=='set':
        sdic=json2dic(ipfi)
        dbfi=checkfile(sdic['args']['dbfi'])
        idlis=sdic['selected']
        seqlis=[]
        for et in fchseqs(dbfi):
            if et[0] in idlis:
                seqlis.append((et[0],et[1]))
    elif dtyp=='peplis':
        seqlis=[]
        peplis=file2lis(ipfi)
        for ep in peplis:
            seqlis.append((ep,ep))
    loginfo('Load sequences successfully: %s'%ipfi)
    loginfo('Total sequences: %s'%len(seqlis))
    #loop for each sequence
    with open(optfn,'w') as optobj:
        optobj.write(joinlis(otits))
        for es in seqlis:
            #es: uid, sequence
            tmplis=[es[0],len(es[1])]
            tmpnsa=''
            for ea in list(set(es[1])):
                if ea not in stdaas and ea not in tmpnsa:
                    tmpnsa+=ea
            tmplis.append(tmpnsa)
            seqobj=ProteinAnalysis(es[1])
            mseq=ProteinAnalysis(es[1],True)
            if iaas:
                for ea in stdaas:
                    tmplis.append(seqobj.count_amino_acids()[ea])
                    tmplis.append(valfmt%(100*(seqobj.get_amino_acids_percent()[ea])))
            if gaas:
                for egk in aasgp:
                    tmpct=0
                    tmppc=0
                    for eaa in aasgp[egk]:
                        tmpct+=seqobj.count_amino_acids()[eaa]
                        tmppc+=seqobj.get_amino_acids_percent()[eaa]
                    tmppc=valfmt%(100*tmppc)
                    tmplis.append(tmpct)
                    tmplis.append(tmppc)
            if not tmpnsa or tmpnsa in ['U','O','OU','UO']:
                molec=seqobj.molar_extinction_coefficient()
                tmplis+=[valfmt%(seqobj.molecular_weight()),
                valfmt%(mseq.molecular_weight()),
                valfmt%(seqobj.isoelectric_point()),
                valfmt%(seqobj.charge_at_pH(7.4)),
                valfmt%(molec[0]),
                valfmt%(molec[1]),
                valfmt%(100*(seqobj.aromaticity()))]
            else:
                tmplis+=[''*7]
            if not tmpnsa:
                tmplis+=[valfmt%(seqobj.instability_index()),
                         valfmt%(seqobj.gravy())]
            else:
                tmplis+=[''*2]
            optobj.write(joinlis(tmplis))
    loginfo('Table file created successfully: %s'%optfn)


