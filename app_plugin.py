from flask                import Flask, request, render_template ,abort
from flask_cors           import CORS
from linebot              import LineBotApi, WebhookHandler
from linebot.exceptions   import InvalidSignatureError
from linebot.models       import * #MessageEvent,TextMessage,ImageSendMessage
from datetime import datetime
import MongoDB.FuncMongodb as mongo
import app_utils.app_request as ap
from flasgger             import Swagger
import openai
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from collections import deque
import logging

logger = logging.getLogger("linebotApp")

dt_Access = datetime(2100, 1, 1, 1, 1, 1) #不限制就是 None #限制格式 datetime(2023,3,8,23,42,30) 

def checkAuthorization():
  dt_now = datetime.now()
  st_now = dt_now.strftime("%Y-%m-%d %H:%M:%S %p")
  
  if(dt_now > dt_Access and dt_Access != datetime(0, 0, 0, 0, 0, 0)):
    print("Authorization:Failed")
    os._exit()
  else:
    return True

def loop_checkAuthorization(in_timezone):
  scheduler = BackgroundScheduler(timezone = in_timezone)
  scheduler.add_job(checkAuthorization, 'interval', hours=1)
  scheduler.start()

print("Check Authorization.")
if(checkAuthorization()):
  logger.info ('Authorization:PASS')
  print("Authorization:PASS")
else:
  logger.info ('Authorization:Failed')
  print("Authorization:Failed")
  exit()
loop_checkAuthorization("Asia/Taipei")

print("[Inital][ENV]")
LINEBOT_POST_TOKEN    = os.environ.get('LINEBOT_POST_TOKEN')
LINEBOT_RECV_TOKEN    = os.environ.get('LINEBOT_RECV_TOKEN')
CONNECTSTRING         = os.environ.get('CONNECTSTRING')
TARGET_SERVER_URL     = os.environ.get('TARGET_SERVER_URL')
SERVER_PORT           = os.environ.get('TEAORFISH_SERVER_PORT')
openai.api_key        = os.getenv("OPENAI_API_KEY")
OPENAI_AdminID        = os.environ.get('OPENAI_AdminID')
SSL_PEM               = os.environ.get('SSL_PEM')
SSL_KEY               = os.environ.get('SSL_KEY')
DOCKER_SSL_PEM_Exists = str(os.path.exists("/run/secrets/SSL_PEM") )
DOCKER_SSL_KEY_Exists = str(os.path.exists("/run/secrets/SSL_KEY") )

print(f"ENV:LINEBOT_POST_TOKEN : {LINEBOT_POST_TOKEN}" )
print(f"ENV:TARGET_SERVER_URL  : {TARGET_SERVER_URL}" )
print(f"ENV:LINEBOT_RECV_TOKEN : {LINEBOT_RECV_TOKEN}" )
print(f"ENV:SERVER_PORT        : {SERVER_PORT}" )
print(f"ENV:SECRETS_SSL_PEM    : {DOCKER_SSL_PEM_Exists}")
print(f"ENV:SECRETS_SSL_KEY    : {DOCKER_SSL_KEY_Exists}")
print(f"ENV:SSL_PEM            : {SSL_PEM}")
print(f"ENV:SSL_KEY            : {SSL_KEY}")
print(f"ENV:OPENAI_AdminID     : {OPENAI_AdminID}")

Linebot_Post_handle = LineBotApi(LINEBOT_POST_TOKEN)
Linebot_Recv_handle = WebhookHandler(LINEBOT_RECV_TOKEN)
Mode = 'Normal Mode'
AllowNormalUser = False

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
      

class ChatCompletionsPara: # the prev version completions parameters commit: 915c6a8e481c532438b0af5b68b5ceb6e28258ab
  model = "gpt-3.5-turbo"
  maxtoken = 150

      
print("[Inital][MongoDB]")
mongo.Clientinit()
      
boardlist=['TOP','八卦版','西施版','表特版']
str_docAITalk = f"說明:對談模式。"
str_doc = f"說明:爬蟲相關功能\n\
【八卦版】 最新十篇八卦版標題與連結\n\
【西施版】 最新十篇西施版標題與連結\n\
【表特版】 最新十篇表特版標題與連結\n\
【TOP】   最新十篇股票版標題與連結\n\
【我的ID】 回傳當前使用者UUID\n\
【是否為管理者】回傳當前使用者是否為管理者"

str_docAISetting = f"說明:可使用下列參數對AI進型設置\n\
【 更換模型:】指定使用的AI模型ex.gpt-3.5-turbo \n\
【 回應長度: 】設定最多能回應的字節 int:0~2048\n\
【 現在數值 】【設定值】顯示當前設定\n"


def isEnableAITalk(userID):
  if(isMainUser(userID)==True):
    return True
  else:
    if(isAllowNormalUser()==True):
      return True
    else:
      return False

def isAllowNormalUser():
  global AllowNormalUser
  return AllowNormalUser

def setAllowNormalUser(flg:bool):
  global AllowNormalUser
  AllowNormalUser=flg

def isMainUser(userID):
  if(str(userID) == str(OPENAI_AdminID)):
    return True
  else:
    return False

@app.route("/")
def home():
  logger.info("home started")
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
  logger.info("Line callback started")
  signature = request.headers['X-Line-Signature']
  body = request.get_data(as_text=True)
  try:
      Linebot_Recv_handle.handle(body,signature)
  except InvalidSignatureError as e:
      logger.error(f"InvalidSignatureError: {str(e)}")
      abort(400)
  except ValueError as e:
      logger.error(f"Error Exception: {str(e)}") 
      abort(500)
  except Exception as e:
      logger.error(f"Error Exception: {str(e)}") 
      abort(400)      
  return 'OK'
        
@Linebot_Recv_handle.add(MessageEvent)
def handle_message(event):
  print(event.message)
  message_id = event.message.id
  MsgType = event.message.type
  userId = str(event.source.user_id)
  print(f"使用者 ID: {userId}")
        
  if(MsgType=="text"):
      mtext=event.message.text
      print(f"['{message_id} ***收到文字***]：")      
      # 當使用者正在使用chatGPT且不開放chatGPT時
      if(isAITalkMode() == True and not isEnableAITalk(userId) ):
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='管理者關閉gpt聊天模式中'))
      else:     
        #Check command or not.
        if mtext=='切換' or mtext=='切換模式' or mtext=='SW' or mtext=='switch' :        
          rtnstr=f"{SwitchSettingMode(userId)}\n{ShowDoc()}"
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
        elif mtext=='當前模式' or mtext=='switcM':
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=ShowMode())) 
        # Check 
        elif isEnableAITalk(userId):
          if (isAISettingMode()):
              if ('現在數值' in mtext) or ('設定值' in mtext):
                rtnstr=f"Model: \t{ChatCompletionsPara.model}\nnMaxtokens: \t{ChatCompletionsPara.maxtoken}\nAllowNormalUser: \t{isAllowNormalUser()}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))
              elif '更換模型' in mtext:
                ChatCompletionsPara.model = mtext[len('更換模型')+1:]
                rtnstr=f"opaibotPara.model: {ChatCompletionsPara.model}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
              elif '回應長度' in mtext:
                ChatCompletionsPara.maxtoken = int(mtext[len('回應長度')+1:])
                rtnstr=f"opaibotPara.maxtoken: {ChatCompletionsPara.maxtoken}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))
              elif ('開放設定' in mtext) and isMainUser(userId):
                setAllowNormalUser(not isAllowNormalUser())
                rtnstr=f"AllowNormalUser: {isAllowNormalUser()}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))
          
          #openai TalkMode
          elif (isAITalkMode()):
                response = openai.ChatCompletion.create(
                  model=ChatCompletionsPara.model,
                  messages=[
                    {"role": "system", "content": "You are a helpful assistant. Respond in traditional Chinese when asked in Chinese."},
                    {"role": "user", "content": mtext}
                  ],
                  max_tokens=ChatCompletionsPara.maxtoken
                )       
                rtnstr = response['choices'][0]['message']['content']                    
                set_DialogueCatch(mtext,rtnstr)
                if(rtnstr!=None):
                  mongo.Insert_AIQuestion("Question:"+mtext+"\n Answer:"+rtnstr)
                if(rtnstr==''):
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='...'))
                else:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))
        #every user could use
        if mtext=='使用說明' or mtext=='--help' or mtext=='說明' :
          if(isMainUser(userId)==True):  
              rtnstr=ShowDoc(); 
          else:
              rtnstr=str_doc
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))         
        elif(mtext == '我的ID' or mtext=='我的id'):
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))                   
        elif(mtext == '是否為管理者'):
            if(isMainUser(userId)):                         
              rtnstr = f"是否為管理者: {isMainUser(userId)}\nUser ID:[{userId}]\nACCESS ID:[{OPENAI_AdminID}]"
            else:
              rtnstr = f"是否為管理者: {isMainUser(userId)}"
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                   
        else:#各種開放功能
            if mtext[0:10] == 'testSpace=':
                #Forward ap
                input_APIAndPara = mtext[10:]
                response = ap.requests_GET_Other_api(input_APIAndPara)  
                if type(response) == str:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
                else:                    
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                             
            elif(mtext == '台股行情搜尋說明'):
                responstring = '請輸入股票代號\n ex. 2330'
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=responstring))                                           
            elif mtext == '打招呼':       
              Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='Hi, 你好!'))                                
            elif mtext[0:3].upper() in boardlist:
                boardname=mtext[0:3]
                numbers=mtext[3:5]   
                if numbers=='':
                  numbers=10 #default
                if(boardname == '八卦版' ):
                  input_APIAndPara = f"/Other/Get_Gossiping_TOP_N_Report,{numbers}"
                elif(boardname == '西施版' ):
                  input_APIAndPara = f"/Other/Get_Sex_TOP_N_Report,{numbers}"
                elif(boardname == '表特版' ):
                  input_APIAndPara = f"/Other/Get_Beauty_TOP_N_Report,{numbers}"
                elif(boardname == 'TOP' ):
                  input_APIAndPara = f"/Stock/Get_TOP_N_Report,{numbers}"
                response = ap.requests_GET_api(input_APIAndPara)                  
                if type(response) == str:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
                else:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                                 
            elif( mtext.upper()[0:2] == 'S '      or
                  mtext.upper()[0:6] == 'STOCK:'  or
                  mtext.upper()[0:3] == '股票 '   ):
                stockstr_index = 0
                if(mtext.upper()[0:2] == 'S '):
                  stockstr_index = 2
                elif(mtext.upper()[0:6] == 'STOCK:'):
                  stockstr_index = 6
                elif(mtext.upper()[0:3] == '股票 '):
                  stockstr_index = 3
                input_APIAndPara = f"/Stock/SearchStock,{mtext[stockstr_index:]}"
                response = ap.requests_POST_Stock_api(input_APIAndPara)                    
                if type(response)==str:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response))                 
                else:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=response.text))                 
      
def SwitchSettingMode(userId):
  """ Switch mode

  Args:
      userId (_type_): Auth userID to turn on AI mode

  Returns:
      _type_: _description_
  """
  global Mode
  oldMode = Mode
  if(isEnableAITalk(userId) == True):
    if(Mode == 'AI Mode'):
      Mode = 'Normal Mode'
    elif(Mode == 'Normal Mode'):
      Mode = 'AISetting Mode'
    elif(Mode == 'AISetting Mode'):
        Mode = 'AI Mode'
    else :
      Mode = 'Normal Mode'
    return f"模式:{oldMode} 更換為:{Mode}"
  else:
    return 'Sorry, only main user could use this function now.'

def isNormalMode():
  global Mode
  if(Mode == 'Normal Mode'):
    return True
  else :
    return False

def isAISettingMode():
  global Mode
  if(Mode == 'AISetting Mode'):
    return True
  else :
    return False
  
def isAITalkMode():
  global Mode
  if(Mode == 'AI Mode'):
    return True
  else :
    return False

def getMode():
  global Mode
  return Mode

def ShowMode():
  global Mode
  return '現在模式為: ' << Mode

def ShowDoc():
  if(isAITalkMode()):
    return str_docAITalk
  elif(isAISettingMode()):
    return str_docAISetting
  else:
    return str_doc
    
# region ------ DialogueBuffer ------ 
# change openai.Completion to chatCompletion will not need that.
DialogueBuffer = deque()
Dialogue = {
    'Question': None,
    'Answer': None,
}

def clean_DialogueBuffer():
  """ 對話模式 - 清除緩存區
  """
  global DialogueBuffer
  DialogueBuffer.clear()

def set_DialogueBuffer():
  """ 對話模式 - 將當前對話存入緩存 下次發話就會記錄對話過程
  """
  global Dialogue,DialogueBuffer
  if(Dialogue['Question']!=''):
    DialogueBuffer.append('Q:'+Dialogue['Question']+"\n******")
  DialogueBuffer.append('A:'+Dialogue['Answer']+"\n******")  
  
def get_DialogueBuffer()->str:
  """ 對話模式 - 取得緩存內容 

  Returns:
      str: 緩存內容
  """
  global DialogueBuffer
  rtnstr=""
  
  if(len(DialogueBuffer) == 0):
    return '[empty.]'
  for d in DialogueBuffer:
    rtnstr = rtnstr + d + '\n'
    
  return rtnstr

### DialogueBuffer

### DialogueCatch
def set_DialogueCatch(question:str,answer:str):
  """ 當openai回應token不足表達時使用

  Args:
      question (str): _description_
      answer (str): _description_
  """
  global Dialogue
  if(question!='繼續' and question.lower()!='continue'):
    Dialogue['Question']=question
  else:
    Dialogue['Question']='' #空字串 不能用None
  Dialogue['Answer']=answer
  
def get_DialogueCatch():
  global Dialogue
  return str(Dialogue['Question']) , str(Dialogue['Answer'])

def clean_DialogueCatch():
  global Dialogue
  Dialogue['Question'] = None
  Dialogue['Answer'] = None
### DialogueCatch
# endregion ------ DialogueBuffer ------

print("[Finnish]..........Linebot Flask start!")
if __name__ == '__main__':
  app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)
