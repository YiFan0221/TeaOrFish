
# 專案說明
===================

## 此專案專門做為Linebot的接收服務並將需求轉給Server

<br><br />
### [Environment]
### LINEBOT_POST_TOKEN = {from post token}
### LINEBOT_RECV_TOKEN = {from post token}
### CONNECTSTRING = {mongodb connection string}
<br><br />
# 要點
 1. Heroku雲端URL
> https://dashboard.heroku.com/apps/teaorfish/logs

 2. LineBotDevelopers URL
> https://developers.line.biz/console/channel/1656189523/messaging-api

 3. 現在有三處可掛
> https://teaorfish.herokuapp.com/callback
> https://yfnoip.ddns.net:4000/callback
> https://yifanserver.teaorfish.com:4000/callback

 4. LineBot 基本開發
> https://engineering.linecorp.com/zh-hant/blog/line-device-10/

 5. 爬蟲對象來源網站URL
> https://invest.cnyes.com/twstock/TWS/2330

※通常要改這個 jsx-2214436525 info-lp
<br><br />

# SSL相關
### OpenSSL 操作筆記 - 產生 CSR
http://jianiau.blogspot.com/2015/07/openssl-generate-csr.html
### 產生Key和中繼請求    
> openssl req -new -sha256 -newkey rsa:2048 -keyout {Name}.key -out {Name}.crr -config {ssl.conf}

### 安裝Snap
> sudo snap install core; sudo snap refresh core

### 安裝Cerbot
> sudo snap install --classic certbot
> 
<br><br />

Docker 相關說明
=============

指令說明
-------------

##  \<version> = 1.0.1

### Docker build  -t 要建立出的image名稱  --no-cache 從頭執行
> sudo docker build --no-cache -t gary80221/teaorfish .

### 添加版本號
> sudo docker tag <ContainerID> gary80221/teaorfish:\<version>

### 將Image 作為容器

> sudo docker run -e LINEBOT_POST_TOKEN={} LINEBOT_RECV_TOKEN = {} CONNECTSTRING = {}
retryWrites=true&w=majority --rm --name teaorfish -p 4000:4000 -p 4000:4000/udp -i -t gary80221/teaorfish:\<version>
 

####  ※run 前綴說明
--rm : run image結束時會自動把容器刪掉
-p : 將要轉發的port開啟 斜線後事協定
-d : 執行後仍有監控式
-t : attach時Container的螢幕會接到原來的螢幕上。
-i : attach時鍵盤輸入會被Container接手
--restart=always : 作用 https://www.cnblogs.com/kaishirenshi/p/10396446.html


### 啟用容器
> sudo docker start teaorfish

### 進入容器
> sudo docker attach teaorfish

### 在容器外對容器下命令 示範從外部執行 bash
> sudo docker exec -it teaorfish /bin/bash

## 移除容器與IMAGE
### 停止容器
> sudo docker stop teaorfish
### 移除容器
> sudo docker rm teaorfish
### 移除IMAGE
> sudo docker rmi gary80221/teaorfish:\<version>

<br><br />

DockerFilse 編寫流程
=================================================

> 在一個 container 只運行一個 one process in one container

在產生 Docker Image 的時候應避免把太多服務包在一起，

通常一個 Docker Image 約幾百MB左右。
<br><br />
> Container 中的 data 不會保存下來 

>> All data in the container is not preserved

當一個 container 停止運作時，存在該 container 的資料也會隨之消失。

必須藉由第三方儲存服務，將內部的data保存下來。

## python建立容器步驟
1.	根據使用的python 找對應版本的Docker Base 容器
2.	https://hub.docker.com/_/python
3.	撰寫requirements.txt  把會用到的套件都寫進去
4.	    pip freeze > requirements.txt 把套件中的都安裝進去
5.	撰寫Docker File
6.	FROM python:3.9 改成 FROM python:3.9-slim 可以把沒用到的給清除
7.	先處理套件(requirements)在處理Copy SourceCode

寫其他Docker File 
上述步驟從第3步驟開始，都相同

另外還有包Docker容器的相關說明

<br><br />

上傳 Docker Image 到 Docker Hub
=============================
> 參考 https://ithelp.ithome.com.tw/articles/10192824

#### 先登入
    sudo docker login

#### 推送到docker imagehub
> sudo docker push gary80221/teaorfish:\<version>

#### 到別台電腦在拉下來
> sudo docker pull gary80221/teaorfish:\<version>


<br><br />

# 參考資料

> [小抄] Docker 基本命令 (實用)
https://yingclin.github.io/2018/docker-basic.html

> 使用 DockerSlim 優化和減小 Docker 容器鏡像的大小(↓這個ARM不能用)
https://grayguide.net/zh-hant/%E4%BD%BF%E7%94%A8-dockerslim-%E5%84%AA%E5%8C%96%E5%92%8C%E6%B8%9B%E5%B0%8F-docker-%E5%AE%B9%E5%99%A8%E9%8F%A1%E5%83%8F%E7%9A%84%E5%A4%A7%E5%B0%8F


> 為你的Python 應用選擇一個最好的Docker 映像(↓各家base評比)
https://aws.amazon.com/cn/blogs/china/choose-the-best-docker-image-for-your-python-application/


> 關於 ping 位於網路層內的位置
https://ithelp.ithome.com.tw/questions/10203841



> 要執行shellscript(可以用 但會多一層image)
> 
    RUN sh ./ConfigRTSPRTMP.sh
建議用 \& 來連接
    
    RUN sh ./ConfigRTSPRTMP.sh \
    && exec OKSOKS \
    && cd /ext/balabala \


> 一般DOCKER FILE指令教學
https://ithelp.ithome.com.tw/articles/10191016

> COPY 複製文件
https://yeasy.gitbook.io/docker_practice/image/dockerfile/copy


> 打造最小 Python Docker 容器(如何打包docker)
https://blog.wu-boy.com/2021/07/building-minimal-docker-containers-for-python-applications/

> 清除緩存 layer方法
https://blog.csdn.net/easylife206/article/details/125814530

> 安裝APT相關庫（-y=對任何提示回答“是”）
> 
    sudo apt-get -y install make


> 可以清除一堆沒用的Image的方法
    docker rmi $(docker images --filter "dangling=true" -q --no-trunc)

> 啟用Image 的方法
前面名字為Tag名稱  後面image名稱 

    –d : 表示背景運作 
    –P : 要轉發port 可以複數個 –p 
    -t : attach時Container的螢幕會接到原來的螢幕上。
    -i : attach時鍵盤輸入會被Container接手

> 執行中的Container
https://joshhu.gitbooks.io/dockercommands/content/Containers/DockerRunMore.html

> Container內部及外部的執行
進入執行中Container內部 : docker attach {my1r:Tag}
https://joshhu.gitbooks.io/dockercommands/content/Containers/IntoContainers.html

> 詳細步驟請看
    dockershellscript.sh

> Link 其他容器 說明: 不須與外界PORT對接 實現安全性
https://philipzheng.gitbook.io/docker_practice/network/linking

> Docker 透過 2 種方式為容器公開連接訊息：
環境變數
更新 /etc/hosts 檔案
使用 env 命令來查看 web 容器的環境變數


> 修改 Docker 中 container 的 Port 對應
https://blog.yowko.com/change-container-port-mapping/

> 假如某一天，你突然想改變 port 的對應或者是新增或移除 port ，該怎麼做呢？
stop container >> commit container to image >> run new image and new port.


# Jenkins 筆記(借存)
### Pull Image
> docker pull jenkins/jenkins:lts-jdk11

### run Jenkins (在容器內新增一個 /var/jenkins_home 資料夾)
> docker run -p 8080:8080 -p 50000:50000 --restart=on-failure -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk11

### 取出初始化密碼
> sudo docker cp b9258fcdaef4:/var/jenkins_home/secrets/initialAdminPassword ./ 

## 用WebUI控制
### 管理員使用者
> root : Gary80221  