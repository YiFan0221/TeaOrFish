import multiprocessing
import os
import time
from functools import partial
import queue
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rs = requests.session()

from backend_models.picIV import Pic_Auth
#Cookie
cookie='''XSRF-TOKEN=eyJpdiI6ImQ4S2pidDVIY3prbWdPRHVvY01RQmc9PSIsInZhbHVlIjoiR1ROckx2bnNmbEJwanNWQ1FKQldEXC8ydU5NQ2tCa25lWW1cL1RTMzBtVERmcUl2bERiaFRrZFNDbTNNK1A0UWN5IiwibWFjIjoiMTVhNDI2MTRmNTc4ZGM5MWZlZDAzODI3OGQyZDAzZTAzNGE2YTYwYjQ1OTI4Yjk0NTM1NGEzM2U5ODNkZGY0OSJ9; jvid_prod_session=gXIHtW1oTiDEuq0iX4RxmoFiheKqoD3TU8WBFw3F; __auc=1a77c905179cd8c88d30046a28a; _ga=GA1.2.1615784831.1622651210; _gid=GA1.2.1126861238.1622651210; _ga_Q4XDSLQE2E=GS1.1.1622651209.1.0.1622651212.0'''    
#Header
#我電腦的
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36','Cookie': cookie}
#範例的
#headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
#"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}


def Func_thsrcOrder():
    print('進入函式:Func_thsrcOrder') 
    link = "https://irs.thsrc.com.tw/IMINT/?locale=tw" 
    res_Page = rs.get(link,headers=header, timeout = 10,verify=False)  
    #例外資訊： socket.timeout: The read operation timed out                  
    soup = BeautifulSoup(res_Page.text, 'html.parser')
    
    #print(soup) 
    #例外情形 返回無資料
    m_error = [tag.text for tag in soup.find_all("div", class_="jsx-3008000365")]
    if(soup.title.string== '404' or str(m_error)!='[]'):
        rtn = '找不到相關資訊歐~'
        print(rtn)
        return rtn  

    #先取得驗證碼URL
    img = soup.find_all('img',id="BookingS1Form_homeCaptcha_passCode")   
    src=img[0].get('src')
    print('src:'+'https://irs.thsrc.com.tw/'+src)
    #將驗證碼圖片下載(可製作成函式)
    #將驗證碼丟進辨識函式(可製作成函式)
    #將辨識結果與其他參數一同送出
    
    picurl = 'https://irs.thsrc.com.tw/'+src        
    response=requests.get(picurl,headers=header,verify=False)    
    print(response.content)
    rtn_st=Pic_Auth(response.content)
    
    print('辨識結果'+rtn_st)
    print('離開函式:Func_thsrcOrder' ) 
    rtn_List=[picurl,rtn_st]
    return rtn_List
