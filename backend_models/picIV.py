from PIL import Image
from io import BytesIO
import pytesseract
import PIL.Image
import PIL.ImageDraw
##https://towardsdatascience.com/deploy-python-tesseract-ocr-on-heroku-bbcc39391a8d

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'#本機
#pytesseract.pytesseract.tesseract_cmd ='/app/.apt/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
#pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/share/tesseract-ocr/4.00/tessdata'
#pytesseract.pytesseract.tesseract_cmd ='/app/vendor/tesseract-ocr/bin/tesseract'


def getPixel(image,x,y,G,N):
    L = image.getpixel((x,y))
    if L > G:
        L = True
    else:
        L = False
 
    nearDots = 0
    if L == (image.getpixel((x - 1,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1,y)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1,y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x,y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y + 1)) > G):
        nearDots += 1
 
    if nearDots < N:
        return image.getpixel((x,y-1))
    else:
        return None
# 降噪 Function
def clearNoise(image,G,N,Z):
    draw = ImageDraw.Draw(image)
 
    for i in range(0,Z):
        for x in range(1,image.size[0] - 1):
            for y in range(1,image.size[1] - 1):
                color = getPixel(image,x,y,G,N)
                if color != None:
                    draw.point((x,y),color)

    return image


def Pic_Auth(Src):
    result="null"     
    if(type(Src)==bytes):#如果傳入二元檔
        print('傳入二元檔:'+str(type(Src)))   
        img = Image.open(BytesIO(Src))
        result = pytesseract.image_to_string(img)
    elif(type(Src)==str):#如果傳入檔案路徑        
        print('傳入路徑:'+ Src)   
        img = Image.open(Src)   
        result = pytesseract.image_to_string(img, lang="chi_tra+eng")
    print('辨識結果:'+result +' 長度:'+str(len(result)))    
    return result

