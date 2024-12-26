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
import configparser  # 导入configparser模块

_print = print 
mutex = threading.Lock()

def print(text, *args, **kw):
    with mutex:
        _print(text, *args, **kw)

# 读取配置文件并初始化通知配置项    
config = configparser.ConfigParser()
config.read('config.ini')

push_config = {
   'BARK_PUSH': config.get('DEFAULT', 'BARK_PUSH', fallback=''),
   'DD_BOT_SECRET': config.get('DEFAULT', 'DD_BOT_SECRET', fallback=''),
   'DD_BOT_TOKEN': config.get('DEFAULT', 'DD_BOT_TOKEN', fallback=''),
   'FSKEY': config.get('DEFAULT', 'FSKEY', fallback=''),
   'GOBOT_URL': config.get('DEFAULT', 'GOBOT_URL', fallback=''),
   'GOBOT_QQ': config.get('DEFAULT', 'GOBOT_QQ', fallback=''),
   'GOTIFY_URL': config.get('DEFAULT', 'GOTIFY_URL', fallback=''),
   'GOTIFY_TOKEN': config.get('DEFAULT', 'GOTIFY_TOKEN', fallback=''),
   'SMTP_SERVER': config.get('DEFAULT', 'SMTP_SERVER', fallback=''),
   'SMTP_SSL': config.get('DEFAULT', 'SMTP_SSL', fallback='false'),
   'SMTP_EMAIL': config.get('DEFAULT', 'SMTP_EMAIL', fallback=''),
   'SMTP_PASSWORD': config.get('DEFAULT', 'SMTP_PASSWORD', fallback=''),
   'SMTP_NAME': config.get('DEFAULT', 'SMTP_NAME', fallback=''),
}

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
