from flask import Flask
from numpy.lib.function_base import _cov_dispatcher
app = Flask(__name__)

print("..........Flask start!")
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * #MessageEvent,TextMessage,ImageSendMessage
from flask import render_template
import os
import tempfile

#其他後端function
from StockSearch import Func_SearchStock_wantgoo
from StockSearch import Func_SearchStock_cnyes
from StockSearch import Func_PTTStock_TopN
from StockSearch import Func_TopRate
from TickerOrder import Func_thsrcOrder
from picIV import Pic_Auth

line_bot_api = LineBotApi('QcRH4+cmpgKeP24rDsHblYBgd0qkifKrgJem7GxmHyXCYLvOdZqsUkLFASyAYhjRAiFkeiY8AYd+aF2fW9Zn1FcUc9QBB4AK7AATm1MVc47orHkod3ZAm8hAOsGOLcoSy1XeyZuk+2fN8Afccu97EwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('976067291be71b6c3e6a3d5c161db416')

#test Area
#Func_TopRate(20)
#test Area
@app.route("/")
def home():
    return render_template("home.html")
    
# 接收到LINE發過來的資訊
@app.route("/callback",methods=['POST'])
def callback():
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
    
    
def Get_SearchStock(mtext):
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
    app.run(host="0.0.0.0", port=3000)


