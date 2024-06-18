from bs4 import BeautifulSoup, Comment
from .utils import fetch
from typing import List, Tuple, Dict, Any
import re
import json
import html
from datetime import datetime

# 配置URL模板
THREAD_URL = "https://tieba.baidu.com/p/{thread_id}?pn={page}"
FETCH_COMMENT_API = "https://tieba.baidu.com/p/totalComment?tid={thread_id}&pn={page}"
GET_LIKE_FORUM = "https://tieba.baidu.com/p/getLikeForum?uid={uid}"
GET_USER_INFO = "https://tieba.baidu.com/home/get/panel?id={portrait}"
USER_HOME = "https://tieba.baidu.com/home/main?id={portrait}"
FORUM_HOME = "https://tieba.baidu.com/f?kw={tbs}&pn={page}"

def fetch_thread_pn(thread_id: int) -> int:
    """
    获取thread页面的页码数量

    :param thread_id: 贴子ID
    :return: 页码数量
    """
    url = THREAD_URL.format(thread_id=thread_id, page=1)
    html_string = fetch(url).text
    pattern = r'\?pn=(\d+)"\s*[^>]*>\s*尾页'
    match = re.search(pattern, html_string)
    if match:
        pn_value = int(match.group(1))
    else:
        pn_value = 1
    return pn_value


def fetch_posts_by_thread(
    thread_id: int, page: int = 0
) -> List[Dict[str, Any]]:
    """
    根据thread_id获得楼层和作者信息

    :param thread_id: 贴子ID
    :param page: 页码
    :return: 楼层信息（包括作者信息）
    """
    if page == 0: # 则循环爬取所有页面
        total_page = fetch_thread_pn(thread_id)
        return [post for pn in range(1, total_page + 1) for post in fetch_posts_by_thread(thread_id, pn)]
    if page < 0: # 代表倒序
        total_page = fetch_thread_pn(thread_id)
        return fetch_posts_by_thread(thread_id, total_page + page + 1)
    url = THREAD_URL.format(thread_id=thread_id, page=page)
    res = fetch(url)
    soup = BeautifulSoup(res.text, "html.parser")

    raw_tails = soup.find_all("div", class_="post-tail-wrap")
    floor_data = {}
    for post in raw_tails:
        tail_info = post.find_all("span", class_="tail-info")
        # 提取来源设备
        source_device_span = post.find("span", class_="tail-info").find("a")
        source_device = source_device_span.text if source_device_span else None
        # print(tail_info)
        # 提取楼层数
        floor_num = int(tail_info[-2].text[:-1])
        # 提取 IP 属地
        ip_location = post.find(
            "span", string=lambda x: x and "IP属地" in x
        ).text.split(":")[1]
        # 提取发布时间
        publish_time = datetime.strptime(tail_info[-1].text, r"%Y-%m-%d %H:%M")
        # 将提取的信息加入字典
        floor_data[floor_num] = (ip_location, source_device, publish_time)

    raw_divs = soup.find_all("div", class_="l_post")
    posts: List[Dict[str, Any]] = []
    for raw_div in raw_divs:
        raw_data = raw_div.get("data-field")
        if raw_data:
            decoded_raw_data = html.unescape(raw_data)
            try:
                data = json.loads(decoded_raw_data)
                raw_author = data["author"]
                raw_post = data["content"]
                floor = raw_post["post_no"]
                ip_location, source_device, publish_time = floor_data[floor]
                post = {
                    "post_id": raw_post["post_id"],
                    "thread_id": raw_post["thread_id"],
                    "forum_id": raw_post["forum_id"],
                    "is_anonym": raw_post["is_anonym"],
                    "content": raw_post["content"],
                    "floor": floor,
                    "comment_num": raw_post["comment_num"],
                    "is_fold": raw_post["is_fold"],
                    "ip_location": ip_location,
                    "post_from": source_device,
                    "post_time": publish_time,

                    "author_id": raw_author["user_id"],
                    "author_name": raw_author["user_name"],
                    "author_portrait": raw_author["portrait"],
                    "author_nickname": raw_author["user_nickname"],
                }
                posts.append(post)
            except json.JSONDecodeError:
                print("JSON解码失败:", decoded_raw_data)
    return posts


def fetch_comments_by_thread(
    thread_id: int, page: int = 0
) -> List[Dict[str, Any]]:
    """
    根据thread_id获得评论和作者信息

    :param thread_id: 贴子ID
    :param page: 页码
    :return: 评论信息（包括作者信息）
    """
    if page == 0: # 循环爬取所有评论
        result = []
        comment = {514}
        last_comment = {114}
        while comment:
            page += 1
            last_comment = comment
            comment = fetch_comments_by_thread(thread_id, page)
            if comment == last_comment:
                break
            result.extend(comment)
        return result
        
    url = FETCH_COMMENT_API.format(thread_id=thread_id, page=page)
    res = fetch(url)
    res_json = res.json()
    if res_json["errno"] != 0:
        raise Exception(res_json["errmsg"])

    data = res_json["data"]
    comment_list: Dict = data["comment_list"]
    user_list: Dict = data["user_list"]
    if user_list == []:
        user_list = dict()
    if comment_list == []:
        comment_list = dict()
    users = {}
    for k, v in user_list.items():
        author = {
            "author_id": v["user_id"],
            "author_name": v.get("user_name"),
            "author_portrait": v["portrait"],
            "author_nickname": v["nickname"],
            "show_nickname": v["show_nickname"],
            "sex": "女" if v.get("user_sex") == 2 else "男",
        }
        users[int(k)] = author

    comments: List[Dict[str, Any]] = []
    for k, v in comment_list.items():
        for comment_info in v["comment_info"]:
            author_id = comment_info["user_id"]
            author = users.get(author_id, {})
            
            comment = {
                "comment_id": comment_info["comment_id"],
                "post_id": comment_info["post_id"],
                "thread_id": comment_info["thread_id"],
                "content": comment_info["content"],
                "comment_from": comment_info.get("come_from"),
                "location": comment_info.get("location"),
                "comment_time": datetime.fromtimestamp(comment_info["now_time"]),
                **author  # 合并作者信息，替换字段名
            }
            comments.append(comment)
    return comments


def get_like_forum(user_id: int) -> List[Dict[str, Any]]:
    """
    获得指定用户关注的贴吧及其经验值

    :param user_id: 用户ID
    :return: 用户关注的贴吧及其经验值
    """
    url = GET_LIKE_FORUM.format(uid=user_id)
    res = fetch(url)
    res_json = res.json()
    if res_json["errno"] != 0:
        raise Exception(res_json["errmsg"])

    data = res_json["data"]["info"]
    userforums: List[Dict[str, Any]] = []
    for d in data:
        userforum = {
            "user_id": user_id,
            "forum_id": d["id"],
            "user_level": d["user_level"],
            "user_exp": d["user_exp"],
            "is_like": bool(d["is_like"]),
            "favo_type": d["favo_type"],
        }
        userforums.append(userforum)
    return userforums


def get_user_location(portrait: str) -> str:
    """
    获得IP属地

    :param portrait: 用户头像标识
    :return: IP属地
    """
    url = USER_HOME.format(portrait=portrait)
    response = fetch(url)
    if response.status_code == 200:
        text = response.text
        pattern = r"IP属地:([^<]+)"
        match = re.search(pattern, text)
        if match:
            ip_location = match.group(1).strip()
            return ip_location
        else:
            print("未找到匹配的IP属地")
    else:
        print(f"获取网页失败，状态码: {response.status_code}")


def get_user_info(portrait: str) -> Dict[str, Any]:
    """
    根据portrait获得完整用户信息

    :param portrait: 用户头像标识
    :return: 完整用户信息
    """
    url = GET_USER_INFO.format(portrait=portrait)
    res = fetch(url)
    res_json = res.json()
    if res_json["no"] != 0:
        raise Exception(res_json["error"])

    data = res_json["data"]
    ip_location = get_user_location(portrait)
    user = {
        "portrait": portrait,
        "show_nickname": data["show_nickname"],
        "age": float(data["tb_age"]),
        "sex": "男" if data["sex"] == "male" else "女",
        "followed_count": data.get("followed_count", 0),
        "post_num": data.get("post_num"),
        "is_vip": data["tb_vip"],
        "is_block": data["is_block"],
        "is_private": data["is_private"],
        "ip_location": ip_location,
    }
    return user


def get_forum_thread(
    tbs: str, page: int = 0
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    根据贴吧名称，获得贴吧数据与一页的贴子列表

    :param tbs: 贴吧名称
    :param page: 页码
    :return: 贴吧数据和贴子列表
    """
    url = FORUM_HOME.format(tbs=tbs, page=page)
    res = fetch(url)
    soup = BeautifulSoup(res.text, "html.parser")

    script_tag = soup.find('script', string=re.compile(r'PageData.forum'))

    if script_tag:
        script_content = script_tag.string

        # 提取JavaScript对象
        start_index = script_content.find('PageData.forum = ') + len('PageData.forum = ')
        end_index = script_content.find('};', start_index) + 1  # 包含结束的花括号
        json_str = script_content[start_index:end_index]
        
        forum_data = eval(json_str)
    else:
        raise
    
    def extract_number_from_span(class_name):
        # 先尝试在非注释部分查找
        span_tag = soup.find('span', class_=class_name)
        if span_tag:
            return int(span_tag.text.replace(',', ''))
        
        # 如果在非注释部分没找到，尝试在注释部分查找
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            span_tag = comment_soup.find('span', class_=class_name)
            if span_tag:
                return int(span_tag.text.replace(',', ''))
        return None

    member_num = extract_number_from_span('card_menNum')
    post_num = extract_number_from_span('card_infoNum')
    match = re.search(r'共有主题数<span class="red_text">(\d+)</span>个', res.text)
    if match:
        # 提取的数字字符串转换为整数
        thread_num = int(match.group(1))
    else:
        thread_num = None
        
    forum = {
        "forum_id": forum_data['id'],
        "forum_name": forum_data['name'],
        "first_class": forum_data["first_class"],
        "second_class": forum_data["second_class"],
        "followed_count": member_num,
        "thread_num": thread_num,
        "post_num": post_num,
    }
    
    threads = []
    # 先尝试在非注释部分查找
    ul_thread = soup.find('ul', id="thread_list")
    if not ul_thread:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            ul_thread = comment_soup.find('ul', id="thread_list")
            if ul_thread:
                break
    lis_thread = ul_thread.find_all(lambda tag: tag.name == 'li' and all(cls in tag.get('class', []) for cls in ['j_thread_list', 'thread_item_box']))
    for li_thread in lis_thread:
        thread = li_thread.get("data-field")
        if thread:
            thread = html.unescape(thread)
            thread = json.loads(thread)
            thread["title"] = li_thread.find('div', class_='threadlist_title').find('a').get('title')
            content_div = li_thread.find('div', class_='threadlist_abs threadlist_abs_onlyline')
            if content_div:
                thread["content"] = content_div.text.strip()
            else:
                thread["content"] = ""
            threads.append(thread)
    return forum, threads