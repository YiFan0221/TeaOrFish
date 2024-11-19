
TeaOrFilsh
===================
作為分散式架構架構中的主服務, 

主要展現backend, Linebot/OpenAI api的串接, SSL的掛載, forward request, build and delivery Docker container

副服務git link: [YiFanServer](https://github.com/YiFan0221/YiFanServer)

<br><br />

# 大綱 <a name="top"></a>
### 1.---------架構方塊圖   [go](#architecture-1)
### 2.---------操作筆記             [go](#操作筆記-2)
### 2.1 -------ssl掛載             [go](#ssl掛載-21)
### 2.2 -------venv啟用關閉        [go](#venv啟用關閉-22)
### 2.3 -------編譯版本            [go](#編譯版本-23)
### 2.4 -------DockerFilse   [go](#write-dockerfilse-24)
### 2.5 -------python建立容器步驟  [go](#python建立容器步驟-25)
### 2.6 -------docker build and launch [go](#docker-build-and-launch-26)
### 2.7 -------docker container operation  [go](#docker-container-operation-27)
### 2.8 -------push Docker Image to Docker Hub [go](#push-docker-image-to-docker-hub-28)
### 2.9 -------docker-compose  [go](#docker-compose-29)
### 2.10 ------docker-compose secretes [go](#docker-compose-secretes-210)

## Architecture 1
![](/ReadmePic/pic0.jpg)
<br><br />
[Back Top](#top)
<br><br />

## 操作筆記 2
記錄些平常開發時會用到的指令與知識
<br><br />
[Back Top](#top)
<br><br />

## SSL掛載 2.1
OpenSSL 操作筆記
[產生 CSR](http://jianiau.blogspot.com/2015/07/openssl-generate-csr.html)

產生Key和中繼請求    (但這邊只是自簽)
```
> openssl req -x509 -new -nodes -sha256 -newkey rsa:2048 -keyout teaorfish.key -out teaorfish.crt -config ssl.conf
```

安裝Snap
```
sudo snap install core; sudo snap refresh core
```

安裝Cerbot
```
sudo snap install --classic certbot
``` 
<br><br />

[Back Top](#top)

<br><br />

# venv啟用關閉 2.2
創建
```
python -m venv tutorial-env
```

啟用
```
source ./venv/bin/activate
```

關閉
```
deactivate
```

<br><br />

[Back Top](#top)

<br><br />

## 編譯版本 2.3
```
cd /TeaOrFish/
./Release_Build/build_release_so.sh   
cp ../lib/TeaOrFish/ {target}
```
<br><br />
[Back Top](#top)
<br><br />

## Write DockerFilse 2.4
產生 Docker Image 的時候應避免把太多服務包在一起，\
一個 container 只運行一個 one process in one container\
通常 Docker Image 約幾百MB左右。\
Container 中的 data 不會保存下來\
當一個 container 停止運作時存在該 container 的資料也會隨之消失。\
必須藉由第三方儲存服務或者用-v做關聯，將內部的data保存下來。
<br><br />
[Back Top](#top)
<br><br />

## python建立容器步驟 2.5
- 根據使用的python 找對應版本的Docker Base 容器 [in this project](https://hub.docker.com/_/python)
- 撰寫requirements.txt 把會用到的套件都寫進去, 可用此指令產出 requirements
``` 
pip freeze > requirements.txt 
```
- 使用requirements安裝則可以使用
```
pip install -r requirements.txt
```
- 撰寫Docker File
- FROM python:3.9 改成 FROM python:3.9-slim 可以把沒用到的給清除
- 先處理套件(requirements)在處理Copy SourceCode
- 寫其他Docker File 
上述步驟從第3步驟開始，都相同
<br><br />
[Back Top](#top)
<br><br />

## Docker build and launch 2.6
-t 要建立出的image名稱  
--no-cache 不產生cache
```
sudo docker build --no-cache -t gary80221/teaorfish .
```

標記版本號
```
sudo docker tag <ContainerID> gary80221/teaorfish:\<version>
```

啟動container
```
sudo docker run --rm --name teaorfish \
 -p 4000:4000 \
 -p 4000:4000/udp \
 -d -e LINEBOT_POST_TOKEN={} \
 -e LINEBOT_RECV_TOKEN={} \
 -e CONNECTSTRING={} \
 -e TARGET_SERVER_URL={} \
 gary80221/teaorfish:\<version>
```
Environment
```
LINEBOT_POST_TOKEN = {from post token}
LINEBOT_RECV_TOKEN = {from post token}
CONNECTSTRING = {mongodb connection string}
TARGET_SERVER_URL = {http://IP or domain :5000}
SSL_PEM = {SSL憑證相對路徑}
SSL_KEY = {SSL私鑰相對路徑}
TEAORFISH_SERVER_PORT = {4000}
YIFANSERV_SERVER_PORT = {5000}
```

run 前綴詞說明\
--rm : run image結束時會自動把容器刪掉\
-p : 將要轉發的port開啟 斜線後事協定\
-d : 執行後仍有監控式\
-t : attach時Container的螢幕會接到原來的螢幕上\
-i : attach時鍵盤輸入會被Container接手\
--restart=always : [作用請參考](https://www.cnblogs.com/kaishirenshi/p/10396446.html)
<br><br />
[Back Top](#top)
<br><br />

## Docker container operation 2.7
 啟用容器
```
sudo docker start teaorfish
```
進入容器
```
sudo docker attach teaorfish
```
在容器外對容器下命令 示範從外部執行 bash
```
sudo docker exec -it teaorfish /bin/bash
```
停止容器
```
sudo docker stop teaorfish
```
移除容器
```
sudo docker rm teaorfish
```
移除IMAGE
```
sudo docker rmi gary80221/teaorfish:\<version>
or
sudo docker rmi <Image ID>
```
<br><br />
[Back Top](#top)
<br><br />
 
## Push Docker Image to Docker Hub 2.8
[參考ref] https://ithelp.ithome.com.tw/articles/10192824

Log in
```
sudo docker login
```

push to docker imagehub
```
sudo docker push gary80221/teaorfish:\<version>
```

pull 
```
sudo docker pull gary80221/teaorfish:\<version>
```
<br><br />
[Back Top](#top)
<br><br />

## Docker-compose 2.9

建立網路nat
```
docker network create nat
```

啟用
```
docker-compose up -d
```
or scale up
```
docker-compose up -d --scale {serviceName}=3
```


停止
```
docker-compose stop <Service Name>
```
開始
```
docker-compose start <Service Name>
```

移除 將較於up down則是關閉並移除
```
docker-compose down
```

若要開啟3個容器則要再輸入一次
```
docker-compose up -d --scale teaorfish=3
```

<br><br />
[Back Top](#top)
<br><br />

## docker-compose secretes 2.10
在最上層宣告並引入檔案到secretes
```
secrets: 
    SSL_PEM:
        file: {FilePath}
```

在服務內宣告要使用的secretes 並且在環境參數中將對應檔案宣告在環境參數中
```
   environment:      
      LINEBOT_POST_TOKEN: ${LINEBOT_POST_TOKEN}
      LINEBOT_RECV_TOKEN: ${LINEBOT_RECV_TOKEN}     
      TARGET_SERVER_URL : ${TARGET_SERVER_URL}
      SSL_PEM : /run/secrets/SSL_PEM
      SSL_KEY : /run/secrets/SSL_KEY
   secrets:
      - SSL_PEM
      - SSL_KEY
```
<br><br />
[Back Top](#top)
<br><br />

# Other ref source. 
[[小抄] Docker 基本命令 (實用)](https://yingclin.github.io/2018/docker-basic.html)\
[一般DOCKER FILE指令教學](https://ithelp.ithome.com.tw/articles/10191016)\
[使用 DockerSlim 優化和減小 Docker 容器鏡像的大小(link內的ARM不能用)](https://grayguide.net/zh-hant/%E4%BD%BF%E7%94%A8-dockerslim-%E5%84%AA%E5%8C%96%E5%92%8C%E6%B8%9B%E5%B0%8F-docker-%E5%AE%B9%E5%99%A8%E9%8F%A1%E5%83%8F%E7%9A%84%E5%A4%A7%E5%B0%8F)\
[為你的Python 應用選擇一個最好的Docker 映像(各版base評比)](https://aws.amazon.com/cn/blogs/china/choose-the-best-docker-image-for-your-python-application/)\
[關於 ping 位於網路層內的位置](https://ithelp.ithome.com.tw/questions/10203841)\
[COPY 複製文件](https://yeasy.gitbook.io/docker_practice/image/dockerfile/copy)\
[打造最小 Python Docker 容器(如何打包docker)](https://blog.wu-boy.com/2021/07/building-minimal-docker-containers-for-python-applications/)\
[清除緩存 layer方法](https://blog.csdn.net/easylife206/article/details/125814530)


dockerfile內要執行shellscript可以用 
```
    RUN sh ./ConfigRTSPRTMP.sh
```
但會多一層image 建議用 \& 來連接
```
    RUN sh ./ConfigRTSPRTMP.sh \
    && exec OKSOKS \
    && cd /ext/balabala \
```
安裝APT相關庫（-y=對任何提示回答“是”）
``` 
    sudo apt-get -y install make
```

可以清除一堆沒用的Image的方法
```
    docker rmi $(docker images --filter "dangling=true" -q --no-trunc)
```

[執行中的Container](https://joshhu.gitbooks.io/dockercommands/content/Containers/DockerRunMore.html)\
進入執行中Container內部 [ref](https://joshhu.gitbooks.io/dockercommands/content/Containers/IntoContainers.html)
```
docker attach {containerID}
```
但容易內部掛掉就出不來 建議用
```
docker -exec {containerID}
```

[Link 其他容器 說明: 不須與外界PORT對接 實現安全性](https://philipzheng.gitbook.io/docker_practice/network/linking)

Docker 透過兩種方式為容器公開連接訊息 並使用 env 命令來查看 web 容器的環境變數
- 環境變數
- 更新 /etc/hosts 檔案


[修改 Docker 中 container 的 Port 對應](https://blog.yowko.com/change-container-port-mapping/)

假如某一天，你突然想改變 port 的對應或者是新增或移除 port ，該怎麼做呢？
```
stop container
commit container to image
run new image and new port.
```
#### note
[LineBotDevelopers URL](https://developers.line.biz/console/channel/1656189523/messaging-api)

 現在有三處可掛\
[1廢置](https://teaorfish.herokuapp.com/callback)\
[2](https://yfnoip.ddns.net:4000/callback)\
[3廢置](https://yifanserver.teaorfish.com:4000/callback)\
[LineBot 基本開發](https://engineering.linecorp.com/zh-hant/blog/line-device-10/)\
[爬蟲對象來源網站URL](https://invest.cnyes.com/twstock/2330)


[Back Top](#top)