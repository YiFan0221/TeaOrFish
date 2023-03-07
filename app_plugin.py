from flask                import Flask, request, render_template ,abort
from flask_cors           import CORS
from linebot              import LineBotApi, WebhookHandler
from linebot.exceptions   import InvalidSignatureError
from linebot.models       import * #MessageEvent,TextMessage,ImageSendMessage
from datetime import datetime
import app_utils.app_result as ap
from flasgger             import Swagger
import openai
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

dt_Access = datetime(1,1,1,0,0,0) #不限制就是 None #限制格式 datetime(2023,3,8,23,42,30) 

def checkAuthorization():
  dt_now = datetime.now()
  st_now = dt_now.strftime("%Y-%m-%d %H:%M:%S %p")
  
  if(dt_now > dt_Access and dt_Access!=datetime(1,1,1,0,0,0)):
    print("Authorization:Failed")
    os._exit()
  else:
    return True

def loop_checkAuthorization():
  scheduler = BackgroundScheduler(timezone="Asia/Taipei")
  scheduler.add_job(checkAuthorization, 'interval', hours=1)
  scheduler.start()
  
  
print("Check Authorization.")
if(checkAuthorization()):
  print("Authorization:PASS")
loop_checkAuthorization()

print("[Inital][ENV]")
LINEBOT_POST_TOKEN  = os.environ.get('LINEBOT_POST_TOKEN')
LINEBOT_RECV_TOKEN  = os.environ.get('LINEBOT_RECV_TOKEN')
CONNECTSTRING       = os.environ.get('CONNECTSTRING')
TARGET_SERVER_URL   = os.environ.get('TARGET_SERVER_URL')
SSL_PEM             = os.environ.get('SSL_PEM')
SSL_KEY             = os.environ.get('SSL_KEY')
SERVER_PORT         = os.environ.get('TEAORFISH_SERVER_PORT')
openai.api_key      = os.getenv("OPENAI_API_KEY")

print("ENV:LINEBOT_POST_TOKEN : "+LINEBOT_POST_TOKEN )
print("ENV:TARGET_SERVER_URL  : "+TARGET_SERVER_URL )
print("ENV:LINEBOT_RECV_TOKEN : "+LINEBOT_RECV_TOKEN )
print("ENV:SERVER_PORT        : "+str(SERVER_PORT) )
print("ENV:SECRETS_SSL_PEM    : "+str( os.path.exists("/run/secrets/SSL_PEM") ))
print("ENV:SECRETS_SSL_KEY    : "+str( os.path.exists("/run/secrets/SSL_KEY") ))
print("ENV:SSL_PEM            : "+str( SSL_PEM))
print("ENV:SSL_KEY            : "+str( SSL_KEY))

Linebot_Post_handle = LineBotApi(LINEBOT_POST_TOKEN)
Linebot_Recv_handle = WebhookHandler(LINEBOT_RECV_TOKEN)
Mode = 'AI Mode'

app = Flask(__name__)
CORS(app)

print("[Inital][SSL]")                          

import ssl
context = ssl.SSLContext()
context.load_cert_chain(SSL_PEM,SSL_KEY)
      

class opaibotPara:
  model = "text-davinci-003"
  temperature = 0.0
  maxtoken = 200
    
      
str_doc = str(
          "說明:可使用下列參數對AI進型設置\n"
          +"【 設定溫度: 】設定AI所擁有的情緒 Float: 0~1\n"
          +"【 設定回應長度: 】設定最多能回應的字節 int:0~2048\n"
          +"【 現在數值 】\n"          
          +"並可透過 【AI \{提問內容\}】來進行問答\n"
          )

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/callback",methods=['POST'])
def callback():
  signature = request.headers['X-Line-Signature']
  body = request.get_data(as_text=True)
  try:
      Linebot_Recv_handle.handle(body,signature)
  except InvalidSignatureError:
      abort(400)
  return 'OK'
        
@Linebot_Recv_handle.add(MessageEvent)
def handle_message(event):
  print(event.message)
  message_id=event.message.id
  MsgType=event.message.type
  userId = str(event.source.user_id)
  print('使用者 ID: '+userId)
        
  if(MsgType=="text"):
      mtext=event.message.text
      print('['+message_id+' ***收到文字***]：')
      
      #先檢查是不是設定模式指令
      if mtext=='switch':        
        rtnstr=SwitchSettingMode()
        if(CheckSettingMode()):
          rtnstr=rtnstr+"\n"+str_doc
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
      elif mtext=='switcM':
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=ShowMode()))     

      elif ('使用說明'in mtext) or ('說明'in mtext) :
        rtnstr=str_doc
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))    
      elif ('現在數值'in mtext) or ('設定值'in mtext):
        # https://beta.openai.com/docs/api-reference/completions/create
        rtnstr=str('Model: \t'+str(opaibotPara.model)
        +'\nTemperature: \t'+str(opaibotPara.temperature)
        +'\nMaxtokens: \t'+str(opaibotPara.maxtoken))
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))              
      elif '設定模型' in mtext:
        para = mtext[len('設定模型')+1:]
        opaibotPara.model = para 
        rtnstr='opaibotPara.model: '+str(opaibotPara.model)
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
      elif ('設定溫度'in mtext) or ('設定情緒'in mtext):
        para =  mtext[len('設定溫度')+1:]
        opaibotPara.temperature = float(para)
        rtnstr='opaibotPara.temperature: '+str(opaibotPara.temperature)
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                  
      elif '設定回應長度' in mtext:
        para = mtext[len('設定回應長度')+1:]
        opaibotPara.maxtoken = int(para)
        rtnstr='opaibotPara.maxtoken: '+str(opaibotPara.maxtoken)
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))               
      elif mtext.upper()[0:3]=='AI ':   
        if(CheckSettingMode()==True):
          input_Para = mtext[3:]                 
          response = openai.Completion.create(
          model= opaibotPara.model ,
          prompt=input_Para,
          max_tokens= opaibotPara.maxtoken, 
          temperature= opaibotPara.temperature)
          rtnstr = response.choices[0].text.lstrip()          
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                      
                                            
       
      
def SwitchSettingMode():
  global Mode
  oldMode = Mode
  if(Mode == 'AI Mode'):
    Mode = 'Normal Mode'
  else :
    Mode = 'AI Mode'
  return '模式:'+oldMode+' 更換為:'+Mode
    
def CheckSettingMode():
  global Mode
  if(Mode == 'AI Mode'):
    return True
  else :
    return False
def ShowMode():
  global Mode
  return '現在模式為: '+Mode

print("[Finnish]..........Linebot Flask start!")
if __name__ == '__main__':
  app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)
