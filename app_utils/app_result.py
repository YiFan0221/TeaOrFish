
from flask import jsonify ,request
import requests
import json


def requests_api(mtext):
    ###
    #用來執行根據mtext 轉發的api
    ###
    ServerURL ='http://yfnoip.ddns.net:5000/Stock'
    
    #ex. 
    # [ testSpace/Echo,HI你好 ] 
    # mtext==[/Echo,HI你好]
    input_para = mtext[9:].split(',')
    #API URL 
    apiurl = ServerURL+input_para[0]
    #Para
    sendobj = None
    if len(input_para) > 1:
      sendobj = {'text':input_para[1]}        
    
    #post
    StateSt = requests.post(apiurl, json=sendobj )
    #header = {"content-type": "application/json"}
    #StateSt = requests.post(apiurl, json=sendobj , headers=header, verify=False )
    return StateSt
    


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


