#-*- coding: utf-8 -*-

#basic information
__appnm__='DbBase'
__appver__='1.0'

#load internal packages
import sqlite3 as sql3
from contextlib import closing

#functions
#sqlite3 functions
#issue: try except in with ?
def sql3_exe(dbdir,sqlcmd,sqlargs=(),emany=0):
    #try:
        with closing(sql3.connect(dbdir)) as dbcn:
            with closing(dbcn.cursor()) as dbcs:
                if emany:
                    dbcs.executemany(sqlcmd,sqlargs)
                else:
                    dbcs.execute(sqlcmd,sqlargs)
            dbcn.commit()
    #except Exception as em:
    #    raise Exception('sql3_exe: '+sqlcmd%sqlargs)

def sql3_fch(dbdir,sqlcmd,sqlargs=(),fchrst='all'):
    try:
        with closing(sql3.connect(dbdir)) as dbcn:
            with closing(dbcn.cursor()) as dbcs:
                dbcs.execute(sqlcmd,sqlargs)
                if fchrst=='all':
                    #print(dbcs.description)
                    return dbcs.fetchall()
                elif fchrst=='one':
                    #print(dbcs.description)
                    return dbcs.fetchone()
    except Exception as em:
        raise em
        #raise Exception('sql3_fch: '+sqlcmd%sqlargs)

def sql3_unicol(dbdir,colnm,tabnm):
    sqltmp='select %s from %s group by %s'%(colnm,tabnm,colnm)
    atups=()
    unilis=sql3_fch(dbdir,sqltmp,atups)
    return unilis
