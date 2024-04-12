
########## 固定代码块，请勿改动 ############

# 主函数
def fun_my_plugin(post_type, user_state, priority, block=False):
    def decorator(func):
        func._post_type = post_type
        func._priority = priority
        func._user_state = user_state
        func._block = block
        return func
    return decorator
##########################################

'''

priority:  插件的优先级，数值越小，越优先执行
post_type: 来自onebot协议的类型
            1. message: 消息事件
            2. request: 请求事件
            3. notice: 通知事件
            4. meta_event: 元事件
user_state: 当前用户（群）所处的状态
            1. 聊天
            2. 文档问答
            3. 知识库问答
            4. 网站问答
data：      监听到的所有数据的json   
block:      是否阻断拦截，如果为Ture，将会执行完当前函数就结束，不再往下一个函数执行

'''

# 插件函数示例1
@fun_my_plugin(post_type="message", user_state="插件问答", priority=2)
def fun_1(data):
    '''
    功能代码逻辑
    '''
    msg = f"他今年45岁了"
    # 必须返回字符结果
    return msg

# 插件函数示例2
@fun_my_plugin(post_type="message", user_state="插件问答", priority=1, block=True)
def fun_2(data):
    msg = f"他喜欢国学文化"
    return msg

# 插件函数示例3
@fun_my_plugin(post_type="message", user_state="插件问答", priority=0)
def fun_3(data):
    msg = f"元龙居士原来是一个养猪的人"
    return msg

'''
- 所有插件必须返回一个字符类型结果，所有函数结果会按照优先级执行得出后自动拼接,作为交给LLM的上下文的一部分，让LLM在当中推理答案
- 主函数中名必须与@装饰函数名一致
'''
