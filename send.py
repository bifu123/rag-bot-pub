import aiohttp
import asyncio
from config import at_string, http_url, admin_qq, bot_qq, chat_type_allow

# 判断聊天类型函数
def get_chat_type(data):

    '''
    =============== Notice ===============
    {'post_type': 'notice', 'notice_type': 'offline_file', 'time': 1711607647, 'self_id': 1878085037, 'user_id': 415135222, 'file': {'name': 'tesla_p40.pdf', 'size': 106509, 'url': 'http://39.145.24.22/ftn_handler/5ad5075ff13463bc2cc7a6b2c8f8621bd15efb11953c58279f7830ae738fdb359f3cf19371d2b137843433fa5a71584023888c1f822a7962714c6f80268ab792'}}

    =============== Notice ===============
    {'post_type': 'notice', 'notice_type': 'group_upload', 'time': 1711608029, 'self_id': 1878085037, 'group_id': 499436648, 'user_id': 415135222, 'file': {'busid': 102, 'id': '/df9c709b-be79-4765-8d94-e1e1f2b13727', 'name': 'tesla_p40.pdf', 'size': 106509, 'url': 'http://223.109.208.144/ftn_handler/226e5a1946afd217ffcf5bee0f759dc6654d1dfc89512a268be65828a5aa23f7647bfbfb928a106f6d7de6321fd87743352758c00e9f518feb325812044651cf/?fname=2f64663963373039622d626537392d343736352d386439342d653165316632623133373237'}}

    {'post_type': 'notice', 'notice_type': 'group_upload', 'time': 1712133142, 'self_id': 3787687088, 'group_id': 499436648, 'user_id': 415135222, 'file': {'busid': 102, 'id': '/b479c4f6-1e62-4a07-ba22-788589158251', 'name': '岳飞简介.txt', 'size': 1407, 'url': 'http://39.145.18.42/ftn_handler/68a27d5c9fc808f171b8537343553a0426d5213b5d57e01e1c60e9d4d845bc976febff7b6c65326845da715c8c359ba3639a38866a60db48fe77917315ab5cac/?fname=2f62343739633466362d316536322d346130372d626132322d373838353839313538323531'}}

    =============== 批准入群 ==============
    {'post_type': 'notice', 'notice_type': 'group_increase', 'time': 1711826628, 'self_id': 3152246598, 'sub_type': 'approve', 'group_id': 222302526, 'operator_id': 0, 'user_id': 990154420}
    '''
    
    user_id = data["user_id"]

    # 消息类型
    if data["post_type"] == "message":
        if data["message_type"] == "private":
            chatType = "private"
            group_id = "no"
            at = "no"
        elif data["message_type"] == "group":
            group_id = data["group_id"]
            if at_string in data["message"]:
                chatType = "group_at"
                at = "no"
            else:
                chatType = "group"
                at = "no"
        else:
            chatType = data["message_type"]
            group_id = "no"
            at = "no"

    # 事件类型
    if data["post_type"] == "notice":
        # 私发离线文件
        if data["notice_type"] == "offline_file":
            chatType = "private"
            group_id = "no"
            at = "no"
        # 群文件
        elif data["notice_type"] == "group_upload":
            group_id = data["group_id"]
            chatType = "group_at"
            at = "no"
        else:
            chatType = data["notice_type"]
            group_id = "no"
            at = "no"

    return {"chatType": chatType, "user_id": str(user_id), "group_id": str(group_id), "at": at}

# 根据聊天类型发送消息的异步函数
async def answer_action(chat_type, user_id, group_id, at, response_message):
    '''
    data : 监听到的用户发来的消息内容
    response_message : 回复的消息内容
    '''
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
            "user_id": admin_qq, 
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
                    print("=" * 40, "\n消息已成功发送\n\n")
                else:
                    print("=" * 40, "\n发送消息时出错:\n\n", await response.text())
    else:
        pass
