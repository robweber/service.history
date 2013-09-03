import os, sys, shutil
import sqlite3 as sqlite
import utils as utils
import xbmc
import xbmcvfs

class Database:     
        
        def __init__(self):                
                self.dataBasePath = os.path.join(xbmc.translatePath(utils.data_dir()), 'History.db')
                #use scripts home for reading SQL files
                self.sqlDir = os.path.join(xbmc.translatePath(utils.addon_dir()), 'resources', 'database')

                #quick check to make sure data_dir exists
                if(not xbmcvfs.exists(xbmc.translatePath(utils.data_dir()))):
                        xbmcvfs.mkdir(xbmc.translatePath(utils.data_dir()))
                
        def connect( self ):
                utils.log(self.dataBasePath)
                sqlite.register_adapter(str, lambda s:s.decode('utf-8'))
                self.connection = sqlite.connect(self.dataBasePath, check_same_thread = False)
                self.cursor = self.connection.cursor()
                
        def commit( self ):             
                try:
                        self.connection.commit()
                        return True
                except:
                        return False

        def close( self ):
                utils.log("close Connection",xbmc.LOGDEBUG)
                self.connection.close()
        
        def executeSQLScript(self, scriptName):
                sqlCreateFile = open(scriptName, 'r')
                sqlCreateString = sqlCreateFile.read()                                          
                self.connection.executescript(sqlCreateString)          
        
        def createTables(self):
                utils.log("Create Tables",xbmc.LOGDEBUG)        
                self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_CREATE.txt'))
                
        def dropTables(self):
                utils.log("Drop Tables",xbmc.LOGDEBUG)
                self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_DROP_ALL.txt'))
        
        def checkDBStructure(self):
                
                try:
                        rcbSettingRows = WatchHistory(self).getAll()
                        if(rcbSettingRows == None): 
                                self.self.createTables()
                                return 1, ""
                        rcbSetting = rcbSettingRows[0]                              
                        
                except  Exception, (exc): 
                        self.createTables()
                        
                        
                
                
        
class DatabaseObject:
        
        def __init__(self, gdb, tableName):
                self.gdb = gdb
                self.tableName = tableName
        
        def insert(self, args):         
                paramsString = ( "?, " * len(args))
                paramsString = paramsString[0:len(paramsString)-2]
                insertString = "Insert INTO %(tablename)s VALUES (NULL, %(args)s)" % {'tablename':self.tableName, 'args': paramsString }                
                self.gdb.cursor.execute(insertString, args)
                self.gdb.commit()
                
                utils.log("Insert INTO %(tablename)s VALUES (%(args)s)" % {'tablename':self.tableName, 'args': args },xbmc.LOGDEBUG)
                
        
        def update(self, columns, args, id):
                
                if(len(columns) != len(args)):
                        #TODO raise Exception?                  
                        return
                        
                updateString = "Update %s SET " %self.tableName
                for i in range(0, len(columns)):
                        updateString += columns[i] +  " = ?"
                        if(i < len(columns) -1):
                                updateString += ", "
                                
                updateString += " WHERE id = " +str(id)         
                self.gdb.cursor.execute(updateString, args)
                
        
        def deleteAll(self):
                self.gdb.cursor.execute("DELETE FROM '%s'" % self.tableName)            
        
        
        def getAll(self):
                self.gdb.cursor.execute("SELECT * FROM '%s'" % self.tableName)
                allObjects = self.gdb.cursor.fetchall()
                newList = self.encodeUtf8(allObjects)
                return newList
                
                
        def getAllOrdered(self,order):                
                self.gdb.cursor.execute("SELECT * FROM '%s' ORDER BY '%s' COLLATE NOCASE" % self.tableName,order)
                allObjects = self.gdb.cursor.fetchall()
                newList = self.encodeUtf8(allObjects)
                return newList          

        def getAllOrderedLimit(self,order,page,limit):
                startNum = page * limit
                self.gdb.cursor.execute("SELECT * FROM '%s' ORDER BY %s desc LIMIT %i, %i COLLATE NOCASE" % (self.tableName,order,startNum,limit))
                allObjects = self.gdb.cursor.fetchall()
                newList = self.encodeUtf8(allObjects)
                return newList
                
        def getOneByName(self, name):                   
                self.gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self.tableName, (name,))
                object = self.gdb.cursor.fetchone()
                return object
                
        def getObjectById(self, id):
                self.gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self.tableName, (id,))
                object = self.gdb.cursor.fetchone()             
                return object   
        
        def getObjectsByWildcardQuery(self, query, args):               
                #double Args for WildCard-Comparison (0 = 0)
                newArgs = []
                for arg in args:
                        newArgs.append(arg)
                        newArgs.append(arg)
                        
                return self.getObjectsByQuery(query, newArgs)           
                
        def getObjectsByQuery(self, query, args):
                self.gdb.cursor.execute(query, args)
                allObjects = self.gdb.cursor.fetchall()         
                return allObjects
                
        def getObjectsByQueryNoArgs(self, query):
                self.gdb.cursor.execute(query)
                allObjects = self.gdb.cursor.fetchall()         
                return allObjects

        def getObjectByQuery(self, query, args):                
                self.gdb.cursor.execute(query, args)
                object = self.gdb.cursor.fetchone()             
                return object
        
        
        def encodeUtf8(self, list):
                newList = []
                for item in list:
                        newItem = []
                        for param in item:
                                if type(param).__name__ == 'str':
                                        newItem.append(param.encode('utf-8'))
                                else:
                                        newItem.append(param)
                        newList.append(newItem)
                return newList

class WatchHistory(DatabaseObject):

        def __init__(self, gdb):                
                self.gdb = gdb
                self.tableName = "history"
        
