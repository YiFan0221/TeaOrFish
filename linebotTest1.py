from flask import Flask, request, abort ,render_template
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage
import os
import tempfile
from controller import Modbus_controller ,SSH_controller        ,Stock_controller      ,TickerOrder_controller




from flasgger import Swagger


#其他後端function
from StockSearch  import Func_SearchStock_cnyes ,Func_PTTStock_TopN ,Func_TopRate
from TickerOrder  import Func_thsrcOrder
from picIV        import Pic_Auth

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
app.register_blueprint(Modbus_controller       , url_prefix='/MODBUS')
app.register_blueprint(SSH_controller          , url_prefix='/SSH')
app.register_blueprint(Stock_controller        , url_prefix='/STOCK')
app.register_blueprint(TickerOrder_controller  , url_prefix='/Ticker')
                            

print("..........Flask start!")


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
      handler.handle(body,signature)
  except InvalidSignatureError:
      abort(400)
  return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
  print(event.message)
  message_id=event.message.id
  MsgType=event.message.type
    
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
          global Mode
          if(Mode == 'setting'):
            Mode = 'normal'
          else :
            Mode = 'setting'
          st = '現在模式為: '+Mode
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))     
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

          
        
def Get_TopRate(mode):
  num = 10
  m_data =Func_TopRate(num,mode)
  if(type(m_data)== str):
      rtn_text =m_data    
  else:
      st=mode+'資本佔比五日排行\n排序\t名稱(代號)\t當日\t2日\t3日\t5日'+'\n'
      for num in range(1,len(m_data), 1):
          st = st+ m_data.get(str(num))+'\n'
      rtn_text=st    
  return rtn_text
    
@app.route("/SearchStock",methods=['GET'])
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
def Get_TOP_N_Report(num):
  if(num>20 or num<=0):
      return "超出上限(20筆)囉"
  st='TOP前'+str(num)+'\n'        
  m_data =Func_PTTStock_TopN()                
  print("Data len:"+str(len(m_data))) 
  for i in range(0,num+3,1):
      data=m_data.pop()
      #濾掉置頂文章,將列表加入列表
      if i>=3:
          st += str(i-2)+':['+data['rate']+'] '+data['title']+' '+data['url']+'\n'            
  print(st)    
  return st
       
if __name__ == '__main__':
  #app.run(ssl_context=('server.crt', 'server.key'),host="0.0.0.0", port=4000 , threaded=True)
  app.run(host="0.0.0.0", port=4000 , threaded=True)
#添加SSL
#https://medium.com/@charming_rust_oyster_221/flask-%E9%85%8D%E7%BD%AE-https-%E7%B6%B2%E7%AB%99-ssl-%E5%AE%89%E5%85%A8%E8%AA%8D%E8%AD%89-36dfeb609fa8
#產生KEY
#https://blog.miniasp.com/post/2019/02/25/Creating-Self-signed-Certificate-using-OpenSSL
#取得授承認的SSL
#https://certbot.eff.org/instructions?ws=other&os=ubuntufocal
#如何在 VSCode 設定完整的 .NET Core 建置、發行與部署工作 看第四點
#https://blog.miniasp.com/post/2019/01/22/Configure-Tasks-and-Launch-in-VSCode-for-NET-Core