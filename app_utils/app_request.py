from enum import Enum, unique
from flask import jsonify ,request
import requests
import json
import os
import logging
TARGET_SERVER_URL = os.environ.get('TARGET_SERVER_URL')
logger = logging.getLogger("linebotApp")

@unique
class RESTful(Enum):
    GET = 0
    POST= 1

def requests_POST_Stock_api(input_APIAndPara):
  """Forward <POST> by mtext.

  Args:
      input_APIAndPara (_type_): /url

  Returns:
      _type_: respon of server
  """
  ServerURL =TARGET_SERVER_URL
  rtn =  requests_api(RESTful.POST,ServerURL,input_APIAndPara)
  return rtn    
  
def requests_GET_api(input_APIAndPara):
  """Forward <GET> by mtext.

  Args:
      input_APIAndPara (_type_): /url

  Returns:
      _type_: respon of server
  """

  ServerURL =TARGET_SERVER_URL
  rtn = requests_api(RESTful.GET , ServerURL,input_APIAndPara)    
  return rtn       
        
def requests_api(REST:RESTful , ServerURL:str , input_APIAndPara):    
  #ex. 
  # [ testSpace/Echo,HI你好 ] 
  # mtext==[/Echo,HI你好]
  logger.info("requests_api started")
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
    logger.info(f"{REST.name} [URL]:{ServerURL} [APIPara]:{input_APIAndPara}")
    if(REST == RESTful.GET):
      StateSt = requests.get(apiurl, json=sendobj , headers=header, verify=False )  
    elif(REST == RESTful.POST):
      StateSt = requests.post(apiurl, json=sendobj , headers=header, verify=False)
    logger.info("requests_api OK")
  except requests.exceptions.Timeout as e:
    httpcode = 500
    StateSt = '服務器回應過長，請聯繫開發者'
    logger.error(f"{httpcode} {StateSt.text} e{e}")
    
  except requests.exceptions.TooManyRedirects as e:
    httpcode = 503
    StateSt = '服務器異常，請聯繫開發者'
    logger.error(f"{httpcode} {StateSt.text} e{e}")
  except Exception as e:
    httpcode = 500
    StateSt = '發生未知錯誤，請聯繫開發者'      
    logger.error(f"{httpcode} {StateSt.text} e{e}")
  if type(StateSt)!=str:      
    respon = json.loads(f"{StateSt.text}")
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


