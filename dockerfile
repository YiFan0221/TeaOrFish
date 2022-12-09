FROM python:3.8-slim as build 


COPY . /
RUN pip install --no-cache-dir -r requirements.txt
# RUN apt-get update \
#  && apt-get install -y \
# tesseract-ocr \
# tesseract-ocr-chi-tra \
# && rm -rf /var/lib/apt/lists/* 

COPY . .
CMD [ "python3", "./linebotTest1.py" ]

#ping
EXPOSE 22
#Flask:4000
EXPOSE 4000
 
