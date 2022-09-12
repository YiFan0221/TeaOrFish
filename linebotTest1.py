from flask import Flask, request, render_template ,abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage

import tempfile
from controller import stock_controller, modbus_controller,ssh_controller,tickerOrder_controller

from flasgger import Swagger
from requests import *

#其他後端function
from backend_models.stocksearch import *
from backend_models.picIV       import Pic_Auth
from controller.stock           import *
from controller.tickerOrder     import *
from app_utils.app_result       import requests_api

line_bot_api = LineBotApi('QcRH4+cmpgKeP24rDsHblYBgd0qkifKrgJem7GxmHyXCYLvOdZqsUkLFASyAYhjRAiFkeiY8AYd+aF2fW9Zn1FcUc9QBB4AK7AATm1MVc47orHkod3ZAm8hAOsGOLcoSy1XeyZuk+2fN8Afccu97EwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('976067291be71b6c3e6a3d5c161db416')

 
Mode = 'setting'

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

#registering blueprints
#註冊其他藍圖中的controllers
app.register_blueprint(modbus_controller       , url_prefix='/Modbus')
app.register_blueprint(ssh_controller          , url_prefix='/SSH')
app.register_blueprint(stock_controller        , url_prefix='/Stock')
app.register_blueprint(tickerOrder_controller  , url_prefix='/Ticker')
                            

print("..........Flask start!")


@app.route("/")
def home():
  return render_template("home.html")


# @app.route("/Tradingcall",methods=['POST'])
# def RecvCallInfo():
#   MASTERD = 16771199787211
#   CHANNEL_ACCESS_TOKEN =
# def RecvCallInfo():
  
#     CHANNEL_ACCESS_TOKEN = 'QcRH4+cmpgKeP24rDsHblYBgd0qkifKrgJem7GxmHyXCYLvOdZqsUkLFASyAYhjRAiFkeiY8AYd+aF2fW9Zn1FcUc9QBB4AK7AATm1MVc47orHkod3ZAm8hAOsGOLcoSy1XeyZuk+2fN8Afccu97EwdB04t89/1O/w1cDnyilFU='
#     url = 'https://api.line.me/v2/bot/message/push';
#     json= {
#         'headers': {
#             'Content-Type': 'application/json; charset=UTF-8',
#             'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN,
#         },
#         'method': 'post',
#         'payload': JSON.stringify({
#             'to':  '16771199787211',
#             'messages': [{
#                 type:'text',
#                 text:'哈囉我是 Push Message！'
#             }]
#         }),
#     }



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
      handler.handle(body,signature)
  except InvalidSignatureError:
      abort(400)
  return 'OK'


          

@handler.add(MessageEvent)
def handle_message(event):
  print(event.message)
  message_id=event.message.id
  MsgType=event.message.type
  userId = str(event.source.user_id)
  print('使用者 ID: '+userId)
  if(MsgType=="image"):
      print('[Stepppppppppppppp]['+message_id+' ***收到圖片***]：')        
      message_content = line_bot_api.get_message_content(message_id)
      print('[Stepppppppppppppp]取得檔案') 
      
      img_st="null"
      #本地路徑 本地絕對路徑
      #file_path = os.path.abspath(os.path.dirname(__file__)) + "\\" +message_id+".jpg"      
      #print('[Stepppppppppppppp]準備複製來源檔案:'+file_path)
      #with open(file_path, 'wb') as fd:
      #    for chunk in message_content.iter_content():
      #        fd.write(chunk)
      #img_st=Pic_Auth(file_path)        
      #print('[Stepppppppppppppp]辨識完畢,刪除暫存') 
      
      #生成臨時文件 tempfile.NamedTemporaryFile
      print('[Stepppppppppppppp]準備複製來源檔案:')
      with tempfile.NamedTemporaryFile(suffix='.jpg',delete=False) as tf:
          for chunk in message_content.iter_content():
              tf.write(chunk)
          file_path = tf.name                
      img_st=Pic_Auth(file_path)        
      print('[Stepppppppppppppp]辨識完畢,刪除暫存')     
                                    
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text=img_st))  
        
  elif(MsgType=="text"):
      mtext=event.message.text
      print('['+message_id+' ***收到文字***]：')
      
      #先檢查是不是設定模式
      if mtext=='switch':                
          StateSt =''
          StateSt += ShowMode()
          StateSt += '\n'
          StateSt += SwitchSettingMode()
          StateSt += '\n'
          StateSt += ShowMode()
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text=StateSt))     
      elif mtext=='switcM':
          StateSt =''
          StateSt += ShowMode()
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text=StateSt))     
      elif mtext[0:9]=='testSpace':
          #這邊要呼叫家裡Server的API
          StateSt = requests_api(mtext)                    
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))     
      else: #功能
        if mtext=='aa':
            testresault_st=Func_thsrcOrder()        
            image_message=ImageSendMessage(
                original_content_url=testresault_st[0],
                preview_image_url=testresault_st[0]
            )        
            line_bot_api.reply_message(event.reply_token,image_message)
        elif mtext=='TOP':        
            st=Get_TOP_N_Report(10)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))
        elif mtext=='TOP20':        
            st=Get_TOP_N_Report(20)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))
        elif mtext=='外資比排行' or mtext=='FT':        
            st=Get_TopRate("外資")
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))
        elif mtext=='投資比排行' or mtext=='TT':        
            st=Get_TopRate("投信")
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))
        elif mtext=='自資比排行' or mtext=='ST':        
            st=Get_TopRate("自營商")
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))        
        elif mtext=='0806449' or mtext=='9527':        
            if mtext=='0806449':
                st='崊盃喝尿簌簌叫'
            elif mtext=='23965088':
                st='先生要報統編嗎?'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))     
        elif(mtext.isdigit() and len(mtext)>=4):
            st =Get_SearchStock(mtext)        
            line_bot_api.reply_message(event.reply_token,TextSendMessage( text = st ))     
        elif(mtext=='我的ID' or mtext=='我的id'):
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))     
            
def SwitchSettingMode():
  global Mode
  if(Mode == 'setting'):
    Mode = 'normal'
  else :
    Mode = 'setting'
  return '更換為'+Mode
    
def CheckSettingMode():
  global Mode
  if(Mode == 'setting'):
    return True
  else :
    return False
def ShowMode():
  global Mode
  return '現在模式為: '+Mode

      
if __name__ == '__main__':
  #app.run(ssl_context=('YiFanServer.crt', 'YiFanServer.key'),host="0.0.0.0", port=4000 , threaded=True)
  app.run(host="0.0.0.0", port=4000 , threaded=True)
#添加SSL
#https://medium.com/@charming_rust_oyster_221/flask-%E9%85%8D%E7%BD%AE-https-%E7%B6%B2%E7%AB%99-ssl-%E5%AE%89%E5%85%A8%E8%AA%8D%E8%AD%89-36dfeb609fa8
#產生KEY
#https://blog.miniasp.com/post/2019/02/25/Creating-Self-signed-Certificate-using-OpenSSL
#取得授承認的SSL
#https://certbot.eff.org/instructions?ws=other&os=ubuntufocal
#如何在 VSCode 設定完整的 .NET Core 建置、發行與部署工作 看第四點
#https://blog.miniasp.com/post/2019/01/22/Configure-Tasks-and-Launch-in-VSCode-for-NET-Core