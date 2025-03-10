import sys
from sqlite_helper import insert_chat_history_to_db, fetch_chat_history, delete_oldest_records
from config import chat_history_size_set
# from config import at_string

# 格式化聊天记录
def format_chat_history(bot_nick_name, history):
    system_prompt = {"user": "system", "content": f"你好，我的名字叫{bot_nick_name}，我会尽力解答大家的问题."}
    result = []
    result.append(system_prompt)
    for item in history:
        result.append({"user": item[0], "content": item[1]})
    return result

# 获取聊天记录
def get_chat_history(bot_nick_name, query, source_id, user_state, name_space):
    
    data = fetch_chat_history(source_id, user_state, name_space) # 从数据库中提取source_id的聊天记录
    chat_history = format_chat_history(bot_nick_name, data)
    
    history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}") # 如果超过预定字节大小，删除记录
    print("=" * 50)
    print(f"预计聊天记录大小：{history_size_now}\n聊天记录：\n{chat_history}")
    
    while history_size_now > chat_history_size_set:
        if history_size_now > chat_history_size_set:
            delete_oldest_records(source_id, user_state, name_space) # 删除数据库中时间最旧的1条记录
            if chat_history and len(chat_history) > 1:
                data.pop(0) # 删除chat_history中时间最旧的1条记录
                chat_history = format_chat_history(bot_nick_name, data)
                history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}")
                print("历史记录及问题字节之和超过预定值，删除时间最旧的1条记录")
            else:
                print("聊天记录为空，无需删除")
                break
        else:
            break  # 如果条件不再满足，则跳出循环
    return chat_history

# 写入聊天记录
def insert_chat_history(content, source_id, user, user_state, name_space):
    if content != "" and content is not None:
        content_size = sys.getsizeof(f"{content}")
        # 如果超过预定字节大小就放弃写入
        if not content_size > chat_history_size_set:
            # 插入当前数据表 source_id、query、result
            insert_chat_history_to_db(source_id, user, content, user_state, name_space)
            # 将聊天记录入旧归档记录表history_old.xlsx表中
            # insert_chat_history_to_excel(source_id, user, content, user_state, name_space)
        else:
            print("记录过大，放弃写入")
    else:
        print("记录为空，放弃写入")
            

    
    
    
    