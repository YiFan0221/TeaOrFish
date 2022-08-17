from PIL import Image
from io import BytesIO
import pytesseract
#https://towardsdatascience.com/deploy-python-tesseract-ocr-on-heroku-bbcc39391a8d

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'#本機
#pytesseract.pytesseract.tesseract_cmd ='/app/.apt/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/share/tesseract-ocr/4.00/tessdata'
#pytesseract.pytesseract.tesseract_cmd ='/app/vendor/tesseract-ocr/bin/tesseract'


def Pic_Auth(Src):
    
    print('進入函式:Pic_Auth' )
    print('型態:'+str(type(Src)))        
    result="null"     
    if(type(Src)==bytes):#如果傳入二元檔
        img = Image.open(BytesIO(Src))
        result = pytesseract.image_to_string(img)
    elif(type(Src)==str):#如果傳入檔案路徑        
        img = Image.open(Src)   
        result = pytesseract.image_to_string(img)
    
    if(len(result)==1):
        print(str(type(result)))    
        print('辨識失敗:'+result +' 長度:'+str(len(result)))
    else:
        print('辨識結果:'+result +' 長度:'+str(len(result)))
    return result
    print('離開函式:Pic_Auth' )
    

