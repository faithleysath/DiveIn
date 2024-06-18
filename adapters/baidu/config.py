import os
import json
import httpx

class Cookies(httpx.Cookies):
    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.load_cookies()

    def load_cookies(self):
        try:
            with open(self.file_path, 'r') as f:
                cookies_dict = json.load(f)
                for name, cookie_value in cookies_dict.items():
                    self.set(name, cookie_value)
        except FileNotFoundError:
            pass

    def save_cookies(self):
        cookies_dict = {cookie.name: cookie.value for cookie in self.jar}
        with open(self.file_path, 'w') as f:
            json.dump(cookies_dict, f)

    def to_dict(self):
        return {cookie.name: cookie.value for cookie in self.jar}

    def __setitem__(self, name, value):
        super().__setitem__(name, value)
        self.save_cookies()

    def __delitem__(self, name):
        super().__delitem__(name)
        self.save_cookies()

    def __iter__(self):
        return iter(self.to_dict())

    def items(self):
        return self.to_dict().items()

    def __repr__(self):
        return f"EnhancedCookies({self.to_dict()})"

# 单例
cookies_file = os.path.join('cookies', 'baidu_tieba.json')
global_cookies = Cookies(cookies_file)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "tieba.baidu.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}