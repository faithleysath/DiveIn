import httpx
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch(url, method='GET', headers=None, params=None, data=None, json=None, cookies=None):
    """
    使用httpx获取URL，支持GET和POST方法。

    :param url: 请求的URL地址。
    :param method: HTTP方法（'GET'或'POST'），默认是'GET'。
    :param headers: 可选的请求头。
    :param params: 可选的查询参数，适用于GET请求。
    :param data: 可选的表单数据，适用于POST请求。
    :param json: 可选的JSON数据，适用于POST请求。
    :return: httpx的响应对象。
    """
    try:
        with httpx.Client() as client:
            if method.upper() == 'GET':
                response = client.get(url, headers=headers, params=params, cookies=cookies)
            elif method.upper() == 'POST':
                response = client.post(url, headers=headers, data=data, json=json, params=params, cookies=cookies)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 检查响应是否成功（状态码200-299）
            # response.raise_for_status()
            return response
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP状态错误: {e}")
        raise
