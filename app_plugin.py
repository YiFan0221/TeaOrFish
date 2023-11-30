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
dt_Access = datetime(2100, 1, 1, 1, 1, 1) #不限制就是 None #限制格式 datetime(2023,3,8,23,42,30) 

def checkAuthorization():
  dt_now = datetime.now()
  st_now = dt_now.strftime("%Y-%m-%d %H:%M:%S %p")
  
  if(dt_now > dt_Access and dt_Access != datetime(0, 0, 0, 0, 0, 0)):
    print("Authorization:Failed")
    os._exit()
  else:
    return True

def loop_checkAuthorization():
  scheduler = BackgroundScheduler(timezone = "Asia/Taipei")
  scheduler.add_job(checkAuthorization, 'interval', hours=1)
  scheduler.start()

print("Check Authorization.")
if(checkAuthorization()):
  print("Authorization:PASS")
loop_checkAuthorization()

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
  top_p = 1
  n = 1
  stream = False
  stop = ["******"]
  presence_penalty = 0 
  frequency_penalty = 0
  logit_bias = None
  
      
print("[Inital][MongoDB]")
mongo.Clientinit()
      
boardlist=['TOP','八卦版','西施版','表特版']
str_docAITalk = f"說明:對談模式。"
str_doc = f"說明:爬蟲相關功能\n\
【八卦版】 回傳最新十篇八卦版標題與連結\n\
【西施版】 回傳最新十篇西施版標題與連結\n\
【表特版】 回傳最新十篇表特版標題與連結\n\
【TOP】   回傳最新十篇股票版標題與連結\n\
【s {{2330或股票代號}}】回傳即時傳回的股票行情價格\n"
str_docAISetting = f"說明:可使用下列參數對AI進型設置\n\
【 設定模型:】指定使用的AI模型ex.text-davinci-003 \n\
【 設定溫度: 】設定AI所擁有的情緒 Float: 0~1\n\
【 設定回應長度: 】設定最多能回應的字節 int:0~2048\n\
【 現在數值 】\n\
並可透過 【AI {{提問內容}}】來進行問答\n"          


DialogueBuffer = deque()
Dialogue = {
    'Question': None,
    'Answer': None,
}

def isMainUser(userID):
  if(str(userID) == str(OPENAI_AdminID)):
    return True
  else:
    return False

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
  message_id = event.message.id
  MsgType = event.message.type
  userId = str(event.source.user_id)
  print(f"使用者 ID: {userId}")
        
  if(MsgType=="text"):
      mtext=event.message.text
      print(f"['{message_id} ***收到文字***]：")      
      if(isAITalkMode == True and not isMainUser(userId) ):
        Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='目前尚未開放中'))
      else:
     
        
        #Only for main user
        if isMainUser(userId) == True:
          #Check command or not.
          if mtext=='切換模式' or mtext=='sssw' or mtext=='switch' :        
            rtnstr=f"{SwitchSettingMode(userId)}\n{ShowDoc()}"
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
          elif mtext=='當前模式' or mtext=='switcM':
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=ShowMode()))  
          elif isAISettingMode() == True:
              if ('現在數值' in mtext) or ('設定值' in mtext):
                # https://beta.openai.com/docs/api-reference/completions/create
                rtnstr=f"Model: \t{opaibotPara.model}\nTemperature: \t {opaibotPara.temperature}\nnMaxtokens: \t{opaibotPara.maxtoken}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))              
              elif '設定模型' in mtext:
                opaibotPara.model = mtext[len('設定模型')+1:]
                rtnstr=f"opaibotPara.model: {opaibotPara.model}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))     
              elif ('設定溫度' in mtext) or ('設定情緒' in mtext):
                opaibotPara.temperature = float(mtext[len('設定溫度')+1:])
                rtnstr=f"opaibotPara.temperature: {opaibotPara.temperature}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                  
              elif '設定回應長度' in mtext:
                opaibotPara.maxtoken = int(mtext[len('設定回應長度')+1:])
                rtnstr=f"opaibotPara.maxtoken: {opaibotPara.maxtoken}"
                Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))               
          #openai TalkMode
          elif isAITalkMode() == True:
              if(len(mtext) == 3): #shortcut key words
                if(mtext == 'mmk' or mtext == 'mkr'):
                  set_DialogueBuffer()
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='reg.'))                        
                elif(mtext == 'clr'):
                  clean_DialogueBuffer()
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='[clean buffer]'))                      
                elif(mtext == 'shw'):
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=get_DialogueBuffer()))                      
              else:
                clean_DialogueCatch()            
                sendstr = get_DialogueBuffer()+mtext
                response = openai.Completion.create(
                  model=opaibotPara.model ,
                  prompt=sendstr,
                  max_tokens=opaibotPara.maxtoken, 
                  temperature=opaibotPara.temperature,
                  stop=opaibotPara.stop)                
                rtnstr = response.choices[0].text.lstrip()                          
                set_DialogueCatch(mtext,rtnstr)
                if(rtnstr!=None):
                  mongo.Insert_AIQuestion("Question:"+mtext+"\n Answer:"+rtnstr)
                if(rtnstr==''):
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='...'))                      
                else:
                  Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))                      
        #every user
           
        if mtext=='使用說明' or mtext=='--help' or mtext=='說明' :
          if(isMainUser(userId)==True):  
              rtnstr=ShowDoc(); 
          else:
              rtnstr=str_doc
          Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text=rtnstr))         
        elif(mtext == '我的ID' or mtext=='我的id'):
            Linebot_Post_handle.reply_message(event.reply_token,TextSendMessage(text='當前傳訊息帳號的id為:'+userId))                   
        elif(mtext == '是否為主使用者'):
            if(isMainUser(userId)):                         
              rtnstr = f"是否為管理者:{isMainUser(userId)}\nuserid:[{userId}]\nenv:[{OPENAI_AdminID}]"
            else:
              rtnstr = f"是否為管理者:{isMainUser(userId)}"
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

### DialogueBuffer
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

      
def SwitchSettingMode(userId):
  """ Switch mode

  Args:
      userId (_type_): Auth userID to turn on AI mode

  Returns:
      _type_: _description_
  """
  global Mode
  oldMode = Mode
  if(isMainUser(userId) == True):
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
    return 'Sorry, only main user could use this function.'

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
    

print("[Finnish]..........Linebot Flask start!")
if __name__ == '__main__':
  app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)
