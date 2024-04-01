from config import at_string, http_url, admin_qq, bot_qq, chat_type_allow
import requests


# 判断聊天类型函数
def get_chat_type(data):

    user_id = data["user_id"]

    if data["post_type"] == "message" and data["message_type"] == "private":
        chatType = "private"
        group_id = "no"
        at = "no"
    elif data["post_type"] == "message" and data["message_type"] == "group":
        group_id = data["group_id"]
        if at_string in data["message"]:
            chatType = "group_at"
            at = "no"
        else:
            chatType = "group"
            at = "no"
    else:
        chatType = "Unkown"
    return {"chatType":chatType, "user_id": str(user_id), "group_id": str(group_id), "at": at}

# 根据聊天类型发送消息的函数
def answer_action(chat_type, user_id, group_id, at, response_message):
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
    if chat_type in chat_type_allow and response_message != "" and response_message is not None:
        response = requests.post(url, params=params)  

        # 检查响应状态码
        if response.status_code == 200:
            print("="*40, "\n消息已成功发送\n\n")
        else:
            print("="*40, "\n发送消息时出错:\n\n", response.text)  
