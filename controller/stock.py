from . import stock_controller as controller
from typing import Any
from flask import app, request
from flask.wrappers import Response
import json , logging , string
from backend_models.stocksearch import *
from app_utils.app_result import result_json
#-------------共用函式-------------
from enum import Enum, unique
@unique
class BodyType(Enum):
    applicationjson = 'multipart/form-data'
    multipartformdata = 'application/json'
def FuncGetFormValue(DataType:type , EventName,):
    #TODO def FuncGetFormValue(DataType:type,EventName,)
    #根據傳入種類找尋網頁中屬於{EventName}的值
    #並嘗試轉換成所需的型態{DataType}並回傳

    #從Body取值
    getData:Any = None
    if request.mimetype==BodyType.multipartformdata.value:
        # getData=request.json[EventName]
        # getData= getData.json['value']
        data = json.loads(request.data)
        getData = data[EventName]              
    elif request.mimetype==BodyType.applicationjson.value:            
        getData=request.form.get(EventName) 
    else:
        return None

    #將值依照所需轉型並回傳
    if DataType==int:
        return int(getData)
    elif DataType==string:
        return str(getData)
    else:
        return None

def FuncEventLog(EventName,GETPOST):
    #TODO def FuncEventLog(EventName,GETPOST):
    #使用傳入的Post/Get種類{GETPOST}，與事件名稱{EventName}
    #ex : 'a [GET] [camera device list] event'
    logging.info('a '+GETPOST+' ['+EventName+'] event')

def FuncEventExecSDK(EventSDKAPI,*args):
    #TODO def FuncEventExecSDK(EventSDKAPI,*args):
    #執行所登入的SDK(或其他)函式
    TestMode = False
    if(TestMode==True): #測試用尚未實裝
        return #這編寫回傳200
    if args==():#沒帶參數值時直接執行函式
        return EventSDKAPI() 
    else:#有帶參數值時將參數帶入函式執行
        return EventSDKAPI(*args)
    
#-------------共用函式-------------

#-------------API 框架範例-------------
# <{}為說明Hint {}內為前者說明>
#TODO#207{API No.}-set sharpness value{API名稱} #0-100{數值合法範圍}
# @controller.route('sharpness_color'{URL}, methods=["POST"]{GET/POST})
# def set_image_sharpness():{函式名稱}
#     #-------------------新增API所需登記項目--------------------------
#     eventName:str        = 'sharpness_color'{API名稱/Body名稱}
#     eventSDKAPI:function = camera.set_image_sharpness{要執行的函式(SDK Function)}
#     
#     min:int              = 0{收到數值的合法範圍最小值}
#     max:int              = 100{收到數值的合法範圍最大值}
#     expectType:type      = int{收到數值期望後送的型態}    
#     returnStr_200        = "Success"  {回應訊息:成功200}
#     returnStr_400        = "Please check paras or query valid."  {回應訊息:成功400}
#     #-------------------此處以下不需更動直接套用即可-------------------
#     FuncEventLog(eventName,request.method){將收到的事件存成訊息}
#     status=FuncGetFormValue(expectType,eventName) {嘗試從Body取出資訊並轉型}
#     if min<= status <= max:{部分邏輯判斷}
#       FuncEventExecSDK(eventSDKAPI,status){執行預先登記好的函式}
#       return result_json(200, returnStr_200)
#     else:
#       return result_json(400, returnStr_400)



    
@controller.route('/Echo', methods=["POST"])
def set_Echo():  
    eventName:str    = 'text'  
    eventSDKAPI:function =Func_Echo
    expectType:type      = string#int or bool
    returnStr            = ""
    returnStr_200        = "Success"
    returnStr_400        = "Please check paras or query valid."
    FuncEventLog(eventName,request.method)
    status=FuncGetFormValue(expectType,eventName)
    returnStr = FuncEventExecSDK(eventSDKAPI,status)
    return result_json(200, returnStr)

    

@controller.route("/SearchStock",methods=['GET'])
def Get_SearchStock(mtext):
  """
    搜尋對應的股票資訊(爬蟲)
    ---
    tags:
      - Stock
    description:
      搜尋股票資訊(爬蟲版)
    produces: application/json,
    parameters:
    - name: name
      in: path
      required: true
      type: string    
    responses:
      400:
        description: InvalidSignatureError
      200:
        description: Receive Line request.
  """
  m_data =Func_SearchStock_cnyes(mtext)
  if(type(m_data)== str):
      rtn_text =m_data
  else:
      st=('股票名稱:'+m_data.get('股票名稱')+' ('+m_data.get('股票編號')+')\n'+
      '股票現價:'+m_data.get('股票現價')+'\n'+                         
      '漲跌:'+m_data.get('漲跌')+' ('+m_data.get('漲跌幅')+')\n'     
      '本益比:'+m_data.get('本益比')+'\n'+     
      '本淨比:'+m_data.get('本淨比'))
      rtn_text=st    
  return rtn_text  

