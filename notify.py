#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.parse

import requests

_print = print 
mutex = threading.Lock()

def print(text, *args, **kw):
    with mutex:
        _print(text, *args, **kw)


push_config = {
   'BARK_PUSH': '',
   'DD_BOT_SECRET': '',
   'DD_BOT_TOKEN': '',
   'FSKEY': '',
   'GOBOT_URL': '',
   'GOBOT_QQ': '',
   'GOTIFY_URL': '',
   'GOTIFY_TOKEN': '',
   'SMTP_SERVER': '',
   'SMTP_SSL': 'false',
   'SMTP_EMAIL': '',
   'SMTP_PASSWORD': '',
   'SMTP_NAME': '',
}

for k in push_config:
   if os.getenv(k):
       v = os.getenv(k)
       push_config[k] = v


def bark(title: str, content: str) -> None:
    if not push_config.get("BARK_PUSH"):
       print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")
       return
    
    print("bark 服务启动")
    
    url=f'https://api.day.app/{push_config.get("BARK_PUSH")}' if push_config.get("BARK_PUSH").startswith('http') else f'https://api.day.app/{push_config.get("BARK_PUSH")}'
    
    data={"title": title,"body": content}
    
    headers={"Content-Type": "application/json;charset=utf-8"}
    
    response=requests.post(url=url,data=json.dumps(data),headers=headers).json()

    if response["code"]==200:
       print("bark 推送成功！")
    else:
       print("bark 推送失败！")


def send(title: str, content: str) -> None:

   notify_function=[]

   if push_config.get('BARK_PUSH'):
       notify_function.append(bark)

   ts=[threading.Thread(target=mode,args=(title, content), name=mode.__name__) for mode in notify_function]
   
   [t.start() for t in ts]
   [t.join() for t in ts]


def main():
   send("title", "content")


if __name__ == "__main__":
   main()
