from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage

#其他後端function
from StockSearch import Func_SearchStock
from StockSearch import Func_PTTStock_TopN

line_bot_api = LineBotApi('QcRH4+cmpgKeP24rDsHblYBgd0qkifKrgJem7GxmHyXCYLvOdZqsUkLFASyAYhjRAiFkeiY8AYd+aF2fW9Zn1FcUc9QBB4AK7AATm1MVc47orHkod3ZAm8hAOsGOLcoSy1XeyZuk+2fN8Afccu97EwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('976067291be71b6c3e6a3d5c161db416')

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
@handler.add(MessageEvent,message=TextMessage)

#鸚鵡
#def handle_message(event):
#    line_bot_api.reply_message(event.reply_token,
#        TextSendMessage(text=event.message.text))
def handle_message(event):
    mtext=event.message.text
    if(type(mtext)==str):
        print('[***收到命令***]：'+mtext)
    if mtext=='股票':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='接收到股票資訊'))
    elif mtext=='TOP':
        m_data =Func_PTTStock_TopN()        
        st='TOP前10'+'\n'
        print("Data len:"+str(len(m_data))) 

        for i in range(0,13,1):
            data=m_data.pop()
            if i>=3:
                st += str(i-2)+':['+data['rate']+'] '+data['title']+' '+data['url']+'\n'            
        print(st)        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=st))
    else:
        m_data =Func_SearchStock(mtext)
        if(type(m_data)== str):
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=m_data))
        else:
            StockInfo = TextSendMessage( text =
            '股票名稱:'+m_data.get('股票名稱')+' ('+m_data.get('股票編號')+')\n'+
            '股票編號:'+m_data.get('股票現價')+'\n'+                         
            '漲跌:'+m_data.get('漲跌')+' ('+m_data.get('漲跌幅')+')\n'     
            '本益比:'+m_data.get('本益比')+'\n'+     
            '本淨比:'+m_data.get('本淨比')     
            )
            line_bot_api.reply_message(event.reply_token,StockInfo)
    
       
if __name__ == '__main__':
    app.run()


