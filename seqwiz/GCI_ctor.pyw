#!/usr/bin/env python
# -*- coding: utf-8 -*-


#import official modules
import os
import re
import sys
import argparse
import textwrap
import subprocess
from functools import partial
import webbrowser
from io import BytesIO
import xml.etree.ElementTree as xmlmod
import json
from collections import OrderedDict

#import the 3rd-party modules
import wx
import wx.lib.scrolledpanel as scrd
import wx.adv
from wx.adv import Animation
from wx.adv import GenericAnimationCtrl as AnimationCtrl
import wx.lib.masked as masked
import wx.lib.agw.floatspin as FS

#get script path
scpdir=os.path.abspath(os.path.realpath(sys.argv[0]))
if not os.path.isdir(scpdir):
    scpdir=os.path.dirname(scpdir)
sys.path.append(scpdir)

#import local modules
import group_icons as gi

#required keys for validation of the configuration file
ckeydic={'appinfo':['name','version','description','developer','contact','homepage','license','standard'],
        'gcipars':['cuiapp','interpreter','atqctrl','cmdctrl','icon','logo','splash','fadeio','transparency','help','wait','sptime','spmaxsz','fontsz','logomaxsz','parasz','infowidth','descsz','titwrap','hpwrap','cmdsz','waitsz'],
        'cuipars':['title','type','style','flag','requirement','exclusive','limitation','default','help']
    }

def resource_path(relative):
    'get the paths of resource files after packaged in one file by pyinstaller'
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

#default gcipars
dfticon=os.path.join(scpdir,resource_path('dft_gci.ico'))
dftlogo=os.path.join(scpdir,resource_path('dft_gci_logo.png'))
dftwait=os.path.join(scpdir,resource_path('dft_gci_wait.gif'))
'''
spmaxsz=(480,240)
sptime=5
fontsz=12
logomaxsz=(120,120)
parasz=(640,360)
infowidth=520
descsz=(500,60)
titwrap=180
hpwrap=240
cmdsz=(600,72)
waitsz=(480,96)
'''

#functions
def json2dic(jsfina,odic=0):
    with open(jsfina,'r') as jsobj:
        if odic:
            jsdic=json.load(jsobj,object_pairs_hook=OrderedDict)
        else:
            jsdic=json.load(jsobj)
    return jsdic

def dic2xtab(adic):
    xtab=[]
    for ek,ev in adic.items():
        if isinstance(ev, dict):
        #isinstance(ev, OrderedDict)
            xtab.append([ek,dic2xtab(ev)])
        else:
            xtab.append([ek,checkipt(ev)])
    return xtab

def autoscale(pnlsize,imgsize):
    'scale image size to fit the panel size'
    pnlws,pnlhs=pnlsize
    imgws,imghs=imgsize
    if imgws>pnlws:
        tmpfct=float(imgws)/pnlws
        imgws=pnlws
        imghs=int(imghs/tmpfct)
    if imghs>pnlhs:
        tmpfct=float(imghs)/pnlhs
        imgws=int(imgws/tmpfct)
        imghs=pnlhs
    return (imgws,imghs)

def file2lis(fina):
    'load text file to a list, separated by new lines'
    #with open(fina,'rU') as fiobj:
    with open(fina,'r') as fiobj:
        templis=re.findall('.+',re.sub('[\r\n]','\n',fiobj.read()))
    return templis

def file2tab(fina,symb='\t'):
    'load tab (or other symbols) separated text file to two-dimensional list'
    rst=[]
    #with open(fina,'rU') as fiobj:
    with open(fina,'r') as fiobj:
        templis=re.findall('.+',re.sub('[\r\n]','\n',fiobj.read()))
    for et in templis:
        rst.append(re.split(symb,et))
    return rst

def file2dic(fina,symb='\t'):
    'load tab (or other symbols) separated text file to dict data'
    rst={}
    #with open(fina,'rU') as fiobj:
    with open(fina,'r') as fiobj:
        templis=re.findall('.+',re.sub('[\r\n]','\n',fiobj.read()))
    for et in templis:
        valis=re.split(symb,et,1)
        rst[valis[0]]=valis[1]
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


#wrap Windows path for safety
def wraparglis(argflag,arglis,spchars='[^a-zA-Z0-9\.:,;/_]',wrapstr='"'):
    'wrap argument list, paired double quotes are added to arguments with special symbols'
    #warning: under different operation systems, wrapping using double quotations may not disable some special actions, for example: "c:\" will becomes 'c:"' after wrapping under Windows
    tmplis=[]
    if argflag:
        tmplis.append(argflag)
    for ea in arglis:
        #wrap special characters to avoiding confusion
        if re.findall(spchars,ea):
            ea=wrapstr+ea+wrapstr
        tmplis.append(ea)
    return tmplis

def checkrunlis(alis):
    'remove empty elements'
    rstlis=[]
    for ea in alis:
        if ea:
            rstlis.append(ea)
    return rstlis

def xml2xtab(curnode):
    'parsing xml nodes and generate a nested list (formated as xtab)'
    xtab=[]
    cldlis=list(curnode)
    if len(cldlis)==0:
        tmptxt=curnode.text
        if not tmptxt:
            tmptxt=''
        xtab=[curnode.tag,checkipt(tmptxt)]
    else:
        xtab=[curnode.tag,[]]
        for ec in curnode:
            xtab[1].append(xml2xtab(ec))
    return xtab

def checkplis(olis,tlis):
    'compare olis (object) to tlis (target)'
    #eaqual label
    eqlb=0
    #repeat label
    rplb=0
    #missed elements, compared to tlis
    mislis=[]
    #added elements, compared to tlis
    addlis=[]
    #repeated elements in olis
    rptlis=[]
    colis=[]
    ctlis=[]
    for eo in olis:
        if eo.lower() in colis:
            rplb=1
            rptlis.append(eo.lower())
        colis.append(eo.lower())
    for et in tlis:
        ctlis.append(et.lower())
    colis.sort()
    ctlis.sort()
    if colis==ctlis:
        eqlb=1
    else:
        for eo in colis:
            if eo not in ctlis:
                addlis.append(eo)
        for et in ctlis:
            if et not in colis:
                mislis.append(et)
    #comparison description including repeated, missed and added elements
    cknote=''
    if rptlis:
        cknote+='Repeated parameters: [%s]. \n'%joinlis(rptlis,', ','')
    if mislis:
        cknote+='Missed parameters: [%s]. \n'%joinlis(mislis,', ','')
    if addlis:
        cknote+='Unknown parameters: [%s]. \n'%joinlis(mislis,', ','')
    return (eqlb,cknote)

def getrownames(atab,sn=0):
    'get the names of a tab (2-D list)'
    rst=[]
    for ea in atab:
        rst.append(ea[sn])
    return rst

def parsextab(xtab,cklis):
    'parsing xtab to a 2-D tab (tags are removed)'
    atab=[]
    errlis=[]
    for ex in xtab:
        tmplis=[]
        olis=[]
        for et in ex[1]:
            olis.append(et[0].lower())
            tmpval=et[1]
            if not tmpval:
                tmpval=''
            tmplis.append(tmpval)
        atab.append(tmplis)
        if olis!=cklis:
            errlis.append(ex[0])
    return (atab,errlis)

def parsepar(atab):
    'parsing parameters table'
    paradic={'position':{},'flag':{}}
    lisdic={'position':[],'flag':[]}
    cn=0
    #table without title
    for ea in atab:
        #check par integrity
        if not ea[3]:
            msgdlg('Flag label [No. %s] - [%s] can not be empty!\n Please check parameter file.'%(cn+1,ea[0]),'Error',fatal=1)
        tmpcls=('position' if ea[3][0]!='-' else 'flag')
        lisdic[tmpcls].append(cn)
        paradic[tmpcls][cn]={}
        paradic[tmpcls][cn]['title']=ea[0]
        paradic[tmpcls][cn]['type']=ea[1]
        paradic[tmpcls][cn]['style']=ea[2]
        paradic[tmpcls][cn]['flag']=(ea[3] if tmpcls=='flag' else '')
        paradic[tmpcls][cn]['require']=ea[4]
        if tmpcls=='position':
            paradic[tmpcls][cn]['require']='yes'
        paradic[tmpcls][cn]['exclude']=ea[5]
        paradic[tmpcls][cn]['limit']=ea[6]
        paradic[tmpcls][cn]['default']=ea[7]
        paradic[tmpcls][cn]['help']=ea[8]
        #for sorted number, defined and assigned in auto_ctrls(self,pclass)
        #paradic[tmpcls][cn]['sort']=0
        #dic for storing parameter widgets, generated in auto_ctrls(self,pclass)
        paradic[tmpcls][cn]['ctrls']={}
        cn+=1
    return (lisdic,paradic)

def parserg(valrg):
    'parsing range type: [lowval,upval]'
    rglis=re.split(',',re.sub('\s','',valrg.lower()))
    lowlb=rglis[0][0]
    uplb=rglis[1][-1]
    lowlm=rglis[0][1:]
    uplm=rglis[1][:-1]
    if (rglis[0][0] not in '([' or  rglis[1][-1] not in ')]'):
        raise Exception('limit condition error: %s'%valrg)
    rgdic={'(':'>','[':'>=',')':'<',']':'<='}
    lowcd=rgdic[rglis[0][0]]
    upcd=rgdic[rglis[1][-1]]
    #warning: be caution with inf and -inf value as python does not fully support infinite features
    if lowlm=='inf' or uplm=='-inf':
        raise Exception('Range value error: %s'%valrg)
    if rglis[0][1:]!='-inf':
        lowval=float(lowlm)
    else:
        lowval='-inf'
    if rglis[1][:-1]!='inf':
        upval=float(uplm)
    else:
        upval='inf'
    if (lowval!='-inf' and upval!='inf') and (lowval>upval):
        raise Exception('Range value error: %s'%valrg)
    return [(lowlb,lowlm,uplm,uplb),(lowcd,lowval,upval,upcd)]

def rgfilter(aval,rgtub):
    'value (aval) filter based on value range (valrg, string in standard interval format)'
    hitlb=0
    lowcd,lowval,upval,upcd=rgtub
    if (lowval=='-inf' and upval=='inf'):
        hitlb=1
        return hitlb
    #pay attention to the safety issue of eval()
    if (lowval=='-inf' and eval(str(aval)+upcd+str(upval))) or (upval=='inf' and eval(str(aval)+lowcd+str(lowval))) or (lowval!='-inf' and upval!='inf' and eval(str(aval)+upcd+str(upval)) and eval(str(aval)+lowcd+str(lowval))):
        hitlb=1
    return hitlb

def checkipt(iptdat):
    'check input text, remove redundant (leading and trailing) spaces'
    #warning: strip() belongs to string methods, but applicable to unicode data??
    if type(iptdat)==list or type(iptdat)==tuple:
        rst=[]
        for ei in iptdat:
            if ei.strip():
                rst.append(ei.strip())
    #string or unicode
    else:
        rst=iptdat.strip()
    return rst

def checkpath(pathobj):
    'check absolute paths'
    if not pathobj:
        return pathobj
    if type(pathobj)==list or type(pathobj)==tuple:
        rstpath=[]
        for ep in pathobj:
            if os.path.isabs(ep):
                rstpath.append(ep)
            else:
                rstpath.append(os.path.abspath(ep))
    #string or unicode
    else:
        if os.path.isabs(pathobj):
            rstpath=pathobj
        else:
            rstpath=os.path.abspath(pathobj)
    return rstpath

def htm2rgb(cstr):
    'convert html colour text to rgb colour tuple'
    if cstr[0] == '#':
        hexc = cstr[1:]
    if len(hexc) != 6:
        #raise ValueError('Wrong HTML colour format!')
        raise Exception('Wrong HTML colour format!')
    tmpr, tmpg, tmpb = hexc[:2], hexc[2:4], hexc[4:]
    rstr, rstg, rstb = [int(n, 16) for n in (tmpr, tmpg, tmpb)]
    return (rstr, rstg, rstb)

def rgb2gray(rgbtb):
    'calculate the gray value of a rgb color'
    rval,gval,bval=rgbtb
    return (rval*30 + gval*59 + bval*11 + 50)/100

def dic2tab(adic,alis):
    'convert a dic to a tab according to the order of alis'
    rst=[]
    for ea in alis:
        if ea in adic.keys():
            rst.append([ea,adic[ea]])
        else:
            rst.append([ea,''])
    return rst

def tab2dic(atab):
    'convert a configuration tab (2 element) to a dic (key: value)'
    rstdic={}
    for ea in atab:
        tmpval=''
        if ea[1]:
            tmpval=ea[1]
        rstdic[ea[0]]=tmpval
    return rstdic

def msgdlg(msgtxt,msgtit='Note',msgsty=wx.OK,fatal=0):
    'message dialogy for displaying note and error information'
    errdlg=wx.MessageDialog(None,textwrap.fill(msgtxt,50),msgtit,msgsty)
    errdlg.ShowModal()
    errdlg.Destroy()
    if fatal==1:
        sys.exit(0)

class MsgDialog(wx.Dialog):
    'message dialog for auto close'
    def __init__(self, amsg, title,actime=0):
        wx.Dialog.__init__(self, None, -1, title)

        okbtn = wx.Button(self, wx.ID_OK, "OK",style=wx.BU_EXACTFIT)
        stext = wx.StaticText(self, -1, amsg)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(stext, 0, wx.ALIGN_CENTER|wx.TOP, 5)

        #auto close time (in seconds)
        self.actime=actime
        if self.actime>0:
            self.actimer=wx.Timer(self,id=1)
            self.Bind(wx.EVT_TIMER, self.autoclose,id=1)
            self.actext=wx.StaticText(self, -1, 'Closing this dialog box in %s...'%self.actime)
            vbox.Add(self.actext, 0, wx.ALIGN_CENTER|wx.TOP, 5)
        vbox.Add(wx.StaticLine(self,-1,size=(270,-1)),0,wx.ALL|wx.EXPAND,5)
        vbox.Add(okbtn, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)
        self.SetSizer(vbox)
        vbox.Fit(self)
        self.Center()

        if self.actime>0:
            self.actimer.Start(1000)

    def autoclose(self, evt):
        self.actime-=1
        self.actext.SetLabel('Closing this dialog box in %s...'%self.actime)
        if self.actime<=0:
            self.actimer.Stop()
            self.Destroy()

class ImgSplash(wx.MiniFrame):
    'image splash'
    def __init__(
        self,parent,imgpath='',pos=wx.DefaultPosition,size=(480,240),
        style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR|wx.NO_BORDER):
        self.imgpath=os.path.abspath(imgpath)
        self.size=size
        wx.MiniFrame.__init__(self, parent, -1,'', pos, size, style)
        imgtyp=re.split('\.',os.path.basename(self.imgpath))[-1].lower()
        self.SetBackgroundColour('#1A0003')
        mainbox=wx.BoxSizer(wx.VERTICAL)
        if imgtyp=='gif':
            ani=Animation(self.imgpath)
            self.img=AnimationCtrl(self, -1, ani,size=self.size)
            self.img.SetUseWindowBackgroundColour()
            self.img.Play()
        else:
            with open(self.imgpath,'rb') as imgdat:
                imgstm=BytesIO(imgdat.read())
                imgobj=wx.Image(imgstm)
                tmpws,tmphs=autoscale(self.size,imgobj.GetSize())
                imgobj=imgobj.Scale(tmpws,tmphs,wx.IMAGE_QUALITY_HIGH)
                imgobj=wx.Bitmap(imgobj)
                self.img=wx.StaticBitmap(self,-1,imgobj)
        self.img.SetToolTip('Powered by '+__version__)
        mainbox.Add(self.img,0,wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,0)
        self.SetSizer(mainbox)
        mainbox.Fit(self)
        self.Center()
        
        #fade-in and fade-out
        #initial transparent
        self.amount = 10
        #transparent increment
        self.delta = 10
        #start timer
        self.stimer = wx.Timer(self,id=1)
        self.SetTransparent(self.amount)
        self.stimer.Start(100)
        self.Bind(wx.EVT_TIMER, self.fadein,id=1)

        self.Show()

        #display setting, last for 3 seconds
        self.ltime=3
        #display timer
        self.ltimer = wx.Timer(self,id=2)
        self.Bind(wx.EVT_TIMER, self.onTimer,id=2)
        #close timer
        self.ctimer = wx.Timer(self,id=3)
        self.Bind(wx.EVT_TIMER, self.fadeout,id=3)

    def fadein(self, evt):
        self.amount += self.delta
        if self.amount >= 250:
            self.amount = 250
            self.stimer.Stop()
            self.ltimer.Start(1000)
        self.SetTransparent(self.amount)

    def onTimer(self,event):
        self.ltime-=1
        if self.ltime<=0:
            self.ltimer.Stop()
            self.ctimer.Start(50)

    def fadeout(self, evt):
        self.amount -= self.delta
        if self.amount <= 0:
            self.amount = 0
            self.ctimer.Stop()
            self.Destroy()
        self.SetTransparent(self.amount)

class HelpPopup(wx.PopupWindow):
    'displaying help information'
    def __init__(self, parent, style,hpwrap,hptit='',hptxt=''):
        wx.PopupWindow.__init__(self, parent, style)
        pnl = self.pnl = wx.Panel(self,-1)
        mainsz=wx.BoxSizer(wx.VERTICAL)
        titsizer=wx.BoxSizer(wx.HORIZONTAL)
        infoicon=wx.StaticBitmap(pnl,-1,wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,size=(16,16)))
        titsizer.Add(infoicon,0,flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=2)
        helptit=wx.StaticText(pnl, -1,hptit)
        helptit.Wrap(200)
        titsizer.Add(helptit,0,wx.ALL|wx.LEFT|wx.EXPAND,5)
        mainsz.Add(titsizer,0,wx.ALL|wx.LEFT|wx.EXPAND,5)
        mainsz.Add(wx.StaticLine(pnl,-1),0,wx.ALL|wx.EXPAND,0)
        hpinfo=wx.StaticText(pnl, -1,hptxt)
        hpinfo.Wrap(hpwrap)
        mainsz.Add(hpinfo,0,wx.ALL|wx.LEFT|wx.EXPAND,2)
        mainsz.Add(wx.StaticLine(pnl,-1),0,wx.ALL|wx.EXPAND,0)
        clsbtn=wx.Button(pnl,label='Close',style=wx.BU_EXACTFIT)
        clsbtn.Bind(wx.EVT_BUTTON, self.ClosePop)
        mainsz.Add(clsbtn,0,wx.ALL|wx.ALIGN_CENTER,2)
        
        pnl.SetSizer(mainsz)
        mainsz.Fit(pnl)
        mainsz.Fit(self)
        self.Layout()

        pnl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        pnl.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        pnl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        pnl.Bind(wx.EVT_RIGHT_UP, self.ClosePop)

        hpinfo.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        hpinfo.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        hpinfo.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        hpinfo.Bind(wx.EVT_RIGHT_UP, self.ClosePop)

        pnl.SetSize(240,-1)
        self.SetSize(240,-1)
        wx.CallAfter(self.Refresh)
        
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.pnl.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                    self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        if self.pnl.HasCapture():
            self.pnl.ReleaseMouse()

    def ClosePop(self, evt):
        self.Show(False)
        self.Destroy()

class AppInfo(wx.MiniFrame):
    'displaying app information'
    def __init__(self,parent=None,infotab=[]):
        wx.MiniFrame.__init__(self,parent, wx.ID_ANY, 'App information',style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER|wx.STAY_ON_TOP)
        mainpnl= wx.Panel(self, -1)
        mainsz=wx.BoxSizer(wx.VERTICAL)
        infosz=wx.FlexGridSizer(cols=2,hgap=5,vgap=5)
        for ei in infotab:
            if ei[0].title()!='Description':
                infosz.Add(wx.StaticText(mainpnl,-1,ei[0].title()),flag=wx.EXPAND)
                infosz.Add(wx.TextCtrl(mainpnl,-1,value=ei[1],size=(270, -1),style=wx.TE_READONLY),1,wx.EXPAND)
            else:
                infosz.Add(wx.StaticText(mainpnl,-1,ei[0].title()),flag=wx.EXPAND)
                desctxt=wx.TextCtrl(mainpnl,-1,value=ei[1],size=(270,90),style=wx.TE_MULTILINE|wx.TE_READONLY)
                desctxt.SetBackgroundColour(wx.NullColour)
                infosz.Add(desctxt,1,wx.EXPAND)
        infosz.AddGrowableCol(1)
        mainsz.Add(infosz,0,wx.ALL|wx.EXPAND,5)
        mainpnl.SetSizer(mainsz)
        mainsz.Fit(self)
        self.Center()

class LogDlg(wx.MiniFrame):
    'display and manage log information for real-time running'
    def __init__(
        self,parent,title='Real-time log information',pos=wx.DefaultPosition,size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER^wx.CLOSE_BOX):
        #style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER|wx.STAY_ON_TOP):
        self.title=title
        self.parent=parent
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        #creat frame background container
        self.fbg=wx.Panel(self,wx.ID_ANY)

        self.cont=wx.TextCtrl(self.fbg,-1,'',size=(480,480),style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.cont.SetEditable(False)
        self.cont.Bind(wx.EVT_SET_FOCUS, self.emptyfunc)
        self.cont.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        funcbox=wx.BoxSizer(wx.HORIZONTAL)
        self.clearbut=wx.Button(self.fbg,label='Clear')
        self.stopbut=wx.Button(self.fbg,label='Stop')
        self.savebut=wx.Button(self.fbg,label='Export')
        self.closebut=wx.Button(self.fbg,label='Close')
        funcbox.Add(self.clearbut,proportion=0,flag=wx.CENTER,border=5)
        funcbox.Add(self.stopbut,proportion=0,flag=wx.CENTER,border=5)
        funcbox.Add(self.savebut,proportion=0,flag=wx.CENTER,border=5)
        funcbox.Add(self.closebut,proportion=0,flag=wx.CENTER,border=5)
        self.clearbut.Bind(wx.EVT_BUTTON,self.OnClear)
        self.stopbut.Bind(wx.EVT_BUTTON,self.OnStop)
        self.closebut.Bind(wx.EVT_BUTTON,self.OnClose)
        self.savebut.Bind(wx.EVT_BUTTON,self.savefile)

        infobox=wx.BoxSizer(wx.VERTICAL)
        infobox.Add(self.cont,1,wx.ALL|wx.EXPAND,5)
        infobox.Add(funcbox,0,wx.ALL|wx.CENTER,5)

        self.fbg.SetSizer(infobox)
        infobox.Fit(self)
        #self.SetTransparent(240)
        self.Center()

        self.Show()

    def emptyfunc(self, event):
        pass

    def OnClose(self, event):
        #self.parent.Destroy()
        self.OnStop(None)
        self.parent.Destroy()
        self.Show(False)
        self.Destroy()

    def OnClear(self,event):
        self.cont.SetValue('')

    def OnStop(self,event):
        try:
            if self.parent.runpcs:
                #self.parent.runpcs.terminate()
                self.parent.runpcs.kill()
        except Exception as em:
            sys.stdout.write(str(em)+'\n')

    def write(self,infotext):
        self.cont.AppendText(infotext)

    def savefile(self,event):
        dlg=wx.FileDialog(
            self,message="Choose a file",
            defaultFile="",
            wildcard="Tab separated data (*.tsd)|*.tsd|All files (*.*)|*.*",
            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
            )
        if not self.cont.GetValue():
            errdlg=wx.MessageDialog(None,'Empty data!','Error',wx.OK|wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
            return
        if dlg.ShowModal()==wx.ID_OK:
            paths=dlg.GetPath()
            with open(paths,'w') as topf:
                topf.write(self.cont.GetValue())
            notedlg=wx.MessageDialog(None,'Export information completed!','Note',wx.OK)
            notedlg.ShowModal()
            notedlg.Destroy()
        else:
            pass
        dlg.Destroy()

class WaitDlg(wx.MiniFrame):
    'dispalying wait dialog for background running'
    def __init__(
        self,parent,title='Background processing ...',asize=[-1,-1],pos=wx.DefaultPosition,size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER):
        #style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER|wx.STAY_ON_TOP):
        self.title=title
        self.parent=parent
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        #creat frame background container
        self.fbg=wx.Panel(self,wx.ID_ANY)
        self.waitimg=AnimationCtrl(self.fbg, -1,Animation(self.parent.waitpath),size=asize)
        self.waitimg.SetUseWindowBackgroundColour()
        self.waitimg.Play()
        funcbox=wx.BoxSizer(wx.HORIZONTAL)
        self.stopbut=wx.Button(self.fbg,label='Stop')
        self.closebut=wx.Button(self.fbg,label='Close')
        funcbox.Add(self.stopbut,proportion=0,flag=wx.CENTER,border=5)
        funcbox.Add(self.closebut,proportion=0,flag=wx.CENTER,border=5)
        self.stopbut.Bind(wx.EVT_BUTTON,self.OnStop)
        self.closebut.Bind(wx.EVT_BUTTON,self.OnClose)

        self.infobox=wx.BoxSizer(wx.VERTICAL)
        self.infobox.Add(self.waitimg,1,wx.ALL|wx.EXPAND,5)
        self.infobox.Add(funcbox,0,wx.ALL|wx.CENTER,5)

        self.fbg.SetSizer(self.infobox)
        self.infobox.Fit(self)
        #self.SetTransparent(240)
        self.Center()

        self.Show()

    def OnClose(self, event):
        #self.parent.Destroy()
        if self.parent.runpcs:
            self.parent.runpcs.kill()
        self.parent.Destroy()
        #self.Show(False)
        #self.Destroy()

    def OnStop(self,event):
        self.waitimg.Stop()
        self.parent.runpcs.kill()


class MainFrame(wx.Frame):
    'main gui frame'
    def __init__(
        self,parent,cfgpath,pos=wx.DefaultPosition,size=wx.DefaultSize,
        #style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX)|wx.MINIMIZE_BOX
        style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX)|wx.MINIMIZE_BOX
        ):
        wx.Frame.__init__(self, parent, -1, '', pos, size, style)
        #scpdir: script directory, defined globally after importing modules
        self.scpdir=scpdir
        self.cfgpath=os.path.abspath(cfgpath)
        #check configuration file
        if not os.path.isfile(self.cfgpath):
            msgdlg('GCI configuration file: [ %s ] is not exist!'%self.cfgpath,'Error',fatal=1)
        #parsing configurations
        gcidic=json2dic(self.cfgpath,1)
        cfglis=[]
        #for py3.x, ek = each key
        for ek in gcidic:
            cfglis.append(ek)
        #for py3.x, dict.keys() return not list
        tmplb,tmpnote=checkplis(cfglis,list(ckeydic.keys()))
        if not tmplb:
            msgdlg('Configuration error in root node: \n%s'%tmpnote,'Error',fatal=1)
        #checking parameters
        self.infodic=gcidic['appinfo']
        tmplb,tmpnote=checkplis(list(self.infodic.keys()),ckeydic['appinfo'])
        if not tmplb:
            msgdlg('Configuration error in appinfo: \n%s'%tmpnote,'Error',fatal=1)
        self.gpardic=gcidic['gcipars']
        tmplb,tmpnote=checkplis(list(self.gpardic.keys()),ckeydic['gcipars'])
        if not tmplb:
            msgdlg('Configuration error in gcipars: \n%s'%tmpnote,'Error',fatal=1)
        if not self.gpardic['cuiapp']:
            msgdlg('Configuration error: \n cuiapp is required! \n (The file name with extension for the CUI app.)','Error',fatal=1)
        cuixtabs=dic2xtab(gcidic['cuipars'])
        for ec in cuixtabs:
            tmpid=ec[0]
            tmptab=ec[1]
            tmplb,tmpnote=checkplis(getrownames(tmptab),ckeydic['cuipars'])
            if not tmplb:
                msgdlg('Configuration error in cuipars: \n%s'%tmpnote,'Error',fatal=1)
        self.cuidir=os.path.dirname(self.cfgpath)
        self.cuipath=os.path.join(self.cuidir,self.gpardic['cuiapp'])
        if not os.path.isfile(self.cuipath):
            msgdlg('CUI app [ %s ] is not exist!'%self.gpardic['cuiapp'],'Error',fatal=1)
        self.appname=os.path.splitext(self.gpardic['cuiapp'])[0]
        #update title
        self.title=''
        if self.infodic['name']:
            self.title+=self.infodic['name']
        else:
            self.title+=self.appname
        if self.infodic['version']:
            self.title+=' - %s'%self.infodic['version']
        self.SetTitle(self.title)
        #check style files
        self.splashpath=os.path.join(self.cuidir,self.gpardic['splash'])
        #if not self.gpardic['splash'] or not os.path.exists(self.splashpath):
        if not os.path.isfile(self.splashpath):
            self.splashpath=''
        self.icopath=os.path.join(self.cuidir,self.gpardic['icon'])
        if not os.path.isfile(self.icopath):
            self.icopath=dfticon
        self.logopath=os.path.join(self.cuidir,self.gpardic['logo'])
        if not os.path.isfile(self.logopath):
            self.logopath=dftlogo
        self.waitpath=os.path.join(self.cuidir,self.gpardic['wait'])
        if not os.path.isfile(self.waitpath):
            self.waitpath=dftwait
        #check help doc for the cui-app
        self.help_path=os.path.join(self.cuidir,self.gpardic['help'])
        if not os.path.isfile(self.help_path):
            self.help_path=''
        #load group icons
        self.gpicons={}
        self.gpicons['required']=wx.Bitmap(gi.required.GetImage().Scale(16,16,wx.IMAGE_QUALITY_HIGH))
        self.gpicons['not_required']=wx.Bitmap(gi.not_required.GetImage().Scale(16,16,wx.IMAGE_QUALITY_HIGH))
        self.gpicons['exclusive']=wx.Bitmap(gi.exclusive.GetImage().Scale(16,16,wx.IMAGE_QUALITY_HIGH))
        self.gpicons['not_exclusive']=wx.Bitmap(gi.not_exclusive.GetImage().Scale(16,16,wx.IMAGE_QUALITY_HIGH))
        #wrapped CMD list for exporting and importing
        self.cmdlis=[]
        #CMD list running without wrapping / exporting to py data
        self.runlis=[]
        #masked text ctrl for displaying
        #self.cmdtxt
        #special CMDs for QA based user interaction
        self.atqlis=[]
        os.chdir(self.cuidir)
        #set icon
        tmpimg=wx.Image(self.icopath, wx.BITMAP_TYPE_ANY)
        tmpobj=wx.Bitmap(tmpimg)
        self.icon=wx.Icon()
        self.icon.CopyFromBitmap(tmpobj)
        self.SetIcon(self.icon)
        #set font and background
        if not self.gpardic['fontsz']:
            self.gpardic['fontsz']='12'
        fontsz=int(self.gpardic['fontsz'])
        #self.SetFont(wx.FFont(fontsz,wx.FONTFAMILY_DEFAULT))
        self.SetBackgroundColour(wx.NullColour)
        #boldft=wx.Font(fontsz,wx.DEFAULT,wx.NORMAL,weight=wx.BOLD)
        #export type dic for cmdtxt
        self.stypdic={0:'w',1:'a'}
        #check interpreter
        self.intprt=''
        if  self.gpardic['interpreter']:
            self.intprt=self.gpardic['interpreter']
        #check transparency
        if not self.gpardic['transparency']:
            self.gpardic['transparency']='255'
        self.transprc=int(self.gpardic['transparency'])
        if self.transprc<200:
            self.transprc=200
        if self.transprc>255:
            self.transprc=255
        #start/current transprc
        self.amount=self.transprc
        if  self.gpardic['fadeio']=='True':
            self.amount=5
        #check size
        if not self.gpardic['spmaxsz']:
            self.gpardic['spmaxsz']='[480,240]'
        if not self.gpardic['logomaxsz']:
            self.gpardic['logomaxsz']='[120,120]'
        if not self.gpardic['parasz']:
            self.gpardic['parasz']='[640,360]'
        if not self.gpardic['descsz']:
            self.gpardic['descsz']='[500,60]'
        if not self.gpardic['cmdsz']:
            self.gpardic['cmdsz']='[600,72]'
        if not self.gpardic['waitsz']:
            self.gpardic['waitsz']='[480,96]'
        for es in ['spmaxsz','logomaxsz','parasz','descsz','cmdsz','waitsz']:
            self.gpardic[es]=json.loads(self.gpardic[es])
        if not self.gpardic['sptime']:
            self.gpardic['sptime']='5'
        self.gpardic['sptime']=int(self.gpardic['sptime'])
        if not self.gpardic['infowidth']:
            self.gpardic['infowidth']='520'
        self.gpardic['infowidth']=int(self.gpardic['infowidth'])
        if not self.gpardic['titwrap']:
            self.gpardic['titwrap']='180'
        self.gpardic['titwrap']=int(self.gpardic['titwrap'])
        if not self.gpardic['hpwrap']:
            self.gpardic['hpwrap']='240'
        self.gpardic['hpwrap']=int(self.gpardic['hpwrap'])
        #top sizer
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        #info panel
        infopnl=wx.Panel(self,size=(self.gpardic['parasz'][0],-1))
        #info sizer
        infosizer=wx.BoxSizer(wx.HORIZONTAL)
        infopnl.SetSizer(infosizer)
        #CUI logo
        imgtyp=re.split('\.',os.path.basename(self.logopath))[-1].lower()
        if imgtyp=='gif':
            logoanm=Animation(self.logopath)
            self.cuilogo=AnimationCtrl(infopnl, -1,logoanm,size=self.gpardic['logomaxsz'])
            self.cuilogo.SetUseWindowBackgroundColour()
            self.cuilogo.Play()
            self.cuilogo.Bind(wx.EVT_LEFT_DCLICK, self.logoplayer)
        else:
            with open(self.logopath,'rb') as imgdat:
                imgstm=BytesIO(imgdat.read())
                imgobj=wx.Image(imgstm)
                tmpws,tmphs=autoscale(self.gpardic['logomaxsz'],imgobj.GetSize())
                imgobj=imgobj.Scale(tmpws,tmphs,wx.IMAGE_QUALITY_HIGH)
                imgobj=wx.Bitmap(imgobj)
                self.cuilogo=wx.StaticBitmap(infopnl,-1,imgobj)
        #self.cuilogo.SetToolTip(self.infodic['name']+' logo')
        infosizer.Add(self.cuilogo,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,0)
        #description sizer
        descbox=wx.StaticBox(infopnl, -1, self.infodic['name'])
        descsizer = wx.StaticBoxSizer(descbox, wx.VERTICAL)
        descsizer.SetMinSize((self.gpardic['infowidth'],-1))
        desctext =wx.TextCtrl(infopnl,-1,value=self.infodic['description'],size=self.gpardic['descsz'],style=wx.TE_MULTILINE|wx.TE_READONLY)
        desctext.SetBackgroundColour(wx.NullColour)
        #prevent input blinking and change cursor to default arrow
        desctext.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        desctext.Bind(wx.EVT_SET_FOCUS, self.emptyfunc)
        descsizer.Add(desctext, 0, wx.TOP|wx.LEFT|wx.EXPAND,5)
        descsizer.Add(wx.StaticLine(infopnl,-1),0,wx.ALL|wx.EXPAND,5)
        #help sizer
        helpsizer=wx.BoxSizer(wx.HORIZONTAL)
        infotxt=wx.StaticText(infopnl, label="About")
        #infotxt.SetFont(boldft)
        infotxt.SetToolTip('Detailed APP information')
        infotxt.SetForegroundColour('Blue')
        infotxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        infotxt.Bind(wx.EVT_LEFT_UP, partial(self.dspinfo,infotab=dic2tab(self.infodic,ckeydic['appinfo'])))
        doctxt=wx.StaticText(infopnl, label="Docs")
        #doctxt.SetFont(boldft)
        doctxt.SetToolTip('Local user documentation')
        doctxt.SetForegroundColour('Blue')
        doctxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        if self.help_path:
            doctxt.Bind(wx.EVT_LEFT_UP, partial(self.loc_brs,fipath=self.help_path))
        hptxt=wx.StaticText(infopnl, label="Homepage")
        #hptxt.SetFont(boldft)
        hptxt.SetToolTip('APP homepage')
        hptxt.SetForegroundColour('Blue')
        hptxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        if self.infodic['homepage']:
            hptxt.Bind(wx.EVT_LEFT_UP, partial(self.web_brs, weblink=self.infodic['homepage']))
        helpsizer.Add(infotxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        helpsizer.Add(wx.StaticLine(infopnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        helpsizer.Add(doctxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        helpsizer.Add(wx.StaticLine(infopnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        helpsizer.Add(hptxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        descsizer.Add(helpsizer,1,wx.ALL|wx.ALIGN_RIGHT,0)
        infosizer.Add(descsizer,0,wx.ALL|wx.EXPAND,2)
        #para panel
        parapnl=self.parapnl=scrd.ScrolledPanel(self,-1, size=self.gpardic['parasz'], style=wx.SIMPLE_BORDER,name='parapnl')
        #parapnl.SetBackgroundColour(wx.NullColour)
        #parapnl.SetAutoLayout(1)
        parapnl.SetupScrolling()
        parasizer=wx.BoxSizer(wx.VERTICAL)
        parapnl.SetSizer(parasizer)
        paratab,paraerr=parsextab(cuixtabs,ckeydic['cuipars'])
        if paraerr:
            msgdlg('Configuration error in cuipars: \n[%s], please check the keys and the order.'%joinlis(paraerr,', ',''),'Error',fatal=1)
        self.lisdic,self.paradic=parsepar(paratab)
        self.pcdic={'position':'Position parameters','flag':'Flag parameters'}
        #sizer dict for parameter classes
        self.para_sizer={}
        self.sizelis=[]
        self.autoheight=0
        if self.lisdic['position']:
            self.sizelis.append('position')
        if self.lisdic['flag']:
            self.sizelis.append('flag')
        #correction for gtk3 height? maybe better to use manual resize ...
        self.gtk3_htc=2
        for ec in self.sizelis:
            self.para_sizer[ec]={}
            self.para_sizer[ec]['box']=wx.StaticBox(parapnl, -1, self.pcdic[ec])
            self.para_sizer[ec]['sizer']=wx.StaticBoxSizer(self.para_sizer[ec]['box'], wx.VERTICAL)
            self.paradic[ec]['gbs']=wx.GridBagSizer(2,2)
            self.auto_ctrls(ec)
            self.para_sizer[ec]['sizer'].Add(self.paradic[ec]['gbs'], 0, wx.ALL|wx.EXPAND,0)
            parasizer.Add(self.para_sizer[ec]['sizer'],0,wx.ALL|wx.EXPAND,2)
            parasizer.Add((0,5))
            #self.autoheight+=self.para_sizer[ec]['sizer'].GetMinSize()[1]
            self.autoheight+=parasizer.GetMinSize()[1]
        
        self.atqbox=wx.StaticBox(parapnl, -1,'ATQ commands')
        self.atqboxsz=wx.StaticBoxSizer(self.atqbox,wx.VERTICAL)
        atqsizer=wx.GridBagSizer(5,5)
        atqsizer.Add(wx.StaticText(parapnl, -1, 'ATQ CMD file:'),(0,0),flag=wx.ALL|wx.EXPAND,border=0)
        self.atqctrl=wx.TextCtrl(parapnl,size=(270,-1))
        atqsizer.Add(self.atqctrl,(0,1),flag=wx.ALL|wx.LEFT|wx.RIGHT,border=0)
        loadbtn=wx.Button(parapnl,label='Load',style=wx.BU_EXACTFIT)
        loadbtn.SetToolTip('Load prepared ATQ CMD file')
        loadbtn.Bind(wx.EVT_BUTTON,self.loadatq)
        savebtn=wx.Button(parapnl,label='Save',style=wx.BU_EXACTFIT)
        savebtn.SetToolTip('Save ATQ CMDs')
        savebtn.Bind(wx.EVT_BUTTON,self.saveatq)
        clearbtn=wx.Button(parapnl,label='Clear',style=wx.BU_EXACTFIT)
        clearbtn.SetToolTip('Clear ATQ CMDs')
        clearbtn.Bind(wx.EVT_BUTTON,self.clearatq)
        atqsizer.Add(loadbtn,(0,2),flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=0)
        atqsizer.Add(savebtn,(0,3),flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=0)
        atqsizer.Add(clearbtn,(0,4),flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=0)
        self.atqlisbox=wx.adv.EditableListBox(self.parapnl,-1, "- ATQ CMDs -",size=(270,120))
        atqsizer.Add(self.atqlisbox,(1,1),(1,2),flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=0)
        self.atqboxsz.Add(atqsizer,0,wx.ALL|wx.CENTER,0)
        parasizer.Add(self.atqboxsz,0,wx.ALL|wx.EXPAND,2)
        if self.gpardic['atqctrl'].title()=='False':
            parasizer.Hide(self.atqboxsz)
        if self.autoheight<self.gpardic['parasz'][1]:
            self.parapnl.SetSizeHints(-1,self.autoheight)
        ctrlpnl=wx.Panel(self)
        ctrlsizer=wx.BoxSizer(wx.VERTICAL)
        ctrlpnl.SetSizer(ctrlsizer)
        cmdtit=wx.StaticText(ctrlpnl, -1, '>>> Command line text: ', size=(self.gpardic['cmdsz'][0],-1))
        #cmdtit.SetFont(boldft)
        #cmdtit.SetBackgroundColour('black')
        #cmdtit.SetForegroundColour('green')
        self.cmdtxt=wx.TextCtrl(ctrlpnl,-1,size=self.gpardic['cmdsz'],style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.cmdtxt.SetBackgroundColour('#1E2933')
        #self.cmdtxt.SetBackgroundColour('#1C3B56')
        self.cmdtxt.SetForegroundColour('#00FF40')
        #self.cmdtxt.SetForegroundColour('#FFFB7C')
        #self.cmdtxt.SetFocus()
        expsizer=wx.BoxSizer(wx.HORIZONTAL)
        copybtn=wx.Button(ctrlpnl,label='Copy',style=wx.BU_EXACTFIT)
        copybtn.SetToolTip('Copy to clipboard')
        copybtn.Bind(wx.EVT_BUTTON,self.copycmd)
        self.exptyp=wx.Choice(ctrlpnl, -1, choices =['Overwrite','Add'],style=wx.BU_EXACTFIT)
        self.exptyp.SetToolTip('Write mode: overwrite or add?')
        self.exptyp.Select(1)
        expbtn=wx.Button(ctrlpnl,label='Export',style=wx.BU_EXACTFIT)
        expbtn.SetToolTip('Export CMD to file')
        expbtn.Bind(wx.EVT_BUTTON,self.expfile)
        expsizer.Add(copybtn,0,flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        expsizer.Add(wx.StaticLine(ctrlpnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,5)
        expsizer.Add(wx.StaticText(ctrlpnl, -1, 'Mode:'),0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        expsizer.Add(self.exptyp,0,flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        expsizer.Add(expbtn,0,flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        self.advsizer=wx.BoxSizer(wx.VERTICAL)
        self.advsizer.Add(cmdtit,0,wx.ALL|wx.CENTER,0)
        self.advsizer.Add(self.cmdtxt,0,wx.ALL|wx.CENTER,0)
        self.advsizer.Add(expsizer,0,wx.ALL|wx.CENTER,0)
        self.advsizer.Add(wx.StaticLine(ctrlpnl,-1),0,wx.ALL|wx.EXPAND,2)
        btnsizer=wx.BoxSizer(wx.HORIZONTAL)
        rstbtn=wx.Button(ctrlpnl,label='Reset',style=wx.BU_EXACTFIT)
        rstbtn.SetToolTip('Reset CMD arguments')
        rstbtn.Bind(wx.EVT_BUTTON,self.rstargs)
        self.ordtyp=wx.Choice(ctrlpnl, -1, choices =['Fs. Ps.','Ps. Fs.'],style=wx.BU_EXACTFIT)
        self.ordtyp.SetToolTip('Assemble mode: positional or flag arguments first?')
        self.ordtyp.Select(1)
        asb_btn=wx.Button(ctrlpnl,label='Assemble',style=wx.BU_EXACTFIT)
        asb_btn.SetToolTip('Check and assemble commands')
        asb_btn.Bind(wx.EVT_BUTTON,self.asbargs)
        self.runtyp=wx.Choice(ctrlpnl, -1, choices =['Real-time','Background','Unattended'],style=wx.BU_EXACTFIT)
        self.runtyp.SetToolTip('Communication mode: real-time, background or unattended?')
        self.runtyp.Select(0)
        runbtn=wx.Button(ctrlpnl,label='Run',style=wx.BU_EXACTFIT)
        runbtn.SetToolTip('Run CUI APP with the current arguments')
        runbtn.Bind(wx.EVT_BUTTON,self.runcmd)
        btnsizer.Add(rstbtn,0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        btnsizer.Add(wx.StaticLine(ctrlpnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,5)
        btnsizer.Add(wx.StaticText(ctrlpnl, -1, 'Order:'),0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        btnsizer.Add(self.ordtyp,0,flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        btnsizer.Add(asb_btn,0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        btnsizer.Add(wx.StaticLine(ctrlpnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,5)
        btnsizer.Add(self.runtyp,0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        btnsizer.Add(runbtn,0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=5)
        ctrlsizer.Add(self.advsizer,0,wx.ALL|wx.CENTER,0)
        ctrlsizer.Add(btnsizer,0,wx.ALL|wx.CENTER,0)
        if 'gtk3' in wx.PlatformInfo:
            for ec in range(self.gtk3_htc):
                ctrlsizer.Add(wx.StaticText(ctrlpnl, -1, " "),0, wx.ALIGN_CENTER)
        if self.gpardic['cmdctrl'].title()=='False':
            ctrlsizer.Hide(self.advsizer)
        self.mainsizer.Add(infopnl,0,wx.ALL|wx.EXPAND,0)
        self.mainsizer.Add(parapnl,0,wx.ALL|wx.EXPAND,5)
        self.mainsizer.Add(ctrlpnl,0,wx.ALL|wx.EXPAND,0)
        self.SetSizer(self.mainsizer)
        self.Fit()
        self.Center()

        self.SetTransparent(self.amount)
        #fade in / out effect
        if  self.gpardic['fadeio']=='True':
            self.tincrs = 10
            self.stimer = wx.Timer(self,id=1)
            self.stimer.Start(50)
            self.Bind(wx.EVT_TIMER, self.fadein,id=1)
            self.ctimer = wx.Timer(self,id=2)
            self.Bind(wx.EVT_TIMER, self.fadeout,id=2)
            #rewrite close event
            self.Bind(wx.EVT_CLOSE,self.OnClose)

        #load splash
        if self.splashpath:
            splash=ImgSplash(None,self.splashpath,size=self.gpardic['spmaxsz'])
            wx.CallLater(self.gpardic['sptime']*1000, self.Show)
        else:
            self.Show()

    def OnClose(self, event):
        if (not self.ctimer.IsRunning()) and (not self.stimer.IsRunning()):
            self.ctimer.Start(50)

    def fadein(self, evt):
        self.amount += self.tincrs
        if self.amount >= self.transprc:
            self.amount = self.transprc
            self.stimer.Stop()
        self.SetTransparent(self.amount)

    def fadeout(self, evt):
        self.amount -= self.tincrs
        if self.amount <= 0:
            self.ctimer.Stop()
            #to avoid blink?
            self.Hide()
            self.Destroy
            wx.Exit()
            #sys.exit()
        self.SetTransparent(self.amount)

    def logoplayer(self,event):
        if self.cuilogo.IsPlaying():
            self.cuilogo.Stop()
        else:
            self.cuilogo.Play()

    def emptyfunc(self, event):
        pass

    def dspinfo(self,event,infotab):
        win = AppInfo(self,infotab)
        win.Show(True)

    def loc_brs(self,event,fipath):
        if os.path.exists(fipath):
            webbrowser.open(fipath)
        else:
            msgdlg('Local file [%s] is not exist!'%fipath,msgtit='Error')

    def web_brs(self,event,weblink):
        webbrowser.open(weblink)

    def auto_ctrls(self,pclass):
        cn=1
        if pclass=='flag':
            flaglis=[]
        for ep in self.lisdic[pclass]:
            #sorted number
            self.paradic[pclass][ep]['sort']=cn
            self.paradic[pclass][ep]['reftit']=joinlis(['['+pclass.title()+']- [',cn,'. ',self.paradic[pclass][ep]['title'],']:\n'],'','')
            #create title column
            self.paradic[pclass][ep]['ctrls']['title']=wx.StaticText(self.parapnl,-1,joinlis([cn,'. ',self.paradic[pclass][ep]['title'],': '],'',''))
            self.paradic[pclass][ep]['ctrls']['title'].Wrap(self.gpardic['titwrap'])
            self.paradic[pclass]['gbs'].Add(self.paradic[pclass][ep]['ctrls']['title'],(cn-1,0),flag=wx.ALIGN_LEFT | wx.ALL,border=2)
            #create parameter sizer
            self.paradic[pclass][ep]['ctrls']['sizer']=wx.BoxSizer(wx.HORIZONTAL)
            tmptyp=self.paradic[pclass][ep]['type']
            #string
            if tmptyp=='string':
                if self.paradic[pclass][ep]['style']=='single':
                    self.paradic[pclass][ep]['ctrls']['string']=wx.TextCtrl(self.parapnl,-1,value=self.paradic[pclass][ep]['default'],size=(270, -1))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['string'],flag=wx.ALL|wx.LEFT,border=0)
                elif self.paradic[pclass][ep]['style']=='multiple':
                    self.paradic[pclass][ep]['ctrls']['string']=wx.adv.EditableListBox(self.parapnl,-1, "- Arguments -",size=(270,120))
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['string'].SetStrings(re.split('\|',self.paradic[pclass][ep]['default']))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['string'],flag=wx.ALL|wx.LEFT,border=0)
                elif self.paradic[pclass][ep]['style']=='password':
                    self.paradic[pclass][ep]['ctrls']['string']=wx.TextCtrl(self.parapnl,value=self.paradic[pclass][ep]['default'],size=(270, -1),style=wx.TE_PASSWORD)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['string'],flag=wx.ALL|wx.LEFT,border=0)
            #int
            elif tmptyp=='int':
                self.gtk3_htc+=1
                self.paradic[pclass][ep]['ctrls']['minus']=wx.Button(self.parapnl,-1,'-',size=(30,30))
                self.paradic[pclass][ep]['ctrls']['int']=wx.TextCtrl(self.parapnl,value=self.paradic[pclass][ep]['default'],size=(90,30))
                self.paradic[pclass][ep]['ctrls']['plus']=wx.Button(self.parapnl,-1,'+',size=(30,30))
                self.paradic[pclass][ep]['ctrls']['minus'].Bind(wx.EVT_BUTTON, partial( self.intminus, paracls=pclass,paraid=ep))
                self.paradic[pclass][ep]['ctrls']['plus'].Bind(wx.EVT_BUTTON, partial( self.intplus, paracls=pclass,paraid=ep))
                #Gtk3 not well supported?
                self.paradic[pclass][ep]['ctrls']['increment']=wx.SpinCtrl(self.parapnl, -1,"1",min=1,size=(-1,30), style=wx.SP_ARROW_KEYS)
                self.paradic[pclass][ep]['rgtub']=()
                if self.paradic[pclass][ep]['limit']:
                    try:
                        self.paradic[pclass][ep]['rgtub']=parserg(self.paradic[pclass][ep]['limit'])[1]
                    except Exception as em:
                        msgdlg(self.paradic[pclass][ep]['reftit']+str(em),'Error')
                        return
                    self.paradic[pclass][ep]['ctrls']['int'].SetToolTip('Range: %s'%(self.paradic[pclass][ep]['limit']))
                self.paradic[pclass][ep]['ctrls']['sizer'].AddMany([
                    (self.paradic[pclass][ep]['ctrls']['minus'],0,wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.LEFT,0),
                    (self.paradic[pclass][ep]['ctrls']['int'],0,wx.ALL|wx.LEFT,0),
                    (self.paradic[pclass][ep]['ctrls']['plus'],0,wx.ALL|wx.LEFT,0),
                    (wx.StaticLine(self.parapnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,5),
                    (wx.StaticText(self.parapnl,-1,'Increment: '),0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,0),
                    (self.paradic[pclass][ep]['ctrls']['increment'],0,wx.ALL|wx.EXPAND,0),
                    ])
            #float
            elif tmptyp=='float':
                self.gtk3_htc+=1
                self.paradic[pclass][ep]['ctrls']['minus']=wx.Button(self.parapnl,-1,'-',size=(30,30))
                self.paradic[pclass][ep]['ctrls']['float']=wx.TextCtrl(self.parapnl,value=self.paradic[pclass][ep]['default'],size=(100,30))
                self.paradic[pclass][ep]['ctrls']['plus']=wx.Button(self.parapnl,-1,'+',size=(30,30))
                self.paradic[pclass][ep]['ctrls']['minus'].Bind(wx.EVT_BUTTON, partial( self.floatminus, paracls=pclass,paraid=ep))
                self.paradic[pclass][ep]['ctrls']['plus'].Bind(wx.EVT_BUTTON, partial( self.floatplus, paracls=pclass,paraid=ep))
                self.paradic[pclass][ep]['ctrls']['increment']=wx.SpinCtrlDouble(self.parapnl, -1,'0.01',inc=0.001,min=0,size=(-1,30), style=wx.SP_ARROW_KEYS)
                #use FS to support wx 2.8
                #self.paradic[pclass][ep]['ctrls']['increment']=FS.FloatSpin(self.parapnl, -1,value=0.01,increment=0.01, agwStyle=FS.FS_RIGHT)
                self.paradic[pclass][ep]['rgtub']=()
                if self.paradic[pclass][ep]['limit']:
                    try:
                        self.paradic[pclass][ep]['rgtub']=parserg(self.paradic[pclass][ep]['limit'])[1]
                    except Exception as em:
                        msgdlg(self.paradic[pclass][ep]['reftit']+str(em),'Error')
                        return
                    self.paradic[pclass][ep]['ctrls']['float'].SetToolTip('Range: %s'%(self.paradic[pclass][ep]['limit']))
                self.paradic[pclass][ep]['ctrls']['sizer'].AddMany([
                    (self.paradic[pclass][ep]['ctrls']['minus'],0,wx.ALL|wx.LEFT,0),
                    (self.paradic[pclass][ep]['ctrls']['float'],0,wx.ALL|wx.LEFT,0),
                    (self.paradic[pclass][ep]['ctrls']['plus'],0,wx.ALL|wx.LEFT,0),
                    (wx.StaticLine(self.parapnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,5),
                    (wx.StaticText(self.parapnl,-1,'Increment: '),0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,0),
                    (self.paradic[pclass][ep]['ctrls']['increment'],0,wx.ALL|wx.EXPAND,0),
                    ])
            #select
            elif tmptyp=='select':
                if self.paradic[pclass][ep]['style']=='single':
                    tmplis=re.split('\|',self.paradic[pclass][ep]['limit'])
                    self.paradic[pclass][ep]['ctrls']['select']=wx.Choice(self.parapnl, -1, choices = ['- Select -']+tmplis)
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['select'].SetStringSelection(self.paradic[pclass][ep]['default'])
                    else:
                        self.paradic[pclass][ep]['ctrls']['select'].SetSelection(0)
                elif self.paradic[pclass][ep]['style']=='multiple':
                    tmplis=re.split('\|',self.paradic[pclass][ep]['limit'])
                    self.paradic[pclass][ep]['ctrls']['select']=wx.CheckListBox(self.parapnl, -1,size=(-1,120), choices = tmplis)
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['select'].SetCheckedStrings(re.split('\|',self.paradic[pclass][ep]['default']))
                self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['select'],flag=wx.ALL|wx.LEFT,border=0)
            #check
            elif tmptyp=='check':
                self.paradic[pclass][ep]['ctrls']['check']=wx.CheckBox(self.parapnl, -1, '')
                if self.paradic[pclass][ep]['default'].title()=='True':
                    self.paradic[pclass][ep]['ctrls']['check'].SetValue(True)
                self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['check'],flag=wx.ALL|wx.LEFT,border=0)
            #file
            elif tmptyp=='file':
                if self.paradic[pclass][ep]['style']=='single':
                    self.paradic[pclass][ep]['ctrls']['file']=wx.TextCtrl(self.parapnl,value=checkpath(self.paradic[pclass][ep]['default']),size=(270,-1))
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,label='Browse',style=wx.BU_EXACTFIT)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.brsfile, paracls=pclass,paraid=ep))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['file'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=0)
                elif self.paradic[pclass][ep]['style']=='multiple':
                    self.paradic[pclass][ep]['ctrls']['file']=wx.adv.EditableListBox(self.parapnl,-1, "- Files -",size=(270,120))
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['file'].SetStrings(checkpath(re.split('\|',self.paradic[pclass][ep]['default'])))
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,label='Browse',style=wx.BU_EXACTFIT)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.brsfiles, paracls=pclass,paraid=ep))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['file'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=0)
            #folder
            elif tmptyp=='folder':
                if self.paradic[pclass][ep]['style']=='single':
                    self.paradic[pclass][ep]['ctrls']['folder']=wx.TextCtrl(self.parapnl,value=self.paradic[pclass][ep]['default'],size=(270,-1))
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,label='Browse',style=wx.BU_EXACTFIT)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['folder'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.brsfolder, paracls=pclass,paraid=ep))
                elif self.paradic[pclass][ep]['style']=='multiple':
                    self.paradic[pclass][ep]['ctrls']['folder']=wx.adv.EditableListBox(self.parapnl,-1, "- Folders -",size=(270,120))
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['folder'].SetStrings(checkpath(re.split('\|',self.paradic[pclass][ep]['default'])))
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,label='Browse',style=wx.BU_EXACTFIT)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['folder'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.brsfolders, paracls=pclass,paraid=ep))
            #range
            elif tmptyp=='range':
                self.paradic[pclass][ep]['ctrls']['lowcd']=wx.Choice(self.parapnl, -1, choices = ['','[','('],size=(50,-1))
                self.paradic[pclass][ep]['ctrls']['lowlm']=wx.TextCtrl(self.parapnl,size=(90,-1))
                self.paradic[pclass][ep]['ctrls']['uplm']=wx.TextCtrl(self.parapnl,size=(90,-1))
                self.paradic[pclass][ep]['ctrls']['upcd']=wx.Choice(self.parapnl, -1, choices = ['',']',')'],size=(50,-1))
                self.paradic[pclass][ep]['ctrls']['lowcd'].SetSelection(0)
                self.paradic[pclass][ep]['ctrls']['upcd'].SetSelection(0)
                if self.paradic[pclass][ep]['default']:
                    try:
                        lowcd,lowlm,uplm,upcd=parserg(self.paradic[pclass][ep]['default'])[0]
                    except Exception as em:
                        msgdlg(self.paradic[pclass][ep]['reftit']+str(em),'Error')
                        return
                    self.paradic[pclass][ep]['ctrls']['lowcd'].SetStringSelection(lowcd)
                    self.paradic[pclass][ep]['ctrls']['lowlm'].SetValue(lowlm)
                    self.paradic[pclass][ep]['ctrls']['uplm'].SetValue(uplm)
                    self.paradic[pclass][ep]['ctrls']['upcd'].SetStringSelection(upcd)
                self.paradic[pclass][ep]['ctrls']['sizer'].AddMany([
                (self.paradic[pclass][ep]['ctrls']['lowcd'],0,wx.ALL|wx.LEFT,0),
                ((5,0),),
                (self.paradic[pclass][ep]['ctrls']['lowlm'],0,wx.ALL|wx.LEFT,0),
                (wx.StaticText(self.parapnl,-1,','),0,wx.ALL|wx.LEFT,2),
                (self.paradic[pclass][ep]['ctrls']['uplm'],0,wx.ALL|wx.LEFT,0),
                ((5,0),),
                (self.paradic[pclass][ep]['ctrls']['upcd'],0,wx.ALL|wx.LEFT,0),
                ])
            #colour
            elif tmptyp=='colour':
                if self.paradic[pclass][ep]['style']=='single':
                    self.paradic[pclass][ep]['ctrls']['colour']=wx.TextCtrl(self.parapnl,-1,value=self.paradic[pclass][ep]['default'],size=(90,-1),style=wx.TE_READONLY)
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,-1,'Choose',style=wx.BU_EXACTFIT)
                    if self.paradic[pclass][ep]['default']:
                        tmphc=self.paradic[pclass][ep]['default']
                        self.paradic[pclass][ep]['ctrls']['colour'].SetBackgroundColour(tmphc)
                        try:
                            tmpcr,tmpcg,tmpcb=htm2rgb(tmphc)
                        except Exception as em:
                            msgdlg(self.paradic[pclass][ep]['reftit']+str(em),'Error')
                            return
                        tmpfc='black'
                        tmpcv=rgb2gray((tmpcr,tmpcg,tmpcb))
                        if tmpcv<150:
                            tmpfc='white'
                        self.paradic[pclass][ep]['ctrls']['colour'].SetForegroundColour(tmpfc)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.chscolour, paracls=pclass,paraid=ep))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['colour'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=0)
                elif self.paradic[pclass][ep]['style']=='multiple':
                    self.paradic[pclass][ep]['ctrls']['colour']=wx.adv.EditableListBox(self.parapnl,-1, "- Colours -",size=(270,120))
                    self.paradic[pclass][ep]['ctrls']['colour'].ListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, partial(self.democolour, paracls=pclass,paraid=ep))
                    self.paradic[pclass][ep]['ctrls']['demo']=wx.Button(self.parapnl,-1,'',size=(25,25))
                    self.paradic[pclass][ep]['ctrls']['button']=wx.Button(self.parapnl,-1,'Add',style=wx.BU_EXACTFIT)
                    if self.paradic[pclass][ep]['default']:
                        self.paradic[pclass][ep]['ctrls']['colour'].SetStrings(re.split('\|',self.paradic[pclass][ep]['default']))
                        tmphc=re.split('\|',self.paradic[pclass][ep]['default'])[0]
                        self.paradic[pclass][ep]['ctrls']['demo'].SetBackgroundColour(tmphc)
                    self.paradic[pclass][ep]['ctrls']['button'].Bind(wx.EVT_BUTTON, partial( self.chscolours, paracls=pclass,paraid=ep))
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['colour'],flag=wx.ALL|wx.LEFT,border=0)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['demo'],flag=wx.ALL|wx.LEFT,border=2)
                    self.paradic[pclass][ep]['ctrls']['sizer'].Add(self.paradic[pclass][ep]['ctrls']['button'],flag=wx.ALL|wx.LEFT,border=2)
            if pclass=='flag':
                if not self.paradic[pclass][ep]['flag']:
                    msgdlg('%s Flag label can not be empty!\n Please check parameter file.'%(self.paradic[pclass][ep]['reftit']),'Error',fatal=1)
                if self.paradic[pclass][ep]['flag'] not in flaglis:
                    flaglis.append(self.paradic[pclass][ep]['flag'])
                else:
                    msgdlg('%s Flag label [%s] is not unique!\n Please check parameter file.'%(self.paradic[pclass][ep]['reftit'],self.paradic[pclass][ep]['flag']),'Error',fatal=1)
            #assemble parameter sizer
            self.paradic[pclass]['gbs'].Add(self.paradic[pclass][ep]['ctrls']['sizer'],(cn-1,1),flag=wx.ALL|wx.LEFT,border=2)
            #requirement
            if pclass=='position' or (self.paradic[pclass][ep]['require'].lower()=='yes'):
                self.paradic[pclass][ep]['ctrls']['require']=wx.StaticBitmap(self.parapnl,-1,self.gpicons['required'])
                self.paradic[pclass][ep]['ctrls']['require'].SetToolTip('Required parameter!')
            else:
                self.paradic[pclass][ep]['ctrls']['require']=wx.StaticBitmap(self.parapnl,-1,self.gpicons['not_required'])
                self.paradic[pclass][ep]['ctrls']['require'].SetToolTip('Optional parameter!')
            self.paradic[pclass]['gbs'].Add(self.paradic[pclass][ep]['ctrls']['require'],(cn-1,2),flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP,border=2)
            #exclusive
            if self.paradic[pclass][ep]['exclude'].lower()=='yes':
                self.paradic[pclass][ep]['ctrls']['exclude']=wx.StaticBitmap(self.parapnl,-1,self.gpicons['exclusive'])
                self.paradic[pclass][ep]['ctrls']['exclude'].SetToolTip('Exclusive parameter!')
            else:
                self.paradic[pclass][ep]['ctrls']['exclude']=wx.StaticBitmap(self.parapnl,-1,self.gpicons['not_exclusive'])
                self.paradic[pclass][ep]['ctrls']['exclude'].SetToolTip('Non-exclusive parameter!')
            self.paradic[pclass]['gbs'].Add(self.paradic[pclass][ep]['ctrls']['exclude'],(cn-1,3),flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP,border=2)
            #help
            self.paradic[pclass][ep]['ctrls']['help']=wx.StaticBitmap(self.parapnl,-1,wx.ArtProvider.GetBitmap(wx.ART_HELP,size=(16,16)))
            self.paradic[pclass]['gbs'].Add(self.paradic[pclass][ep]['ctrls']['help'],(cn-1,4),flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP,border=2)
            self.paradic[pclass][ep]['ctrls']['help'].SetCursor(wx.Cursor(wx.CURSOR_HAND))
            tmpflag=self.paradic[pclass][ep]['flag']
            if not tmpflag:
                tmpflag='[positional parameter]'
            self.paradic[pclass][ep]['ctrls']['help'].Bind(wx.EVT_LEFT_UP, partial( self.showpop, hptit=self.paradic[pclass][ep]['title'],hptxt='Flag: %s\nDescription: \n'%tmpflag+self.paradic[pclass][ep]['help']))
            cn+=1
        self.paradic[pclass]['gbs'].AddGrowableCol(1)

    def intminus(self,event,paracls,paraid):
        if self.paradic[paracls][paraid]['default'] or self.paradic[paracls][paraid]['ctrls']['int'].GetValue():
            tmpval=int(self.paradic[paracls][paraid]['ctrls']['int'].GetValue())-self.paradic[paracls][paraid]['ctrls']['increment'].GetValue()
            self.paradic[paracls][paraid]['ctrls']['int'].SetValue(str(tmpval))

    def intplus(self,event,paracls,paraid):
        if self.paradic[paracls][paraid]['default'] or self.paradic[paracls][paraid]['ctrls']['int'].GetValue():
            tmpval=int(self.paradic[paracls][paraid]['ctrls']['int'].GetValue())+self.paradic[paracls][paraid]['ctrls']['increment'].GetValue()
            self.paradic[paracls][paraid]['ctrls']['int'].SetValue(str(tmpval))

    def floatminus(self,event,paracls,paraid):
        if self.paradic[paracls][paraid]['default'] or self.paradic[paracls][paraid]['ctrls']['float'].GetValue():
            tmpval=float(self.paradic[paracls][paraid]['ctrls']['float'].GetValue())-self.paradic[paracls][paraid]['ctrls']['increment'].GetValue()
            self.paradic[paracls][paraid]['ctrls']['float'].SetValue(str(tmpval))

    def floatplus(self,event,paracls,paraid):
        if self.paradic[paracls][paraid]['default'] or self.paradic[paracls][paraid]['ctrls']['float'].GetValue():
            tmpval=float(self.paradic[paracls][paraid]['ctrls']['float'].GetValue())+self.paradic[paracls][paraid]['ctrls']['increment'].GetValue()
            self.paradic[paracls][paraid]['ctrls']['float'].SetValue(str(tmpval))

    def brsfile(self,event,paracls,paraid):
        dlg=wx.FileDialog(
            self,message="Choose or create a file:",
            defaultDir=os.getcwd(), 
            wildcard=self.paradic[paracls][paraid]['limit'],
            style=wx.FD_SAVE
            )
        if dlg.ShowModal()==wx.ID_OK:
            apath=dlg.GetPath()
            self.paradic[paracls][paraid]['ctrls']['file'].SetValue(apath)
        dlg.Destroy()

    def brsfiles(self,event,paracls,paraid):
        dlg=wx.FileDialog(
            self,message="Choose or create files:",
            defaultDir=os.getcwd(), 
            wildcard=self.paradic[paracls][paraid]['limit'],
            style=wx.FD_OPEN|wx.FD_MULTIPLE
            )
        if dlg.ShowModal()==wx.ID_OK:
            apath=dlg.GetPath()
            pathlis=self.paradic[paracls][paraid]['ctrls']['file'].GetStrings()
            pathlis.append(apath)
            self.paradic[paracls][paraid]['ctrls']['file'].SetStrings(pathlis)
        dlg.Destroy()

    def brsfolder(self,event,paracls,paraid):
        dlg=wx.DirDialog(
            self,message="Choose or create a folder:",
            style=wx.DD_DEFAULT_STYLE
            )
        if dlg.ShowModal()==wx.ID_OK:
            apath=dlg.GetPath()
            self.paradic[paracls][paraid]['ctrls']['folder'].SetValue(apath)
        dlg.Destroy()

    def brsfolders(self,event,paracls,paraid):
        dlg=wx.DirDialog(
            self,message="Choose or create folders:",
            style=wx.DD_DEFAULT_STYLE
            )
        if dlg.ShowModal()==wx.ID_OK:
            apath=dlg.GetPath()
            pathlis=self.paradic[paracls][paraid]['ctrls']['folder'].GetStrings()
            pathlis.append(apath)
            self.paradic[paracls][paraid]['ctrls']['folder'].SetStrings(pathlis)
        dlg.Destroy()

    def chscolour(self,event,paracls,paraid):
        dftcolour='#808080'
        if self.paradic[paracls][paraid]['ctrls']['colour'].GetValue():
            dftcolour=self.paradic[paracls][paraid]['ctrls']['colour'].GetValue()
        dftcdata=wx.ColourData()
        tmpr,tmpg,tmpb=htm2rgb(dftcolour)
        dftcdata.SetColour(wx.Colour(tmpr,tmpg,tmpb))
        dlg=wx.ColourDialog(self,dftcdata)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal()==wx.ID_OK:
            tmpcolour=dlg.GetColourData().GetColour()
            tmpcstr=tmpcolour.GetAsString(wx.C2S_HTML_SYNTAX)
            print(tmpcstr)
            #tmphc,tmphs,tmphv,tmpha=dlg.GetHSVAColour()
            tmpfc='black'
            if rgb2gray(tmpcolour.Get()[:3])<150:
                tmpfc='white'
            self.paradic[paracls][paraid]['ctrls']['colour'].SetValue(tmpcstr)
            self.paradic[paracls][paraid]['ctrls']['colour'].SetBackgroundColour(tmpcstr)
            self.paradic[paracls][paraid]['ctrls']['colour'].SetForegroundColour(tmpfc)
        dlg.Destroy

    def chscolours(self,event,paracls,paraid):
        dftcolour='#808080'
        if self.paradic[paracls][paraid]['ctrls']['colour'].GetStrings():
            dftcolour=self.paradic[paracls][paraid]['ctrls']['colour'].GetStrings()[-1]
        dftcdata=wx.ColourData()
        tmpr,tmpg,tmpb=htm2rgb(dftcolour)
        dftcdata.SetColour(wx.Colour(tmpr,tmpg,tmpb))
        dlg=wx.ColourDialog(self,dftcdata)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal()==wx.ID_OK:
            tmpcolour=dlg.GetColourData().GetColour()
            tmpcstr=tmpcolour.GetAsString(wx.C2S_HTML_SYNTAX)
            self.paradic[paracls][paraid]['ctrls']['demo'].SetBackgroundColour(tmpcstr)
            clis=self.paradic[paracls][paraid]['ctrls']['colour'].GetStrings()
            clis.append(tmpcstr)
            self.paradic[paracls][paraid]['ctrls']['colour'].SetStrings(clis)
            self.paradic[paracls][paraid]['ctrls']['colour'].ListCtrl.Select(len(clis)-1)
        dlg.Destroy

    def democolour(self,event,paracls,paraid):
        self.paradic[paracls][paraid]['ctrls']['demo'].SetBackgroundColour(event.Text)

    def showpop(self,evt,hptit,hptxt):
        win = HelpPopup(self.GetTopLevelParent(), wx.SIMPLE_BORDER,self.gpardic['hpwrap'],hptit,hptxt)
        evtobj = evt.GetEventObject()
        pos = evtobj.ClientToScreen( (0,0) )
        sz =  evtobj.GetSize()
        win.Position(pos, (sz[0]+5,0))
        win.Show(True)

    def loadatq(self,event):
        dlg=wx.FileDialog(
            self,message="Choose the pre-defined ATQ CMD file:",
            wildcard="Tab separated data (*.tsd)|*.tsd|All files (*.*)|*.*",
            style=wx.FD_OPEN
            )
        if dlg.ShowModal()==wx.ID_OK:
            apath=dlg.GetPath()
            self.atqctrl.SetValue(apath)
            self.atqlis=file2lis(apath)
            self.atqlisbox.SetStrings(self.atqlis)
            msgdlg('ATQ CMD loaded!')
        dlg.Destroy()

    def clearatq(self,event):
        self.atqctrl.SetValue('')
        self.atqlis=[]
        self.atqlisbox.SetStrings(self.atqlis)
        msgdlg('ATQ CMD cleaned!')

    def saveatq(self,event):
        self.atqlis=self.atqlisbox.GetStrings()
        if not self.atqlis:
            msgdlg('ATQ CMD is empty!','Error')
            return
        expdlg=wx.FileDialog(
            self,message="Choose or create a file",
            defaultFile="",
            wildcard="Tab separated data (*.tsd)|*.tsd|All files (*.*)|*.*",
            style=wx.FD_SAVE
            )
        if expdlg.ShowModal()==wx.ID_OK:
            paths=expdlg.GetPath()
            if os.path.exists(paths):
                notedlg=wx.MessageDialog(None,'File already exist, are you sure to overwrite?','Note',wx.YES_NO | wx.ICON_WARNING)
                if notedlg.ShowModal()!=wx.ID_YES:
                    wx.MessageBox("Save action aborted!", "Note")
                    notedlg.Destroy()
                    return
                notedlg.Destroy()
            topf=open(paths,'w')
            topf.write(joinlis(self.atqlis,'\n','\n'))
            topf.close()
            notedlg=wx.MessageDialog(None,'ATQ CMD saved to file!','Note',wx.OK)
            notedlg.ShowModal()
            notedlg.Destroy()
        else:
            pass
        expdlg.Destroy()

    def copycmd(self,event):
        cmdobj=wx.TextDataObject()
        tmptxt=self.cmdtxt.GetValue()
        if tmptxt:
            cmdobj.SetText(joinlis(self.cmdlis,' ',''))
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(cmdobj)
                wx.TheClipboard.Close()
                errdlg=wx.MessageDialog(None,'CMD copied into clipboard!','Note',wx.OK)
                errdlg.ShowModal()
                errdlg.Destroy()
            else:
                errdlg=wx.MessageDialog(None,'Open the clipboard failed!','Error',wx.OK|wx.ICON_ERROR)
                errdlg.ShowModal()
                errdlg.Destroy()
        else:
            msgdlg(u'CMD text is not assembled!')

    def expfile(self,event):
        if not self.cmdtxt.GetValue():
            errdlg=wx.MessageDialog(None,'Empty CMD text!','Error',wx.OK|wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
            return 
        expdlg=wx.FileDialog(
            self,message="Choose or create a file",
            defaultFile="",
            wildcard="Tab separated data (*.tsd)|*.tsd|All files (*.*)|*.*",
            style=wx.FD_SAVE
            )
        expmod=self.stypdic[self.exptyp.GetCurrentSelection()]
        if expdlg.ShowModal()==wx.ID_OK:
            paths=expdlg.GetPath()
            if os.path.exists(paths):
                notedlg=wx.MessageDialog(None,'File already exists, are you sure?','Note',wx.YES_NO | wx.ICON_WARNING)
                if notedlg.ShowModal()!=wx.ID_YES:
                    wx.MessageBox("Export action aborted!", "Note")
                    notedlg.Destroy()
                    return
                notedlg.Destroy()
            topf=open(paths,expmod)
            topf.write(joinlis(self.cmdlis,' ','\n'))
            topf.close()
            notedlg=wx.MessageDialog(None,'CMD exported to file!','Note',wx.OK)
            notedlg.ShowModal()
            notedlg.Destroy()
        else:
            pass
        expdlg.Destroy()
        if self.atqlisbox.GetStrings():
            msgdlg('ATQ CMD detected, please manually save the ATQ CMD if necessary!','Error')

    def rstargs(self,event):
        for ec in self.sizelis:
            for ep in self.lisdic[ec]:
                tmptyp=self.paradic[ec][ep]['type']
                #string
                if tmptyp=='string':
                    if self.paradic[ec][ep]['style']=='single':
                        self.paradic[ec][ep]['ctrls']['string'].SetValue(self.paradic[ec][ep]['default'])
                    elif self.paradic[ec][ep]['style']=='multiple':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['string'].SetStrings(re.split('\|',self.paradic[ec][ep]['default']))
                        else:
                            self.paradic[ec][ep]['ctrls']['string'].SetStrings([])
                    elif self.paradic[ec][ep]['style']=='password':
                        self.paradic[ec][ep]['ctrls']['string'].SetValue(self.paradic[ec][ep]['default'])
                #int
                elif tmptyp=='int':
                    self.paradic[ec][ep]['ctrls']['int'].SetValue(self.paradic[ec][ep]['default'])
                #float
                elif tmptyp=='float':
                    self.paradic[ec][ep]['ctrls']['float'].SetValue(self.paradic[ec][ep]['default'])
                #select
                elif tmptyp=='select':
                    if self.paradic[ec][ep]['style']=='single':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['select'].SetStringSelection(self.paradic[ec][ep]['default'])
                        else:
                            self.paradic[ec][ep]['ctrls']['select'].SetSelection(0)
                    elif self.paradic[ec][ep]['style']=='multiple':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['select'].SetCheckedStrings(re.split('\|',self.paradic[ec][ep]['default']))
                        else:
                            self.paradic[ec][ep]['ctrls']['select'].SetCheckedStrings([])
                #check
                elif tmptyp=='check':
                    if self.paradic[ec][ep]['default'].title()=='True':
                        self.paradic[ec][ep]['ctrls']['check'].SetValue(True)
                    else:
                        self.paradic[ec][ep]['ctrls']['check'].SetValue(False)
                #file
                elif tmptyp=='file':
                    if self.paradic[ec][ep]['style']=='single':
                        self.paradic[ec][ep]['ctrls']['file'].SetValue(checkpath(self.paradic[ec][ep]['default']))
                    elif self.paradic[ec][ep]['style']=='multiple':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['file'].SetStrings(checkpath(re.split('\|',self.paradic[ec][ep]['default'])))
                        else:
                            self.paradic[ec][ep]['ctrls']['file'].SetStrings([])
                #folder
                elif tmptyp=='folder':
                    if self.paradic[ec][ep]['style']=='single':
                        self.paradic[ec][ep]['ctrls']['folder'].SetValue(checkpath(self.paradic[ec][ep]['default']))
                    elif self.paradic[ec][ep]['style']=='multiple':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['folder'].SetStrings(checkpath(re.split('\|',self.paradic[ec][ep]['default'])))
                        else:
                            self.paradic[ec][ep]['ctrls']['folder'].SetStrings([])
                #range
                elif tmptyp=='range':
                    if self.paradic[ec][ep]['default']:
                        try:
                            lowcd,lowlm,uplm,upcd=parserg(self.paradic[ec][ep]['default'])[0]
                        except Exception as em:
                            msgdlg(self.paradic[ec][ep]['reftit']+str(em),'Error')
                            return
                        self.paradic[ec][ep]['ctrls']['lowcd'].SetStringSelection(lowcd)
                        self.paradic[ec][ep]['ctrls']['lowlm'].SetValue(lowlm)
                        self.paradic[ec][ep]['ctrls']['uplm'].SetValue(uplm)
                        self.paradic[ec][ep]['ctrls']['upcd'].SetStringSelection(upcd)
                    else:
                        self.paradic[ec][ep]['ctrls']['lowcd'].SetSelection(0)
                        self.paradic[ec][ep]['ctrls']['lowlm'].SetValue('')
                        self.paradic[ec][ep]['ctrls']['uplm'].SetValue('')
                        self.paradic[ec][ep]['ctrls']['upcd'].SetSelection(0)
                #colour
                elif tmptyp=='colour':
                    if self.paradic[ec][ep]['style']=='single':
                        if self.paradic[ec][ep]['default']:
                            tmphc=self.paradic[ec][ep]['default']
                            self.paradic[ec][ep]['ctrls']['colour'].SetBackgroundColour(tmphc)
                            tmpcr,tmpcg,tmpcb=htm2rgb(tmphc)
                            tmpfc='black'
                            tmpcv=rgb2gray((tmpcr,tmpcg,tmpcb))
                            if tmpcv<150:
                                tmpfc='white'
                            self.paradic[ec][ep]['ctrls']['colour'].SetForegroundColour(tmpfc)
                            self.paradic[ec][ep]['ctrls']['colour'].SetFocus()
                        else:
                            self.paradic[ec][ep]['ctrls']['colour'].SetValue(self.paradic[ec][ep]['default'])
                            self.paradic[ec][ep]['ctrls']['colour'].SetBackgroundColour(wx.NullColour)
                    elif self.paradic[ec][ep]['style']=='multiple':
                        if self.paradic[ec][ep]['default']:
                            self.paradic[ec][ep]['ctrls']['colour'].SetStrings(re.split('\|',self.paradic[ec][ep]['default']))
                            tmphc=re.split('\|',self.paradic[ec][ep]['default'])[0]
                            self.paradic[ec][ep]['ctrls']['demo'].SetBackgroundColour(tmphc)
                        else:
                            self.paradic[ec][ep]['ctrls']['colour'].SetStrings([])
                            self.paradic[ec][ep]['ctrls']['demo'].SetBackgroundColour(wx.NullColour)
        #reset ATQ CMD
        self.cmdtxt.SetValue('')
        self.atqctrl.SetValue('')
        self.atqlis=[]
        self.atqlisbox.SetStrings(self.atqlis)
        msgdlg('All set to default configurations!')

    def asbargs(self,event):
        tmpdic={'position':[],'flag':[]}
        tmpmskdic={'position':[],'flag':[]}
        tmprundic={'position':[],'flag':[]}
        tmpargdic={}
        for ec in self.sizelis:
            for ep in self.lisdic[ec]:
                tmptyp=self.paradic[ec][ep]['type']
                tmpflag=self.paradic[ec][ep]['flag']
                #string
                if tmptyp=='string':
                    if self.paradic[ec][ep]['style']=='single':
                        tmpval=checkipt(self.paradic[ec][ep]['ctrls']['string'].GetValue())
                        if tmpval:
                            tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmprundic[ec]+=[tmpflag,tmpval]
                    elif self.paradic[ec][ep]['style']=='multiple':
                        tmplis=checkipt(self.paradic[ec][ep]['ctrls']['string'].GetStrings())
                        if tmplis:
                            tmpdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmpmskdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmprundic[ec]+=[tmpflag]+tmplis
                    elif self.paradic[ec][ep]['style']=='password':
                        tmpval=checkipt(self.paradic[ec][ep]['ctrls']['string'].GetValue())
                        if tmpval:
                            tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmpmskdic[ec]+=wraparglis(tmpflag,['******'])
                            tmprundic[ec]+=[tmpflag,tmpval]
                elif tmptyp=='int':
                    tmpval=checkipt(self.paradic[ec][ep]['ctrls']['int'].GetValue())
                    if tmpval:
                        try:
                            int(tmpval)
                        except Exception as em:
                            msgdlg(self.paradic[ec][ep]['reftit']+' Data type error!\n '+str(em),'Error')
                            return
                        if self.paradic[ec][ep]['rgtub']:
                            if not rgfilter(tmpval,self.paradic[ec][ep]['rgtub']):
                                msgdlg(self.paradic[ec][ep]['reftit']+'Value out of pre-defined range!','Error')
                                return
                        tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                        tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                        tmprundic[ec]+=[tmpflag,tmpval]
                #float
                elif tmptyp=='float':
                    tmpval=checkipt(self.paradic[ec][ep]['ctrls']['float'].GetValue())
                    if tmpval:
                        try:
                            float(tmpval)
                        except Exception as em:
                            msgdlg(self.paradic[ec][ep]['reftit']+' Data type error!\n '+str(em),'Error')
                            return
                        if self.paradic[ec][ep]['rgtub']:
                            if not rgfilter(tmpval,self.paradic[ec][ep]['rgtub']):
                                msgdlg(self.paradic[ec][ep]['reftit']+'Value out of pre-defined range!','Error')
                                return
                        tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                        tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                        tmprundic[ec]+=[tmpflag,tmpval]
                #select
                elif tmptyp=='select':
                    if self.paradic[ec][ep]['style']=='single':
                        if self.paradic[ec][ep]['ctrls']['select'].GetSelection()!=0:
                            tmpval=checkipt(self.paradic[ec][ep]['ctrls']['select'].GetStringSelection())
                            if tmpval:
                                tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                                tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                                tmprundic[ec]+=[tmpflag,tmpval]
                    elif self.paradic[ec][ep]['style']=='multiple':
                        tmplis=checkipt(self.paradic[ec][ep]['ctrls']['select'].GetCheckedStrings())
                        if tmplis:
                            tmpdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmpmskdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmprundic[ec]+=[tmpflag]+tmplis
                #check
                elif tmptyp=='check':
                    tmpval='uncheck'
                    if self.paradic[ec][ep]['ctrls']['check'].IsChecked():
                        tmpdic[ec]+=wraparglis(tmpflag,[])
                        tmpmskdic[ec]+=wraparglis(tmpflag,[])
                        tmprundic[ec]+=[tmpflag]
                        #only used for requirement check
                        tmpval='check'
                #file
                elif tmptyp=='file':
                    if self.paradic[ec][ep]['style']=='single':
                        tmpval=checkipt(self.paradic[ec][ep]['ctrls']['file'].GetValue())
                        if tmpval:
                            tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmprundic[ec]+=[tmpflag,tmpval]
                    elif self.paradic[ec][ep]['style']=='multiple':
                        tmplis=checkipt(self.paradic[ec][ep]['ctrls']['file'].GetStrings())
                        if tmplis:
                            tmpdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmpmskdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmprundic[ec]+=[tmpflag]+tmplis
                #folder
                elif tmptyp=='folder':
                    if self.paradic[ec][ep]['style']=='single':
                        tmpval=checkipt(self.paradic[ec][ep]['ctrls']['folder'].GetValue())
                        if tmpval:
                            tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmprundic[ec]+=[tmpflag,tmpval]
                    elif self.paradic[ec][ep]['style']=='multiple':
                        tmplis=checkipt(self.paradic[ec][ep]['ctrls']['folder'].GetStrings())
                        if tmplis:
                            tmpdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmpmskdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmprundic[ec]+=[tmpflag]+tmplis
                #range
                elif tmptyp=='range':
                    lowcd=checkipt(self.paradic[ec][ep]['ctrls']['lowcd'].GetStringSelection())
                    lowlm=checkipt(self.paradic[ec][ep]['ctrls']['lowlm'].GetValue())
                    uplm=checkipt(self.paradic[ec][ep]['ctrls']['uplm'].GetValue())
                    upcd=checkipt(self.paradic[ec][ep]['ctrls']['upcd'].GetStringSelection())
                    if self.paradic[ec][ep]['ctrls']['lowcd'].GetSelection()!=0 and lowlm!='' and uplm!='' and self.paradic[ec][ep]['ctrls']['upcd'].GetSelection()!=0:
                        tmpdic[ec]+=wraparglis(tmpflag,[joinlis([lowcd,lowlm,',',uplm,upcd],'','')])
                        tmpmskdic[ec]+=wraparglis(tmpflag,[joinlis([lowcd,lowlm,',',uplm,upcd],'','')])
                        tmprundic[ec]+=[tmpflag,joinlis([lowcd,lowlm,',',uplm,upcd],'','')]
                        try:
                            parserg(joinlis([lowcd,lowlm,',',uplm,upcd],'',''))
                        except Exception as em:
                            msgdlg(self.paradic[ec][ep]['reftit']+str(em),'Error')
                            return
                        tmpval=joinlis([lowcd,lowlm,',',uplm,upcd],'','')
                    else:
                        tmpval=''
                        self.paradic[ec][ep]['ctrls']['lowcd'].SetSelection(0)
                        self.paradic[ec][ep]['ctrls']['upcd'].SetSelection(0)
                        self.paradic[ec][ep]['ctrls']['lowlm'].SetValue('')
                        self.paradic[ec][ep]['ctrls']['uplm'].SetValue('')
                #colour
                elif tmptyp=='colour':
                    if self.paradic[ec][ep]['style']=='single':
                        tmpval=checkipt(self.paradic[ec][ep]['ctrls']['colour'].GetValue())
                        if tmpval:
                            tmpdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmpmskdic[ec]+=wraparglis(tmpflag,[tmpval])
                            tmprundic[ec]+=[tmpflag,tmpval]
                    elif self.paradic[ec][ep]['style']=='multiple':
                        tmplis=checkipt(self.paradic[ec][ep]['ctrls']['colour'].GetStrings())
                        if tmplis:
                            tmpdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmpmskdic[ec]+=wraparglis(tmpflag,tmplis)
                            tmprundic[ec]+=[tmpflag]+tmplis
                #for requirement checking
                if self.paradic[ec][ep]['style']=='multiple':
                    tmpargdic[ep]=tmplis
                else:
                    tmpargdic[ep]=tmpval
        #check requirement and exclusive
        rqlis=[]
        exclulis=[]
        exclurlis=[]
        for ec in self.sizelis:
            for ep in self.lisdic[ec]:
                tmpnu=self.paradic[ec][ep]['sort']
                tmpreq=self.paradic[ec][ep]['require']
                tmpexclu=self.paradic[ec][ep]['exclude']
                if tmpreq.lower()=='yes' and ((not tmpargdic[ep])  or (self.paradic[ec][ep]['type']=='check' and tmpargdic[ep]!='check')):
                    rqlis.append(joinlis(['['+ec+']: ',tmpnu,'. ',self.paradic[ec][ep]['title'],'\n'],'',''))
                if tmpexclu.lower()=='yes' and (tmpargdic[ep] and not (self.paradic[ec][ep]['type']=='check' and tmpargdic[ep]=='uncheck')):
                    exclulis.append(joinlis(['['+ec+']: ',tmpnu,'. ',self.paradic[ec][ep]['title'],'\n'],'',''))
                if tmpexclu.lower()=='yes':
                    exclurlis.append(joinlis(['['+ec+']: ',tmpnu,'. ',self.paradic[ec][ep]['title'],'\n'],'',''))
        if len(rqlis)>0 and not (len(rqlis)<len(exclurlis) and set(rqlis).issubset(set(exclurlis))):
            errdlg=wx.MessageDialog(None,'These parameters are required: \n%s'%(joinlis(rqlis,'','')),'Error',wx.OK|wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
            return
        if len(exclulis)>1:
            errdlg=wx.MessageDialog(None,'These parameters are mutually exclusive: \n%s'%(joinlis(exclulis,'','')),'Error',wx.OK|wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
            return
        ordtyp=self.ordtyp.GetStringSelection()
        #self.intprt to correct the running of CMD scripts
        if ordtyp=='Ps. Fs.':
            self.cmdlis=wraparglis(self.intprt ,[self.cuipath])+tmpdic['position']+tmpdic['flag']
            self.cmdtxt.SetValue(joinlis(wraparglis(self.intprt ,[self.cuipath])+tmpmskdic['position']+tmpmskdic['flag'],' ',''))
            self.runlis=[self.intprt,self.cuipath]+tmprundic['position']+tmprundic['flag']
        else:
            self.cmdlis=wraparglis(self.intprt ,[self.cuipath])+tmpdic['flag']+tmpdic['position']
            self.cmdtxt.SetValue(joinlis(wraparglis(self.intprt ,[self.cuipath])+tmpmskdic['flag']+tmpmskdic['position'],' ',''))
            self.runlis=[self.intprt,self.cuipath]+tmprundic['flag']+tmprundic['position']
        self.runlis=checkrunlis(self.runlis)
        msgdlg('CMD arguments updated!')

    def runcmd(self, event):
        if not self.cmdlis:
            msgdlg('CMD arguments not assembled!','Error')
            return
        runtyp=self.runtyp.GetStringSelection()
        self.Show(False)
        #set shell=False for safety
        if runtyp=='Real-time':
            sys.stdout=sys.stderr=LogDlg(self)
            #logwin=LogDlg(self)
            #self.runpcs=subprocess.Popen(joinlis(self.cmdlis,' ',''),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
            self.runpcs=subprocess.Popen(self.runlis,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
            #write pre-defined ATQ arguments
            if self.atqlisbox.GetStrings():
                self.runpcs.stdin.write(joinlis(self.atqlisbox.GetStrings(),'\n','\n'))
            '''
            #note: iter() makes it possible to get output line-by-line in real-time, may cause initial deadlock issue?
            #caution: however, this solution disable the function to terminate the process?
            for line in iter(self.runpcs.stdout.readline, b''):
                wx.Yield()
                #logwin.write(notemsg)
                sys.stdout.write(line)
            self.runpcs.wait()
            '''
            #note: using poll(), the process could be terminated during running
            #caution: however, if the process ends too fast, it may lose some of the output
            while self.runpcs.poll() is None:
                wx.Yield()
                notemsg = self.runpcs.stdout.readline()
                if notemsg:
                    sys.stdout.write(notemsg)
            #caution: communicate()[0] was supposed to get the remaining part of output, however, the process becomes unresponsive
            #rstmsg=self.runpcs.communicate()[0]
            #sys.stdout.write(rstmsg)
            returncd=self.runpcs.returncode
            self.runpcs=None
            notedlg=wx.MessageDialog(None,'CUI process finished!\nCheck the Log information?','Note',wx.YES_NO | wx.ICON_INFORMATION)
            if notedlg.ShowModal()!=wx.ID_YES:
                notedlg.Destroy()
                self.Destroy()
        elif runtyp=='Background':
            self.runpcs=subprocess.Popen(self.runlis,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
            #self.runpcs=subprocess.Popen(joinlis(self.cmdlis,' ',''),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
            runwin=WaitDlg(self,asize=self.gpardic['waitsz'])
            if self.atqlisbox.GetStrings():
                self.runpcs.stdin.write(joinlis(self.atqlisbox.GetStrings(),'\n','\n'))
            while self.runpcs.poll() is None:
                wx.Yield()
                #may cause deadlock for long-running task without the following code ?
                notemsg = self.runpcs.stdout.readline()
                pass
            runwin.Show(False)
            runwin.Destroy()
            returncd=self.runpcs.returncode
            self.runpcs=None
            msgdlg('CUI process finished!','Note')
            self.Destroy()
            wx.Exit()
        elif runtyp=='Unattended':
            #Unattended mode do not support ATQ arguments, however, the system console could be used for QA interaction
            if self.atqlisbox.GetStrings():
                msgdlg('Unattended mode do not support ATQ arguments!','Error')
                self.Show()
                return
            subprocess.Popen(self.runlis,stdin=None,stdout=None,stderr=None,shell=False,close_fds=True)
            #subprocess.Popen(joinlis(self.cmdlis,' ',''),stdin=None,stdout=None,stderr=None,shell=True,close_fds=True)
            dlg = MsgDialog('CUI process started!', 'Note',actime=5)
            #wx.CallLater(5000, dlg.Destroy)
            dlg.ShowModal()
            #dlg.Destroy()
            self.Destroy()
            wx.Exit()
        elif runtyp=='Debug':
            #use customized console for better QA interaction and log management?
            pass

__appnm__='GUI2CUI'
__appver__='1.0'
__appdesc__='This is a customized version of GUI2CUI'

#for command-line usage
aparser=argparse.ArgumentParser(description=__appdesc__)
aparser.add_argument('gcicfg',help='GCI configuration file for the CUI APP (absolute path)')
aparser.add_argument('-v','--version', action='version', version=__appver__)
args=aparser.parse_args()

loadpath=os.path.abspath(args.gcicfg)

if __name__ == '__main__':
    app=wx.App(False)
    frame=MainFrame(None,cfgpath=loadpath)
    app.MainLoop()
