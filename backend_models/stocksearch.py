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

#Cookie
cookie='''XSRF-TOKEN=eyJpdiI6ImQ4S2pidDVIY3prbWdPRHVvY01RQmc9PSIsInZhbHVlIjoiR1ROckx2bnNmbEJwanNWQ1FKQldEXC8ydU5NQ2tCa25lWW1cL1RTMzBtVERmcUl2bERiaFRrZFNDbTNNK1A0UWN5IiwibWFjIjoiMTVhNDI2MTRmNTc4ZGM5MWZlZDAzODI3OGQyZDAzZTAzNGE2YTYwYjQ1OTI4Yjk0NTM1NGEzM2U5ODNkZGY0OSJ9; jvid_prod_session=gXIHtW1oTiDEuq0iX4RxmoFiheKqoD3TU8WBFw3F; __auc=1a77c905179cd8c88d30046a28a; _ga=GA1.2.1615784831.1622651210; _gid=GA1.2.1126861238.1622651210; _ga_Q4XDSLQE2E=GS1.1.1622651209.1.0.1622651212.0'''    
#Header
#我電腦的
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36','Cookie': cookie}
#範例的
#headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
#"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}

def Func_Echo(mtext):
    return mtext

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
  
  
def Func_PTTStock_TopN():
    print('進入函式:Func_PTTStock_TopN') 
    link = "https://www.ptt.cc/bbs/Stock/index.html" 
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
    
    index_list = []
    
    article_list = []
    
    board = 'Stock'
    all_page_url = soup.select('.btn.wide')[1]['href']
    End_page = get_page_number(all_page_url)
    #print(End_page)  
    #取預計找尋的頁數
    for page in range(End_page-1, End_page+1, 1):        
        page_url = 'https://www.ptt.cc/bbs/{}/index{}.html'.format(board, page)
        #print('URL:'+page_url)
        index_list.append(page_url)        

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)        
        res = rs.get(index,headers=header, timeout = 10, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            #塞回去再來一次
            index_list.append(index)
            time.sleep(1)
        else:
            article_list.extend(craw_page(res))#往後加入列表
        time.sleep(0.05)

    total = len(article_list)

    print('離開函式:Func_PTTStock_TopN 數量:'+str(total)) 
    return article_list

#取得當前所有頁數
def get_page_number(content):
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1
#傳入資料網址 取出標題與連結
def craw_page(res):
    print('進入函式:craw_page')
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            #print('1') 
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                #print('2') 
                rate = r_ent.find(class_="nrec").text
                title = r_ent.find(class_="title").text.strip()                
                url = 'https://www.ptt.cc' + link
                #print('3') 
                print(rate+title)
                article_seq.append({
                    'title': title,
                    'url': url,
                    'rate': rate,
                })
                #print('4') 
        except Exception as e:
            # print('crawPage function error:',r_ent.find(class_="title").text.strip())
            print(e)
    print('離開函式:craw_page')           
    return article_seq
    


def Func_SearchStock_cnyes(StockNum):
    print('進入函式:Func_SearchStock') 
    numstring = str(StockNum)
    link = "https://invest.cnyes.com/twstock/TWS/"+numstring+"/" 
    res_Page = rs.get(link,headers=header, timeout = 10,verify=False)  
    #PS.例外資訊： socket.timeout: The read operation timed out                  
    soup = BeautifulSoup(res_Page.text, 'html.parser')
    
    #例外情形 返回無資料
    m_error = [tag.text for tag in soup.find_all("div", class_="jsx-3008000365")]
    if(soup.title.string== '404' or str(m_error)!='[]'):
        rtn = '找不到相關資訊歐~'
        print(rtn)        
        return rtn

    m_key=[]
    m_Value=[]
    
    #股票編號 
    m_ID = StockNum   
    m_key.append('股票編號')
    m_Value.append(m_ID)
    print("股票編號:"+str(m_ID[0]) )

    #名稱 #jsx-37573986 header_second 也可以
    m_Name = [tag.text for tag in soup.find_all("div", {"class": "jsx-2715122309 main_subTitle"})]
    m_key.append('股票名稱')
    m_Value.append(m_Name[0])
    print("股票名稱:"+m_Name[0])     
    
    #現價
    m_Price = [tag.text for tag in soup.find_all("div", {"class": "jsx-2214436525 info-lp"})]
    m_key.append('股票現價')
    m_Value.append(m_Price[0])
    print("股票現價:"+str(m_Price[0]))       

    #漲跌
    m_UpDown = [tag.text for tag in soup.find_all("div", {"class": "jsx-2214436525 change-net"})]
    m_key.append('漲跌')
    m_Value.append(m_UpDown[0])
    print("漲跌:"+str(m_UpDown[0]))  
    
    #漲跌幅
    m_UpDownPercent = [tag.text for tag in soup.find_all("div", {"class": "jsx-2214436525 change-percent"})]
    m_key.append('漲跌幅')
    m_Value.append(m_UpDownPercent[0])
    print("漲跌幅:"+str(m_UpDownPercent[0]))  
            
    for tag in soup.find_all("div", {"class": "jsx-3874884103 jsx-1763002358 data-block"}):
        Name = [val.text for val in tag.find_all("div", {"class": "jsx-3874884103 jsx-1763002358 block-title"})]
        m_key.append(Name[0])         
        value = [val.text for val in tag.find_all("div", {"class": "jsx-3874884103 jsx-1763002358 block-value block-value--"})]
        if str(value) == "[]":
            value2 = [val.text for val in tag.find_all("div", {"class": "jsx-3874884103 jsx-1763002358 block-value block-value-- block-value--small"})]
            m_Value.append(value2[0])        
        else:
            m_Value.append(value[0])  
    #轉換看這篇:
    #https://blog.csdn.net/loner_fang/article/details/80940600    
    m_data_zip=[]
    m_data_zip = zip(m_key,m_Value)
    m_data_dict = dict(m_data_zip)
    print("其他資訊:"+str(m_data_dict))
    print('離開函式:Func_SearchStock')   
    return m_data_dict
   
   
def Func_TopRate(TopNum,mode): #TopNum:int
    print('進入函式:Func_TopRate 模式:'+mode)
    #mode = "Trust"
    #if(mode=="投信"):
    #    link = "https://goodinfo.tw/StockInfo/StockList.asp?RPT_TIME=&MARKET_CAT=熱門排行&INDUSTRY_CAT=投信買超佔發行張數+–+5日%40%40投信買超佔發行張數%40%40投信+–+5日" 
    #else if(mode=="外資")
    #    link = "https://goodinfo.tw/StockInfo/StockList.asp?RPT_TIME=&MARKET_CAT=熱門排行&INDUSTRY_CAT=外資買超佔發行張數+–+5日%40%40外資買超佔發行張數%40%40外資+–+5日"
    #else if(mode=="自營商")
    #    link = "https://goodinfo.tw/StockInfo/StockList.asp?RPT_TIME=&MARKET_CAT=熱門排行&INDUSTRY_CAT=自營商買超佔發行張數+–+5日%40%40自營商買超佔發行張數%40%40自營商+–+5日"
    link= "https://goodinfo.tw/StockInfo/StockList.asp?RPT_TIME=&MARKET_CAT=熱門排行&INDUSTRY_CAT="+mode+"買超佔發行張數+–+5日%40%40"+mode+"買超佔發行張數%40%40"+mode+"+–+5日"
    print(link+'\n')
    res_Page = rs.get(link,headers=header, timeout = 15,verify=True)  
    res_Page.encoding = res_Page.apparent_encoding#根據網站轉換編碼

    
    #PS.例外資訊： socket.timeout: The read operation timed out                  
    soup = BeautifulSoup(res_Page.text, 'html.parser')
    #例外情形 返回無資料
    #m_error = [tag.text for tag in soup.find_all("div", class_="jsx-3008000365")]
    #if(soup.title.string== '404' or str(m_error)!='[]'):
    #    rtn = '找不到相關資訊歐~'
    #    print(rtn)
    #    return rtn
    
    m_key=[]
    m_Value=[]
   
    for num in range(0,TopNum, 1):
        st_Row="row"+str(num)
        RowInfo=soup.find(id=st_Row)
        m_Info = [tag.text for tag in RowInfo.find_all("td")]                 
        #建立字典
        dInfo={
                   '排行':str(m_Info[0]),
                   '代號':str(m_Info[1]),
                   '名稱':str(m_Info[2]),
                   '成交':str(m_Info[3]), 
                   '漲跌價':str(m_Info[4]), 
                   '漲跌幅':str(m_Info[5]), 
                   '更新日期':str(m_Info[6]), 
                   '當日買賣超佔發行張數':str(m_Info[7]) ,
                   '2日買賣超佔發行張數':str(m_Info[8]) ,
                   '3日買賣超佔發行張數':str(m_Info[9]) ,
                   '5日買賣超佔發行張數':str(m_Info[10])             
        }       
        #排行,代號,名稱,成交,五日連買比
        rtn_st = dInfo["排行"]+'\t'+dInfo["名稱"]+"("+dInfo["代號"]+")\t"+dInfo["當日買賣超佔發行張數"]+"\t"+dInfo["2日買賣超佔發行張數"]+"\t"+ dInfo["當日買賣超佔發行張數"]+"\t"+dInfo["3日買賣超佔發行張數"]     
        m_key.append(dInfo['排行'])
        m_Value.append(rtn_st)
  
    
    m_data_zip=[]
    m_data_zip = zip(m_key,m_Value)
    m_data_dict = dict(m_data_zip)
    print("其他資訊:"+str(m_data_dict))
    print('離開函式:ContinuousTrust 模式:'+mode)   
    return m_data_dict   
   
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