# -*- coding: utf-8 -*-
import os
import time
import logging
import random
from os import path
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
import shutil
import configparser  # 导入configparser模块

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s %(levelname)s] %(message)s", datefmt="%H:%M:%S"
)

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 检查配置项是否存在
if not config.has_section('DEFAULT'):
    logging.error("配置文件中缺少 DEFAULT 节，请检查 config.ini 文件。")
    exit(1)

USERNAME = [line.strip() for line in config.get('DEFAULT', 'LINUXDO_USERNAME').splitlines() if line.strip()]
PASSWORD = [line.strip() for line in config.get('DEFAULT', 'LINUXDO_PASSWORD').splitlines() if line.strip()]
SCROLL_DURATION = config.getint('DEFAULT', 'SCROLL_DURATION', fallback=0)
VIEW_COUNT = config.getint('DEFAULT', 'VIEW_COUNT', fallback=1000)
HOME_URL = config.get('DEFAULT', 'HOME_URL', fallback="https://linux.do/")
CONNECT_URL = config.get('DEFAULT', 'CONNECT_URL', fallback="https://connect.linux.do/")

browse_count = 0
connect_info = ""
like_count = 0
account_info = []

user_count = len(USERNAME)

if user_count != len(PASSWORD):
    logging.error("用户名和密码的数量不一致，请检查配置文件设置。")
    exit(1)

logging.info(f"共找到 {user_count} 个账户")


class LinuxDoBrowser:
    def __init__(self) -> None:
        logging.info("启动 Selenium")

        global chrome_options
        chrome_options = webdriver.ChromeOptions()

        # Chrome 选项配置，适合 Linux 环境，无头模式设置
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # 启用无头模式
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument("--disable-popup-blocking")

        # 添加 user-agent（根据需要修改）
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0')

        # 检查 chromedriver 路径
        global chromedriver_path
        chromedriver_path = shutil.which("chromedriver")

        if not chromedriver_path:
            logging.error("chromedriver 未找到，请确保已安装并配置正确的路径。")
            exit(1)

        self.driver = None

    def create_driver(self):
        try:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 删除 navigator.webdriver 标志
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)

            return True

        except Exception as e:
            logging.error(f"创建 WebDriver 失败: {e}")
            return False

    def simulate_typing(self, element, text, typing_speed=0.1, random_delay=True):
        for char in text:
            element.send_keys(char)
            if random_delay:
                time.sleep(typing_speed + random.uniform(0, 0.1))
            else:
                time.sleep(typing_speed)

    def login(self) -> bool:
       # ... (保持原有逻辑)
       pass

   def load_all_topics(self):
       # ... (保持原有逻辑)
       pass

   def click_topic(self):
       # ... (保持原有逻辑)
       pass

   def run(self):
       """主运行函数"""
       # ... (保持原有逻辑)
       pass

if __name__ == "__main__":
   linuxdo_browser = LinuxDoBrowser()
   linuxdo_browser.run()
