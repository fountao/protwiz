#!/usr/bin/env python
# -*- coding: utf-8 -*-


__appnm__='GUI2KIT'
__appver__='1.0'
__appdesc__='This is a customized version of GUI2KIT'

import sys 
import re
import argparse
import subprocess
import os
import json
import wx
import textwrap
from wx.adv import Animation
from wx.adv import GenericAnimationCtrl as AnimationCtrl
from io import BytesIO
from functools import partial
from collections import OrderedDict
import webbrowser

#required keys for validation of the configuration file
ckeydic={'kitinfo':['name','version','description','developer','contact','homepage','license','standard'],
        'gkipars':['gcictor','interpreter','icon','logo','splash','fadeio','transparency','help','sptime','spmaxsz','fontsz','logomaxsz','infowidth','descsz'],
        'cuilist':[]
}

#get script path
scpdir=os.path.abspath(os.path.realpath(sys.argv[0]))
if not os.path.isdir(scpdir):
    scpdir=os.path.dirname(scpdir)
sys.path.append(scpdir)


def dic2tab(adic,alis):
    'convert a dic to a tab according to the order of alis'
    rst=[]
    for ea in alis:
        if ea in adic.keys():
            rst.append([ea,adic[ea]])
        else:
            rst.append([ea,''])
    return rst

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

def msgdlg(msgtxt,msgtit='Note',msgsty=wx.OK,fatal=0):
    'message dialogy for displaying note and error information'
    errdlg=wx.MessageDialog(None,textwrap.fill(msgtxt,50),msgtit,msgsty)
    errdlg.ShowModal()
    errdlg.Destroy()
    if fatal==1:
        sys.exit(0)

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

def resource_path(relative):
    'get the paths of resource files after packaged in one file by pyinstaller'
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

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

def loadcuilis(cuilis,curdir):
    rtab=[]
    for ec in cuilis:
        if os.path.isabs(ec):
            cuifi=ec
        else:
            #cuifi=os.path.join(curdir,*list(os.path.split(ec)))
            cuifi=os.path.join(curdir,ec)
        if not os.path.isfile(cuifi):
            msgdlg('CUI config file not found: %s!'%cuifi,'Error',fatal=1)
        try:
            gcidic=json2dic(cuifi,1)
        except Exception as em:
            msgdlg('CUI config file error: %s!\n%s'%(cuifi,str(em)),'Error',fatal=1)
        appdir=os.path.dirname(cuifi)
        appcls=os.path.basename(appdir)
        appfi=os.path.join(appdir,gcidic['gcipars']['cuiapp'])
        try:
            tmplis=[gcidic['appinfo']['name'],gcidic['appinfo']['version'],gcidic['gcipars']['cuiapp'],cuifi,appcls,gcidic['appinfo']['description']]
        except Exception as em:
            msgdlg('CUI config file error: %s!\n%s'%(cuifi,str(em)),'Error',fatal=1)
        rtab.append(tmplis)
    return rtab

dfticon=os.path.join(scpdir,resource_path('dft_gci.ico'))
dftlogo=os.path.join(scpdir,resource_path('dft_gci_logo.png'))

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
        self.img.SetToolTip('Powered by '+__appver__)
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


class MainFrame(wx.Frame): 
    def __init__(
        self,parent,cfgpath,pos=wx.DefaultPosition,size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX)|wx.MINIMIZE_BOX
        ):
        wx.Frame.__init__(self, parent, -1, '', pos, size, style)
        #scpdir: script directory, defined globally after importing modules
        self.scpdir=scpdir
        self.cfgpath=os.path.abspath(cfgpath)
        self.kitdir=os.path.dirname(self.cfgpath)
        #super(Mywin, self).__init__(parent, title = title) 
        #check configuration file
        if not os.path.isfile(self.cfgpath):
            msgdlg('GCI configuration file: [ %s ] is not exist!'%self.cfgpath,'Error',fatal=1)

        self.mainpnl = wx.Panel(self) 
        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        #cfg data
        gkidic=json2dic(self.cfgpath,1)
        cfglis=[]
        #for py3.x, ek = each key
        for ek in gkidic:
            cfglis.append(ek)
        tmplb,tmpnote=checkplis(cfglis,list(ckeydic.keys()))
        if not tmplb:
            msgdlg('Configuration error in root node: \n%s'%tmpnote,'Error',fatal=1)
        self.infodic=gkidic['kitinfo']
        tmplb,tmpnote=checkplis(list(self.infodic.keys()),ckeydic['kitinfo'])
        if not tmplb:
            msgdlg('Configuration error in kitinfo: \n%s'%tmpnote,'Error',fatal=1)
        self.gpardic=gkidic['gkipars']
        tmplb,tmpnote=checkplis(list(self.gpardic.keys()),ckeydic['gkipars'])
        if not tmplb:
            msgdlg('Configuration error in gkipars: \n%s'%tmpnote,'Error',fatal=1)
        if 'cuilist' not in gkidic:
            msgdlg('Configuration error: \n cuilist is required! \n (The file name with extension for the CUI app.)','Error',fatal=1)
        self.cuilist=gkidic['cuilist']
        if len(self.cuilist)==0:
            msgdlg('No CUI apps are defined in the CFG list!','Error',fatal=1)
        self.gcictor=self.gpardic['gcictor']
        if not self.gcictor:
            msgdlg('GCIctor not defined!','Error',fatal=1)
        #check gcictor
        if not os.path.isabs(self.gcictor):
            self.gcictor=os.path.join(self.kitdir,self.gcictor)
        if not os.path.isfile(self.gcictor):
            msgdlg('GCIctor not exist!','Error',fatal=1)
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
        self.splashpath=os.path.join(self.kitdir,self.gpardic['splash'])
        #if not self.gpardic['splash'] or not os.path.exists(self.splashpath):
        if not os.path.isfile(self.splashpath):
            self.splashpath=''
        self.icopath=os.path.join(self.kitdir,self.gpardic['icon'])
        if not os.path.isfile(self.icopath):
            self.icopath=dfticon
        self.logopath=os.path.join(self.kitdir,self.gpardic['logo'])
        if not os.path.isfile(self.logopath):
            self.logopath=dftlogo
        #check help doc for the cui-app
        self.help_path=os.path.join(self.kitdir,self.gpardic['help'])
        if not os.path.isfile(self.help_path):
            self.help_path=''
        os.chdir(self.kitdir)
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
        self.SetFont(wx.FFont(fontsz,wx.FONTFAMILY_DEFAULT))
        self.SetBackgroundColour(wx.NullColour)
        self.boldft=wx.Font(fontsz,wx.DEFAULT,wx.NORMAL,weight=wx.BOLD)
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
        if not self.gpardic['descsz']:
            self.gpardic['descsz']='[500,60]'
        if not self.gpardic['logomaxsz']:
            self.gpardic['logomaxsz']='[120,120]'
        for es in ['spmaxsz','logomaxsz','descsz']:
            self.gpardic[es]=json.loads(self.gpardic[es])
        if not self.gpardic['sptime']:
            self.gpardic['sptime']='5'
        self.gpardic['sptime']=int(self.gpardic['sptime'])
        if not self.gpardic['infowidth']:
            self.gpardic['infowidth']='520'
        self.gpardic['infowidth']=int(self.gpardic['infowidth'])

        #check logo
        imgtyp=re.split('\.',os.path.basename(self.logopath))[-1].lower()
        if imgtyp=='gif':
            logoanm=Animation(self.logopath)
            self.cuilogo=AnimationCtrl(self.mainpnl, -1,logoanm,size=self.gpardic['logomaxsz'])
            self.cuilogo.SetUseWindowBackgroundColour()
            self.cuilogo.Play()
        else:
            with open(self.logopath,'rb') as imgdat:
                imgstm=BytesIO(imgdat.read())
                imgobj=wx.Image(imgstm)
                tmpws,tmphs=autoscale(self.gpardic['logomaxsz'],imgobj.GetSize())
                imgobj=imgobj.Scale(tmpws,tmphs,wx.IMAGE_QUALITY_HIGH)
                imgobj=wx.Bitmap(imgobj)
                self.cuilogo=wx.StaticBitmap(self.mainpnl,-1,imgobj)

        #app information
        infosizer=wx.BoxSizer(wx.HORIZONTAL)
        infosizer.Add(self.cuilogo,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,0)
        #description sizer
        #add version to name
        descbox=wx.StaticBox(self.mainpnl, -1, self.infodic['name'])
        descsizer = wx.StaticBoxSizer(descbox, wx.VERTICAL)
        descsizer.SetMinSize((self.gpardic['infowidth'],-1))
        desctext =wx.TextCtrl(self.mainpnl,-1,value=self.infodic['description'],size=self.gpardic['descsz'],style=wx.TE_MULTILINE|wx.TE_READONLY)
        desctext.SetBackgroundColour(wx.NullColour)
        desctext.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        desctext.Bind(wx.EVT_SET_FOCUS, self.emptyfunc)
        descsizer.Add(desctext, 0, wx.TOP|wx.LEFT|wx.EXPAND,5)
        descsizer.Add(wx.StaticLine(self.mainpnl,-1),0,wx.ALL|wx.EXPAND,5)
        #help sizer
        helpsizer=wx.BoxSizer(wx.HORIZONTAL)
        infotxt=wx.StaticText(self.mainpnl, label="About")
        infotxt.SetFont(self.boldft)
        infotxt.SetToolTip('Detailed APP information')
        infotxt.SetForegroundColour('Blue')
        infotxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        infotxt.Bind(wx.EVT_LEFT_UP, partial(self.dspinfo,infotab=dic2tab(self.infodic,ckeydic['kitinfo'])))
        doctxt=wx.StaticText(self.mainpnl, label="Docs")
        doctxt.SetFont(self.boldft)
        doctxt.SetToolTip('Local user documentation')
        doctxt.SetForegroundColour('Blue')
        doctxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        if self.help_path:
            doctxt.Bind(wx.EVT_LEFT_UP, partial(self.loc_brs,fipath=self.help_path))
        hptxt=wx.StaticText(self.mainpnl, label="Homepage")
        hptxt.SetFont(self.boldft)
        hptxt.SetToolTip('APP homepage')
        hptxt.SetForegroundColour('Blue')
        hptxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        if self.infodic['homepage']:
            hptxt.Bind(wx.EVT_LEFT_UP, partial(self.web_brs, weblink=self.infodic['homepage']))
        helpsizer.Add(infotxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        helpsizer.Add(wx.StaticLine(self.mainpnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        helpsizer.Add(doctxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        helpsizer.Add(wx.StaticLine(self.mainpnl,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        helpsizer.Add(hptxt,proportion=0,flag=wx.ALL|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,border=2)
        descsizer.Add(helpsizer,1,wx.ALL|wx.ALIGN_RIGHT,0)
        infosizer.Add(descsizer,0,wx.ALL|wx.EXPAND,2)

        #add searchctrl
        self.schctrl=wx.SearchCtrl(self.mainpnl, style=wx.TE_PROCESS_ENTER,size=(200,-1))
        if 'gtk3' in wx.PlatformInfo:
            # Something is wrong with the bestsize of the SearchCtrl, so for now
            # let's set it based on the size of a TextCtrl.
            tmpctrl = wx.TextCtrl(self.mainpnl)
            tmpctsz = tmpctrl.GetBestSize()
            tmpctrl.DestroyLater()
            self.schctrl.SetMinSize((200, tmpctsz.height+4))
        self.schctrl.ShowCancelButton(True)
        self.schctrl.SetToolTip(wx.ToolTip("Search for APPs ..."))
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch,self.schctrl)

        lisbox=wx.StaticBox(self.mainpnl, -1,'APP list')
        lisboxsz=wx.StaticBoxSizer(lisbox, wx.VERTICAL)
        #add lisctrl
        self.lisctrl = wx.ListCtrl(self.mainpnl, -1, size=(-1,180),style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        #add title row
        self.lisctrl.InsertColumn(0, 'Index') 
        self.lisctrl.InsertColumn(1, 'APP Classification', wx.LIST_FORMAT_CENTER) 
        self.lisctrl.InsertColumn(2, 'Name', wx.LIST_FORMAT_CENTER) 
        self.lisctrl.InsertColumn(3, 'Version', wx.LIST_FORMAT_CENTER) 
        self.lisctrl.InsertColumn(4, 'CUI APP',width=wx.LIST_AUTOSIZE_USEHEADER)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.lisctrl)
        self.sltidx=None
        #load self.cuilist
        #[ [name,version,directory,description],...]
        self.slistab=loadcuilis(self.cuilist,self.kitdir)
        self.listab=self.slistab.copy()
        #0: proportion
        lisboxsz.Add(self.lisctrl, 0, wx.EXPAND|wx.ALL,5)
        lisboxsz.Add(wx.StaticLine(self.mainpnl,-1),0,wx.ALL|wx.EXPAND,5)
        countsz=wx.BoxSizer(wx.VERTICAL)
        self.countinfo=wx.StaticText(self.mainpnl, label="Total CUI APPS: %s | Selected CUI APP: %s"%(len(self.listab),'None'))
        #self.countinfo.SetFont(self.boldft)
        infotxt.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        countsz.Add(self.countinfo,proportion=0,flag=wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL,border=0)
        lisboxsz.Add(countsz,0,wx.ALL|wx.EXPAND,5)
        
        
        #information for selected app
        self.sltsz=wx.BoxSizer(wx.HORIZONTAL)
        sltdescbox=wx.StaticBox(self.mainpnl, -1, 'About selected APP:')
        sltdescsz = wx.StaticBoxSizer(sltdescbox, wx.VERTICAL)
        self.sltdesctext =wx.TextCtrl(self.mainpnl,-1,value='',size=(-1,64),style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.sltdesctext.SetBackgroundColour(wx.NullColour)
        self.sltdesctext.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.sltdesctext.Bind(wx.EVT_SET_FOCUS, self.emptyfunc)
        sltdescsz.Add(self.sltdesctext, 0, wx.ALL|wx.EXPAND,5)
        self.sltsz.Add(sltdescsz,1,wx.EXPAND|wx.EAST|wx.WEST,0)

        self.updlist()

        #ctrl panel
        self.ctrlbox = wx.BoxSizer(wx.HORIZONTAL)
        loadbut=wx.Button(self.mainpnl, label="Load APP")
        self.Bind(wx.EVT_BUTTON, self.Loadapp, loadbut)
        loadbut.SetToolTip("Load selected APP ...")

        resetbut=wx.Button(self.mainpnl,label= "Reset")
        self.Bind(wx.EVT_BUTTON, self.Resetlis, resetbut)
        resetbut.SetToolTip("Reset APP list and selection ...")
        
        self.ctrlbox.Add(loadbut, flag=wx.ALL, border=5)
        self.ctrlbox.Add(resetbut, flag=wx.ALL, border=5)

        #main boxsizer
        self.mainbox.Add(infosizer,0, wx.ALIGN_CENTER|wx.EAST|wx.WEST,10)
        self.mainbox.Add(self.schctrl,0,wx.EXPAND|wx.EAST|wx.WEST|wx.NORTH,10)
        self.mainbox.Add(lisboxsz,0,wx.EXPAND|wx.ALL,10) 
        self.mainbox.Add(self.sltsz,0,wx.EXPAND|wx.EAST|wx.WEST,10) 
        self.mainbox.Add(self.ctrlbox,0, wx.ALIGN_CENTER)
        #Gtk3 eats the heights??
        if 'gtk3' in wx.PlatformInfo:
            self.mainbox.Add(wx.StaticText(self.mainpnl, -1, " "),0, wx.ALIGN_CENTER)
            self.mainbox.Add(wx.StaticText(self.mainpnl, -1, " "),0, wx.ALIGN_CENTER)

        
        self.mainpnl.SetSizer(self.mainbox) 
        self.mainpnl.Fit()
        self.Fit()
        self.Centre() 

        self.SetTransparent(self.amount)
        #fade in out effect
        if self.gpardic['fadeio']=='True':
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

    def web_brs(self,event,weblink):
        webbrowser.open(weblink)

    def loc_brs(self,event,fipath):
        if os.path.exists(fipath):
            webbrowser.open(fipath)
        else:
            msgdlg('Local file [%s] is not exist!'%fipath,msgtit='Error')

    def OnClose(self, event):
        if (not self.ctimer.IsRunning()) and (not self.stimer.IsRunning()):
            self.ctimer.Start(50)

    def fadein(self, evt):
        self.amount += self.tincrs
        if self.amount >= 255:
            self.amount = 255
            self.stimer.Stop()
        self.SetTransparent(self.amount)

    def fadeout(self, evt):
        self.amount -= self.tincrs
        if self.amount <= 0:
            self.ctimer.Stop()
            self.Hide()
            wx.Exit()
            #sys.exit()
        self.SetTransparent(self.amount)
        
    def dspinfo(self,event,infotab):
        win = AppInfo(self,infotab)
        win.Show(True)

    def emptyfunc(self, event):
        pass

    def OnItemSelected(self, event):
        self.currentItem = event.Index
        self.sltidx=self.currentItem
        tmpdesc=self.listab[self.currentItem][-1]
        if not tmpdesc:
            tmpdesc='No description!'
        #parse app pars
        #update selected app information
        self.sltdesctext.SetValue(tmpdesc)
        self.countinfo.SetLabel("Total CUI APPS: %s | Selected CUI APP: %s"%(len(self.listab),self.listab[self.sltidx][0]))

       
    def updlist(self):
        self.lisctrl.DeleteAllItems()
        cnu=1
        for er in self.listab:
            index = self.lisctrl.InsertItem(self.lisctrl.GetItemCount(), str(cnu)) 
            #to get relative path
            rltpath=os.path.dirname(er[3].replace(os.path.dirname(self.scpdir), '.', 1))
            self.lisctrl.SetItem(index, 1, os.path.basename(rltpath).replace('_',' ').title())
            self.lisctrl.SetItem(index, 2, er[0]) 
            self.lisctrl.SetItem(index, 3, er[1]) 
            self.lisctrl.SetItem(index, 4, er[2])
            self.lisctrl.SetItemData(index, cnu)
            cnu+=1
        self.lisctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.lisctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lisctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.lisctrl.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.lisctrl.SetColumnWidth(4, 150)
        self.sltdesctext.SetValue('')
        self.sltidx=None
        self.countinfo.SetLabel("Total CUI APPS: %s | Selected CUI APP: %s"%(len(self.listab),"None"))
        #self.currentItem = 0

    def OnSearch(self,evt):
        schkey=self.schctrl.GetValue()
        #search name, version , description or classification
        self.listab=[]
        for es in self.slistab:
            if re.findall(schkey.lower(),es[-1].lower()) or re.findall(schkey.lower(),es[0].lower()) or re.findall(schkey.lower(),es[1].lower()) or re.findall(schkey.lower(),es[-2].lower()):
                self.listab.append(es)
        self.updlist()

    def Loadapp(self,evt):
        if self.sltidx==None:
            msgdlg('Not select a CUI APP!')
        else:
            runlis=[]
            if self.intprt:
                runlis=[self.intprt]
            runlis.append(self.gcictor)
            runlis.append(self.listab[self.sltidx][3])
            subprocess.Popen(runlis,stdin=None,stdout=None,stderr=None,shell=False,close_fds=True)
    

    def Resetlis(self,evt):
       self.listab=self.slistab.copy()
       self.updlist()



#change the parameter file here
cfgfile=r'SeqWiz_KIT.json'
loadpath=os.path.join(scpdir,cfgfile)


if __name__ == '__main__':
    app=wx.App(False)
    frame=MainFrame(None,cfgpath=loadpath)
    app.MainLoop()
