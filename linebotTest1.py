from flask import Flask, request, render_template ,abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage
import os
import tempfile
from flasgger import Swagger

#其他後端function
# from backend_models.picIV       import Pic_Auth
from app_utils.app_result       import requests_POST_Stock_api,requests_GET_Stock_api

print("[Inital][ENV]")
LINEBOT_POST_TOKEN  = os.environ.get('LINEBOT_POST_TOKEN')
LINEBOT_RECV_TOKEN  = os.environ.get('LINEBOT_RECV_TOKEN')
TARGET_SERVER_URL   = os.environ.get('TARGET_SERVER_URL')
SSL_PEM             = os.environ.get('SSL_PEM')
SSL_KEY             = os.environ.get('SSL_KEY')
SERVER_PORT         = os.environ.get('TEAORFISH_SERVER_PORT')

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
Mode = 'setting'

print("[Inital][Swagger]")
app = Flask(__name__)
app.config['SWAGGER'] = {
    "title": "TeaOrFish",
    "description": "Flasgger by TeaOrFish,stockSearch in Linebot",
    "version": "1.0.2",
    "termsOfService": "",
    "hide_top_bar": True
}
CORS(app)
Swagger(app)

print("[Inital][SSL]")                          

import ssl
context = ssl.SSLContext()
context.load_cert_chain(SSL_PEM,SSL_KEY)
      
@app.route("/")
def home():
  return render_template("home.html")

@app.route("/.well-known/acme-challenge/fKno72R1QH41oxIYC_FWMbivpvGQe0GIZRTUG0VWafs")
def forcetbot():
  return render_template("cerbot.html")

@app.route("/callback",methods=['POST'])
def callback():
  """
    接收到LINE發過來的資訊
    ---
    tags:
      - Linebot
    description:
      接收到LINE發過來的資訊,並藉此放到@handle中做處理
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
      
      #先檢查是不是設定模式
      if mtext=='switch':                
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=SwitchSettingMode()))     
      elif mtext=='switcM':
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=ShowMode()))     
      elif mtext[0:9]=='testSpace':
          #這邊要呼叫家裡Server的API
          input_APIAndPara = mtext[9:]
          StateSt = requests_POST_Stock_api(input_APIAndPara)                    
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))     
      else: #功能
        if(mtext=='台股行情搜尋說明'):
            responstring = '請輸入股票代號\n ex. 2330'
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=responstring))                   
        elif(mtext=='我的ID' or mtext=='我的id'):
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))                   
        elif mtext=='打招呼':       
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='Hi, 你好!'))                   
        elif mtext=='TOP':       
            input_APIAndPara = '/Get_TOP_N_Report,10'
            StateSt = requests_GET_Stock_api(input_APIAndPara)                    
            if type(StateSt)==str:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt))                 
            else:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))                 
        elif mtext=='TOP20':    
            input_APIAndPara = '/Get_TOP_N_Report,20'
            StateSt = requests_GET_Stock_api(input_APIAndPara)                    
            if type(StateSt)==str:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt))                 
            else:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))                 
        elif(mtext.isdigit() and len(mtext)>=4):
            input_APIAndPara = '/SearchStock,'+str(mtext)
            StateSt = requests_POST_Stock_api(input_APIAndPara)                    
            if type(StateSt)==str:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt))                 
            else:
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))                 
  
  # elif(MsgType=="image"):      #CI效能問題，暫時移除OCR功能增加build速度
  #   if(Mode == 'vision'):    
  #     print('[Step]['+message_id+' ***收到圖片***]：')        
  #     message_content = Linebot_Post_handle.get_message_content(message_id)                    
  #     img_st="尚未辨識"      
  #     with tempfile.NamedTemporaryFile(suffix='.jpg',delete=False) as tf:
  #       for chunk in message_content.iter_content():
  #           tf.write(chunk)              
  #       file_path = tf.name                
  #     img_st=Pic_Auth(file_path)        
  #     print('[Step]辨識完畢,刪除暫存')     
  #     tf.close()                                
  #     os.unlink(tf.name)    
  #     Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=img_st))        
      
def SwitchSettingMode():
  global Mode
  oldMode = Mode
  if(Mode == 'vision'):
    Mode = 'normal'
  else :
    Mode = 'vision'
  return '模式:'+oldMode+' 更換為:'+Mode
    
def CheckSettingMode():
  global Mode
  if(Mode == 'setting'):
    return True
  else :
    return False
def ShowMode():
  global Mode
  return '現在模式為: '+Mode

print("[Finnish]..........Linebot Flask start!")
if __name__ == '__main__':
  app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)