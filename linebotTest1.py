from flask import Flask, request, render_template ,abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage
import os
import tempfile
from flasgger import Swagger

#其他後端function
#from backend_models.picIV       import Pic_Auth
from app_utils.app_result       import requests_POST_Stock_api,requests_GET_Stock_api

LINEBOT_POST_TOKEN = os.environ.get('LINEBOT_POST_TOKEN')
LINEBOT_RECV_TOKEN = os.environ.get('LINEBOT_RECV_TOKEN')


Linebot_Post_handle = LineBotApi(LINEBOT_POST_TOKEN)
Linebot_Recv_handle = WebhookHandler(LINEBOT_RECV_TOKEN)

 
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
                          
print("..........Linebot Flask start!")

@app.route("/")
def home():
  return render_template("home.html")

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
  if(MsgType=="image"):
      print('[Stepppppppppppppp]['+message_id+' ***收到圖片***]：')        
      message_content = Linebot_Post_handle.get_message_content(message_id)
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
                                    
      Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=img_st))  
        
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
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt))     
      elif mtext=='switcM':
          StateSt =''
          StateSt += ShowMode()
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt))     
      elif mtext[0:9]=='testSpace':
          #這邊要呼叫家裡Server的API
          input_APIAndPara = mtext[9:]
          StateSt = requests_POST_Stock_api(input_APIAndPara)                    
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))     
      else: #功能
        if mtext=='aa':
            testresault_st=Func_thsrcOrder()        
            image_message=ImageSendMessage(
                original_content_url=testresault_st[0],
                preview_image_url=testresault_st[0]
            )        
            Linebot_Post_handle.reply_message(event.reply_token,image_message)
        elif mtext=='TOP':       
            input_APIAndPara = '/Get_TOP_N_Report,10'
            StateSt = requests_GET_Stock_api(input_APIAndPara)                    
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))     
        elif mtext=='TOP20':    
            input_APIAndPara = '/Get_TOP_N_Report,20'
            StateSt = requests_GET_Stock_api(input_APIAndPara)                    
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))                  
        elif mtext=='0806449' or mtext=='9527':        
            if mtext=='0806449':
                st='崊盃喝尿簌簌叫'
            elif mtext=='23965088':
                st='先生要報統編嗎?'
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=st))     
        elif(mtext.isdigit() and len(mtext)>=4):
            input_APIAndPara = '/SearchStock,'+str(mtext)
            StateSt = requests_GET_Stock_api(input_APIAndPara)                    
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=StateSt.text))                
        elif(mtext=='我的ID' or mtext=='我的id'):
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))     
            
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

import ssl
context = ssl.SSLContext()
context.load_cert_chain('yfnoip_ddns_net.pem-chain', 'YiFanServer.key')
      
if __name__ == '__main__':
  #測試用 記得開ngrok
  app.run(ssl_context=context,host="0.0.0.0", port=4000 , threaded=True)
  #上傳Heroku用
  #app.run(host="0.0.0.0", port=4000 , threaded=True)
#添加SSL
#https://medium.com/@charming_rust_oyster_221/flask-%E9%85%8D%E7%BD%AE-https-%E7%B6%B2%E7%AB%99-ssl-%E5%AE%89%E5%85%A8%E8%AA%8D%E8%AD%89-36dfeb609fa8
#產生KEY
#https://blog.miniasp.com/post/2019/02/25/Creating-Self-signed-Certificate-using-OpenSSL
#取得授承認的SSL
#https://certbot.eff.org/instructions?ws=other&os=ubuntufocal
#如何在 VSCode 設定完整的 .NET Core 建置、發行與部署工作 看第四點
#https://blog.miniasp.com/post/2019/01/22/Configure-Tasks-and-Launch-in-VSCode-for-NET-Core
#[SSL 基礎]私有金鑰、CSR 、CRT 與 中繼憑證
# https://haway.30cm.gg/ssl-key-csr-crt-pem/