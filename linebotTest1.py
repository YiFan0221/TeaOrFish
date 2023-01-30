from flask import Flask, request, render_template ,abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage
from MongoDB.FuncMongodb        import *
import os
import tempfile
from flasgger import Swagger
import openai
#其他後端function
# from backend_models.picIV       import Pic_Auth
from app_utils.app_result       import requests_POST_Stock_api,requests_GET_Stock_api,requests_GET_Other_api,requests_POST_Other_api

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
      

class opaibotPara:
  model = "text-davinci-003"
  temperature = 0.0
  maxtoken = 200
      
print("[Inital][MongoDB]")
Clientinit()
      
str_doc = str(
          "說明:可使用下列參數對AI進型設置\n"
          # +"【 設定模型:】指定使用的AI模型ex.text-davinci-003 \n"
          +"【 設定溫度: 】設定AI所擁有的情緒 Float: 0~1\n"
          +"【 設定回應長度: 】設定最多能回應的字節 int:0~2048\n"
          +"【 現在數值 】\n"          
          +"並可透過 【AI \{提問內容\}】來進行問答\n"
          +"爬蟲相關功能:\n"
          +"【八卦版】 回傳最新十篇八卦版標題與連結\n"
          +"【西施版】 回傳最新十篇西施版標題與連結\n"
          +"【表特版】 回傳最新十篇表特版標題與連結\n"
          +"【TOP】   回傳最新十篇股票版標題與連結\n"
          +"【s /{2330或股票代號/}】回傳即時傳回的股票行情價格\n"
          )

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
      
      #先檢查是不是設定模式指令
      if mtext=='switch':        
        rtnstr=SwitchSettingMode()
        if(CheckSettingMode()):
          rtnstr=rtnstr+"\n"+str_doc
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
      elif mtext=='switcM':
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=ShowMode()))     

      elif ('使用說明' or '說明') in mtext:
        rtnstr=str_doc
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))    
      elif ('使用說明' or '設定值') in mtext:
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
      elif ('設定溫度' or '情緒設定') in mtext:
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
          if(rtnstr!=None):
            Insert_AIQuestion("Question:"+input_Para+"\n Answer:"+rtnstr)
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                      
                                    
         
      #功能型函式   
      elif mtext[0:10]=='testSpace=':
          #這邊要呼叫家裡Server的API
          input_APIAndPara = mtext[10:]
          response = requests_GET_Other_api(input_APIAndPara)  
          if type(response)==str:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
          else:                    
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                             
      elif(mtext=='台股行情搜尋說明'):
          responstring = '請輸入股票代號\n ex. 2330'
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=responstring))                   
      elif(mtext=='我的ID' or mtext=='我的id'):
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))                   
      elif mtext=='打招呼':       
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='Hi, 你好!'))                   
      elif(mtext=='八卦版' or mtext=='西施版' or mtext=='表特版'):        
          input_APIAndPara=""         
          if(mtext=='八卦版' ):
            input_APIAndPara = '/Get_Gossiping_TOP_N_Report,10'
          elif(mtext=='西施版' ):
            input_APIAndPara = '/Get_Sex_TOP_N_Report,10'
          elif(mtext=='表特版' ):
            input_APIAndPara = '/Get_Beauty_TOP_N_Report,10'            
          response = requests_GET_Other_api(input_APIAndPara)                                
          if type(response)==str:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
          else:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                   
      elif mtext=='TOP':       
          input_APIAndPara = '/Get_TOP_N_Report,10'
          response = requests_GET_Stock_api(input_APIAndPara)                    
          if type(response)==str:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
          else:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                 
      elif mtext=='TOP20':    
          input_APIAndPara = '/Get_TOP_N_Report,20'
          response = requests_GET_Stock_api(input_APIAndPara)                    
          if type(response)==str:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
          else:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                 
      elif( mtext.upper()[0:2]=='S 'or
            mtext.upper()[0:6]=='STOCK:' or
            mtext.upper()[0:3]=='股票 '            
          ):
          stockstr_index=0
          if(mtext.upper()[0:2]=='S '):
            stockstr_index = 2
          elif(mtext.upper()[0:6]=='STOCK:'):
            stockstr_index = 6
          elif(mtext.upper()[0:3]=='股票 '):
            stockstr_index = 3
          input_APIAndPara = '/SearchStock,'+str(mtext[stockstr_index:])
          response = requests_POST_Stock_api(input_APIAndPara)                    
          if type(response)==str:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
          else:
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                 
    
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