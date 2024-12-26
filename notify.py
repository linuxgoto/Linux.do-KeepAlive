#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import json
import os
import requests
import threading

# 定义新的 print 函数，确保多线程输出有序
_print = print
mutex = threading.Lock()

def print(text, *args, **kw):
    with mutex:
        _print(text, *args, **kw)

# 从环境变量读取配置
push_config = {
    'BARK_PUSH': os.getenv('BARK_PUSH', ''),
    'DD_BOT_SECRET': os.getenv('DD_BOT_SECRET', ''),
    'DD_BOT_TOKEN': os.getenv('DD_BOT_TOKEN', ''),
    'FSKEY': os.getenv('FSKEY', ''),
    'GOBOT_URL': os.getenv('GOBOT_URL', ''),
    'GOBOT_QQ': os.getenv('GOBOT_QQ', ''),
    'GOTIFY_URL': os.getenv('GOTIFY_URL', ''),
    'GOTIFY_TOKEN': os.getenv('GOTIFY_TOKEN', ''),
    'SMTP_SERVER': os.getenv('SMTP_SERVER', ''),
    'SMTP_SSL': os.getenv('SMTP_SSL', 'false'),
    'SMTP_EMAIL': os.getenv('SMTP_EMAIL', ''),
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
    'SMTP_NAME': os.getenv('SMTP_NAME', ''),
}

def bark(title: str, content: str) -> None:
    if not push_config['BARK_PUSH']:
        print("Bark 服务的 BARK_PUSH 未设置!!\n取消推送")
        return

    print("Bark 服务启动")
    
    url = f'https://api.day.app/{push_config["BARK_PUSH"]}'
    
    data = {
        "title": title,
        "body": content,
    }
    
    headers = {"Content-Type": "application/json;charset=utf-8"}
    
    response = requests.post(url=url, data=json.dumps(data), headers=headers).json()

    if response.get("code") == 200:
        print("Bark 推送成功！")
    else:
        print("Bark 推送失败！")

def send(title: str, content: str) -> None:
    notify_function = []

    if push_config.get("BARK_PUSH"):
        notify_function.append(bark)

    # 可以根据需要添加其他通知函数，例如钉钉、飞书等

    ts = [
        threading.Thread(target=mode, args=(title, content), name=mode.__name__)
        for mode in notify_function
    ]
    
    [t.start() for t in ts]
    [t.join() for t in ts]

def main():
    # 示例调用 send 函数
    send("测试标题", "这是一条测试消息。")

if __name__ == "__main__":
    main()
