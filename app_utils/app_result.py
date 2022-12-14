from enum import Enum, unique
from flask import jsonify ,request
import requests
import json
import os
TARGET_SERVER_URL = os.environ.get('TARGET_SERVER_URL')


@unique
class RESTful(Enum):
    GET = 0
    POST= 1

def requests_POST_Stock_api(input_APIAndPara):
    ###
    #用來執行<POST>,並根據mtext 轉發的api
    ###
    ServerURL =TARGET_SERVER_URL+'/Stock'
    rtn =  requests_api(RESTful.POST,ServerURL,input_APIAndPara)
    return rtn    
  
def requests_GET_Stock_api(input_APIAndPara):
    ###
    #用來執行<GET>,並根據mtext 轉發的api
    ###
    ServerURL =TARGET_SERVER_URL+'/Stock'
    rtn = requests_api(RESTful.GET , ServerURL,input_APIAndPara)    
    return rtn

def requests_POST_Other_api(input_APIAndPara):
    ###
    #用來執行<POST>,並根據mtext 轉發的api
    ###
    ServerURL =TARGET_SERVER_URL+'/Other'
    rtn =  requests_api(RESTful.POST,ServerURL,input_APIAndPara)
    return rtn    
  
def requests_GET_Other_api(input_APIAndPara):
    ###
    #用來執行<GET>,並根據mtext 轉發的api
    ###
    ServerURL =TARGET_SERVER_URL+'/Other'
    rtn = requests_api(RESTful.GET , ServerURL,input_APIAndPara)    
    return rtn        
        
def requests_api(REST:RESTful , ServerURL:str , input_APIAndPara):    
    #ex. 
    # [ testSpace/Echo,HI你好 ] 
    # mtext==[/Echo,HI你好]
    input_para = input_APIAndPara.split(',')
    #API URL 
    apiurl = ServerURL+input_para[0]
    #Para
    sendobj = None
    if len(input_para) > 1:
      sendobj = {'text':input_para[1]}        
    
    header = {'Connection':'close',"content-type": "application/json"}
    httpcode=200
    try:
      if(REST == RESTful.GET):
        StateSt = requests.get(apiurl, json=sendobj , headers=header, verify=False )  
      elif(REST == RESTful.POST):
        StateSt = requests.post(apiurl, json=sendobj , headers=header, verify=False)
    except requests.exceptions.Timeout:
      httpcode = 500
      StateSt = '服務器回應過長，請聯繫開發者'
    except requests.exceptions.TooManyRedirects:
      httpcode = 503
      StateSt = '服務器異常，請聯繫開發者'
    except Exception:
      httpcode = 500
      StateSt = '發生未知錯誤，請聯繫開發者'      
    if type(StateSt)!=str:      
      respon = json.loads(StateSt.text)      
    return respon['result']
            
status = {
    200:"OK",
    400:"Bad Request",
    401:"unauthorized",
    403:"Forbidden",
    404:"Not Found",
    405:"Method Not Allowed",
    500:"Internal Server Error"
}

#http code description (default)
default_description = {
    200:"Successful response.",
    400:"Please check paras or query valid.",
    401: 'Please read the document to check API.',
	403: 'Please read the document to check API.',
	404: 'Please read the document to check API.',
	405: 'Please read the document to check API.',
	500: 'Please contact api server manager.'
}

    
def result_json(code, data = {}, description = ''):
	description = default_description.get(code) if description == '' else description
	response = json.dumps({
		"code": code,
		"status": status.get(code),
		"result": data,
		"description": description
	}, default=lambda o: '<not serializable>')

	return response, code, {'Content-Type': 'application/json'}


