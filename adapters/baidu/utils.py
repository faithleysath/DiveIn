from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from utils.requests import fetch as f
from .config import global_cookies, headers
import time

def get_browser_driver():
    try:
        # 尝试使用Chrome浏览器
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        return driver
    except Exception as e:
        print(f"Chrome不可用，尝试使用Edge: {e}")
        try:
            # 尝试使用Edge浏览器
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            return driver
        except Exception as e:
            print(f"Edge也不可用: {e}")
            raise

def get_specific_cookies_from_browser(verification_url):
    # 启动浏览器
    driver = get_browser_driver()
    # 打开验证页面
    driver.get(verification_url)
    
    # 轮询监测URL是否变动
    while True:
        current_url = driver.current_url
        if not current_url.startswith('https://wappass.baidu.com/static/captcha/tuxing.html'):
            break
        time.sleep(0.3)  # 每秒钟检查一次
    
    # 获取指定的cookies
    cookies = driver.get_cookies()
    driver.quit()
    
    for cookie in cookies:
        if cookie['name'] == 'BAIDUID_BFESS':
            global_cookies['BAIDUID_BFESS'] = cookie['value']
        elif cookie['name'] == 'tb_as_data':
            global_cookies['tb_as_data'] = cookie['value']
    
    # 如果有缺失的cookie，提醒用户
    if 'BAIDUID_BFESS' not in global_cookies or 'tb_as_data' not in global_cookies:
        print("未能获取到所有关键cookies，请重新运行脚本并确保完成所有验证。")
        exit(1)
    
    return global_cookies

def fetch(url, method='GET', headers=headers, params=None, data=None, json=None, cookies=global_cookies):
    response = f(url, method, headers, params, data, json, cookies)
    if response.status_code == 302:
        verification_url = response.headers.get('Location', 'No location header found')
        print(f"需要验证，访问: {verification_url}")
        get_specific_cookies_from_browser(verification_url)
        response = f(url, method, headers, params, data, json, cookies)
    
    if response.status_code == 200:
        return response
    else:
        raise Exception(f'Failed to retrieve the page - {response.status_code}')