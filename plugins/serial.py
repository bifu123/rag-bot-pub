

'''
本脚本向您演示了一个 串行模式 下的插件编写方式、脚本用几个函数演示一个加法的步骤。并示例了如果block=True,后面的函数不再执行
'''
import aiohttp
import asyncio
from models_load import *

# LLM调用所需参数
msg = 0 # 串行模式返回数值类型时需要
bot_nick_name = ""
user_nick_name = ""
user_state = ""
name_space = ""
source_id = ""
# LLM调用示例
# response_message = asyncio.run(chat_generic_langchain(bot_nick_name, user_nick_name, source_id, message, user_state, name_space))


################ 参数说明 #################
# priority:  插件的优先级，数值越小，越优先执行
# post_type: 来自onebot协议的类型
#             1. message: 消息事件
#             2. request: 请求事件
#             3. notice: 通知事件
#             4. meta_event: 元事件
# user_state: 当前用户（群）所处的状态
#             1. 聊天
#             2. 文档问答
#             3. 知识库问答
#             4. 网站问答
# data：      监听到的所有数据的json   
# block:      是否阻断拦截，如果为Ture，将会执行完当前函数就结束，不再往下一个函数执行
# name_space: 插件命名空间，用于精准定位到执行某一功能的一个或多个函数
# role:       拥有执行插件权限命名空间的微信号、微信群列表

# - 串行模式 serial：  所有函数结果会按照优先级执行，上一个函数结果是下一个函数的输入，最后一个函数的结果为最终结果。
# - 并行模式 parallel：所有函数结果会按照优先级执行，所有函数必须返回一个字符类型结果（可以是""），最后结果是所有函数的拼合。
# - 两种模式会最终在主程序中调用拼合，一并交给LLM推理。
# - 主函数中名必须与@装饰函数名一致。

# *** 插件问答是很消耗 Token 的




# 主函数
def fun_add(name_space, function_type, post_type, user_state, priority, role=[], block=False):
    def decorator(func):
        func._name_space = name_space
        func._function_type = function_type
        func._post_type = post_type
        func._priority = priority
        func._user_state = user_state
        func._role = role
        func._block = block
        return func
    return decorator

# 全局变量，仅当函数结果为数字时才需要
msg = 0

# 子函数示例1
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=0, role=["222302526","415135222"])
def fun_add_1(data={}): # 第一个函数的参数必须为字典类型
    
    # 第一个子函数中获取全局变量，并将全局变量中保存数据，因为如果在本插件中调用LLM时用到
    global msg
    global bot_nick_name
    global user_nick_name
    global user_state
    global name_space
    global source_id
    
    message = data["message"]
    bot_nick_name = data["bot_nick_name"]
    user_nick_name = data["user_nick_name"]
    source_id = data["source_id"]
    user_state = data["user_state"]
    name_space = data["name_space"]

    
    
    msg = 10000
    return msg

# 子函数示例2
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=1, role=["222302526","415135222"])
def fun_add_2(data):
    global msg
    msg += 1
    return msg

# 子函数示例3
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=2, role=["222302526","415135222"], block=True)
def fun_add_3(data):
    global msg
    msg += 1
    return f"每头猪的价钱是：{msg}元"





