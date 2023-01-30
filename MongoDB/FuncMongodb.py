###
# 撰寫來存取MongoDB的函式庫
###


import collections
import os
from enum import Enum, unique
import pprint
import pymongo
username = None
password = None
conn_str = None
import datetime

client =None
db     =None

@unique
class InfoType(Enum):
    SysLog = 'SYSLog'
    APILog_Linebot = 'apilog_Linebot'
    APILog_StockSearchlog = 'apilog_StockSearchlog'
    APILog_PostRank = 'apilog_PostRank'
    AIQuestion = 'AIQuestion'

#region ------ Common Function------
def ImportUserInfoByENV():
    global conn_str
    conn_str = os.environ.get('CONNECTSTRING')
    return conn_str

def Clientinit():
    global username
    global password
    global client
    global db    
    ImportUserInfoByENV()
    if(conn_str==None):
        return "-1"
    else:
        print("Mongodb connection string : "+conn_str )
    
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    try:
        print(client.server_info())
        db = client['APILOG']
    except Exception:
        print("Unable to connect to the server.")
        print(Exception)
        
        db = None
        
    
    
def getDataBase():
    global db
    if(db==None):
        if(client['APILOG']!=None):
            db = client['APILOG']
            return db    
        else:
            return None
    else:
        return db
    
def getConnectInfo(Collections:InfoType):
    #DataBase
    global db    
    
    if(getDataBase()!=None):
        db = getDataBase()
    else:
        return None        
    #Collections
    collections = db[Collections.value]    
    return collections
    
    
#endregion ------ Common ------

#region ------ Insert ------

def Insert_AIQuestion(text:str):
    return Insert_unit_nonTags(InfoType.AIQuestion,text)

def Insert_APILog_Trade(text:str):
    return Insert_unit_nonTags(InfoType.APILog_Trade,text)
    
def Insert_APILog_Linebot(text:str):
    return Insert_unit_nonTags(InfoType.APILog_Linebot,text)    

def Insert_APILog_PostRank(text:str):
    return Insert_unit_nonTags(InfoType.APILog_PostRank,text)  

def Insert_APILog_StockSearchlog(text:str):
    return Insert_unit_nonTags(InfoType.APILog_StockSearchlog,text)    
    
def Insert_unit_nonTags(Collections:InfoType,text:str):
    return Insert_unit(Collections,text,None)

def Insert_unit(Collections:InfoType,text:str,Tags:tuple):
    return False
    #插入資料庫的根本函式
    
    #connect     
    collections = getConnectInfo(Collections)
    if(collections==None):
        return False

    post = {
    "TypeName": Collections.value,
    "text": text,
    "tags": [Collections.value, text],
    "date": datetime.datetime.utcnow(),
    }
    
    post_id = collections.insert_one(post).inserted_id
    # print("post_id:"+str(post_id))
    return post_id

#endregion ------ Insert ------

#region ------ Find ------
def Find_one_byid(Collections:InfoType,post_id):
    #connect     
    collections = getConnectInfo(Collections)
    if(collections==None):
        return False
    pprint.pprint(collections.find_one({"_id": post_id}))
    return True
        
def Find(Collections:InfoType,SelectItemName:str,SelectItem:str):
    #connect     
    collections = getConnectInfo(Collections)
    if(collections==None):
        return False
    
    for post in collections.find({SelectItemName: SelectItem}):
        pprint.pprint(post)      
    return True
        
#endregion ------ Find ------        

#region ------ Delete ------
def delete(Collections:InfoType,SelectItemName:str,SelectItem:str):
    #connect     
    collections = getConnectInfo(Collections)
    if(collections==None):
        return False
    
    query = {SelectItemName: SelectItem}
    d = collections.delete_many(query)
    print(d.deleted_count, " documents deleted !!")
    return True
    
        
#endregion ------ Delete ------

Clientinit()
# id=Insert_unit_nonTags(InfoType.SysLog,"System On.")
# Find(InfoType.APILog_Linebot,"_id",id)#display 
# delete(InfoType.APILog_Line,"TypeName",InfoType.APILog_Line.value)