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
        try:
            logging.info(f"--- 开始尝试登录：{self.username}---")

            # 先等待页面加载完成
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )

            # 确保在点击之前页面已完全加载
            time.sleep(3)

            try:
                login_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-button .d-button-label"))
                )
                self.driver.execute_script("arguments[0].click();", login_button)
            except:
                logging.info("尝试备用登录按钮选择器")
                login_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.login-button"))
                )
                self.driver.execute_script("arguments[0].click();", login_button)

            # 等待登录表单出现
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "login-form"))
            )

            # 输入用户名
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "login-account-name"))
            )
            username_field.clear()
            time.sleep(1)
            self.simulate_typing(username_field, self.username)

            # 输入密码
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "login-account-password"))
            )
            password_field.clear()
            time.sleep(1)
            self.simulate_typing(password_field, self.password)

            # 提交登录
            submit_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "login-button"))
            )
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", submit_button)

            # 验证登录结果
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#current-user"))
                )
                logging.info("登录成功")
                return True
            except TimeoutException:
                error_element = self.driver.find_elements(By.CSS_SELECTOR, "#modal-alert.alert-error")
                if error_element:
                    logging.error(f"登录失败：{error_element[0].text}")
                else:
                    logging.error("登录失败：无法验证登录状态")
                return False

        except Exception as e:
           logging.error(f"登录过程发生错误：{str(e)}")
           try:
               self.driver.save_screenshot("login_error.png")
               logging.info("已保存错误截图到 login_error.png")
           except Exception as screenshot_error:
               logging.error(f"保存截图失败: {screenshot_error}")
           return False

    def load_all_topics(self):
       end_time = time.time() + SCROLL_DURATION
       actions = ActionChains(self.driver)

       while time.time() < end_time:
           actions.scroll_by_amount(0, 500).perform()
           time.sleep(0.1)

       logging.info("页面滚动完成，已停止加载更多帖子")

    def click_topic(self):
       try:
           # ... (保持原有逻辑)
           pass

       except Exception as e:
           logging.error(f"click_topic 方法发生错误: {e}")

    def run(self):
       """主运行函数"""
       global browse_count
       global connect_info
       global like_count

       for i in range(user_count):
           start_time = time.time()
           self.username = USERNAME[i]
           self.password = PASSWORD[i]

           logging.info(f"▶️▶️▶️ 开始执行第{i + 1}个账号: {self.username}")

           try:
               if not self.create_driver():
                   logging.error("创建浏览器实例失败，跳过当前账号")
                   continue

               logging.info("导航到 LINUX DO 首页")
               self.driver.get(HOME_URL)

               if not self.login():
                   logging.error(f"{self.username} 登录失败")
                   continue

               self.click_topic()
               logging.info(f"🎉 恭喜：{self.username}，帖子浏览全部完成")

               # 获取 Connect 信息（省略）
               self.logout()

           except WebDriverException as e:
               logging.error(f"WebDriver 初始化失败: {e}")
               exit(1)
           except Exception as e:
               logging.error(f"运行过程中出错: {e}")
           finally:
               if self.driver is not None:
                   self.driver.quit()

           end_time = time.time()
           spend_time = int((end_time - start_time) // 60)

           account_info.append(
               {
                   "username": self.username,
                   "browse_count": browse_count,
                   "like_count": like_count,
                   "spend_time": spend_time,
                   "connect_info": connect_info,
               }
           )

           browse_count = 0
           like_count = 0
           connect_info = ""

       logging.info("所有账户处理完毕")

       summary = ""
       for info in account_info:
           summary += (
               f"用户：{info['username']}\n\n"
               f"本次共浏览 {info['browse_count']} 个帖子\n"
               f"共点赞{info['like_count']} 个帖子\n"
               f"共用时 {info['spend_time']} 分钟\n"
               f"{info['connect_info']}\n\n"
           )
       send = load_send()
       if callable(send):
           send("Linux.do浏览帖子", summary)
       else:
           print("\n通知推送失败")


if __name__ == "__main__":
   linuxdo_browser = LinuxDoBrowser()
   linuxdo_browser.run()
