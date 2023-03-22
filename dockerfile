FROM python:3.8-slim as build 

COPY . /
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python3", "./linebotTest1.py" ]

#ping
EXPOSE 22
#Flask:4000
EXPOSE 4000
 
