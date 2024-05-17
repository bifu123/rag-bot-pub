import aiohttp
import asyncio
from config import http_url, admin_id, bot_id, chat_type_allow, bot_at_string
import re
import requests
import json


# 获取昵称
def get_nickname_by_user_id(user_id):
    data = requests.get(http_url+"/get_friend_list").text
    data = json.loads(data)
    for item in data["data"]:
        if str(item["user_id"]) == str(user_id):
            return str(item["nickname"])
    return f"QQ号为{user_id}的朋友"

# 获取机器人昵称
def get_nickname_by_bot_id(bot_id):
    data = requests.get(http_url+"/get_login_info").text
    data = json.loads(data)["data"]["nickname"]
    return str(data)


# 获取包含@昵称的消息
def get_chat_type(bot_id, data):
    
    user_id = data["user_id"]
    
    user_nick_name = get_nickname_by_user_id(user_id)
    bot_nick_name = get_nickname_by_bot_id(bot_id)
    


    # 消息类型
    if data["post_type"] == "message":
        # 匹配@字符串
        message = data["message"]
        qq_num_pattern = r'\[CQ:at,qq=(\d+)\]' # 匹配[CQ:at,qq=123456]
        qq_num_match = re.search(qq_num_pattern, message)
        if qq_num_match:
            match_id = qq_num_match.group(1)
            if match_id == str(bot_id):
                at_string = "@" + bot_nick_name + " "
            else:
                at_string = "@" + user_nick_name + " "
            at = "yes"
        else:
            at_string = ""
            at = "no"
        other_str = re.sub(qq_num_pattern, '', message).lstrip() # 除去@部分后的字符，再去除开头的空格
        re_combine_message = at_string + other_str 
        

        if data["message_type"] == "private":
            chat_type = "private"
            group_id = "no"
            source_id = user_id
        elif data["message_type"] == "group":
            group_id = data["group_id"]
            source_id = group_id
            if bot_at_string in data["message"]:
                chat_type = "group_at"
            else:
                chat_type = "group"
        else:
            chat_type = data["message_type"]
            group_id = "no"
            source_id = "no"
            
            

    # 事件类型
    if data["post_type"] == "notice":
        # 私发离线文件
        if data["notice_type"] == "offline_file":
            chat_type = "private"
            group_id = "no"
            at = "no"
            source_id = user_id
        # 群文件
        elif data["notice_type"] == "group_upload":
            group_id = data["group_id"]
            chat_type = "group"
            at = "no"
            source_id = user_id
        else:
            chat_type = data["notice_type"]
            group_id = "no"
            at = "no"
            source_id = "no"
        at_string = ""  
        re_combine_message = "" 
        other_str = ""
            
            
    result = {
        "chat_type": chat_type, 
        "user_id": str(user_id), 
        "group_id": str(group_id), 
        "source_id": str(source_id), 
        "at": at,
        "at_string": at_string,
        "re_combine_message": re_combine_message,
        "message": other_str,
        "user_nick_name": user_nick_name,
        "bot_nick_name": bot_nick_name
        }
    return result

# 根据聊天类型发送消息的异步函数
async def answer_action(chat_type, user_id, group_id, at, response_message):
    # 根据是私发/群中@来组装不同发送参数,避免群中接话
    if chat_type == "group_at": # 群中@
        url = http_url + "/send_group_msg"
        at_string_user = f"[CQ:at,qq={user_id}]"
        params = {
            "group_id": group_id,
            "user_id": user_id, 
            "message": f"{at_string_user} " + response_message
        }  
    elif chat_type == "private": # 私聊
        url = http_url + "/send_private_msg"
        params = {
            "user_id": user_id, 
            "message": response_message
        } 
    elif chat_type == "group": # 群聊
        url = http_url + "/send_group_msg"
        params = {
            "group_id": group_id,
            "message": response_message
        } 
    else:
        url = http_url + "/send_private_msg"
        params = {
            "user_id": admin_id, 
            "message": f"{user_id} 发送了未知类型消息"
        } 
  
  
  
    # 如果是在config.py中允许的类型就发送消息  
    if response_message == "" or response_message is None:
        pass
    
    elif chat_type in chat_type_allow:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                # 检查响应状态码
                if response.status == 200:
                    print("=" * 50, "\n消息已成功发送\n\n")
                else:
                    print("=" * 50, "\n发送消息时出错:\n\n", await response.text())
    else:
        pass
