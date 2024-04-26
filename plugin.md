# 怎样开发插件

- YLBot的插件理念不同于以往任意一个机器人，它不局限SQL查询，它关注自动化和更智能的语义理解，插件的作用是给LLM提供我们预定内容的上下文，它完全依赖语言模型的推理能力，得出答案和结果。

- 插件必须放在./plugins目录下，一个python文件就是一个插件，文件里必须是函数

![插件示意图](images/插件示意图.png)


<!-- ################ 参数说明 #################
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
#             5. 插件问答
# data：      监听到的所有数据的json   
# block:      是否阻断拦截，如果为Ture，将会执行完当前函数就结束，不再往下一个函数执行
# name_space: 功能的命名空间，用于区分不同的功能。前端交互方法与状态切换是一样的，只是写法不同，比如 ::天气查询。


# - 串行模式 serial：  所有函数结果会按照优先级执行，上一个函数结果是下一个函数的输入，最后一个函数的结果为最终结果。
# - 并行模式 parallel：所有函数结果会按照优先级执行，所有函数必须返回一个字符类型结果（可以是""），最后结果是所有函数的拼合。
# - 两种模式会最终在主程序中调用拼合，一并交给LLM推理。
# - 主函数中名必须与@装饰函数名一致。

# *** 插件问答是很消耗 Token 的 -->

## 串行模式
```python

# 主函数
def fun_add(name_space, function_type, post_type, user_state, priority, block=False):
    def decorator(func):
        func._name_space = name_space
        func._function_type = function_type
        func._post_type = post_type
        func._priority = priority
        func._user_state = user_state
        func._block = block
        return func
    return decorator

# 全局变量
msg = 0

# 子函数示例1
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=0)
def fun_add_1(data={}): # 第一个函数的参数必须为字典类型
    global msg
    msg = 10000
    return msg

# 子函数示例2
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=1, block=True)
def fun_add_2(data):
    global msg
    msg += 1
    return msg

# 子函数示例3
@fun_add(name_space="test", function_type="serial", post_type="message", user_state="插件问答", priority=2)
def fun_add_3(data):
    global msg
    msg += 1
    return msg
```

## 并行模式
```python
################# 主函数 ##################
def fun_my_plugin(name_space, function_type, post_type, user_state, priority, block=False):
    def decorator(func):
        func._name_space = name_space
        func._function_type = function_type
        func._post_type = post_type
        func._priority = priority
        func._user_state = user_state
        func._block = block
        return func
    return decorator





################# 子函数 ##################
# 插件函数示例1
@fun_my_plugin(name_space="test", function_type="parallel", post_type="message", user_state="插件问答", priority=3)
def fun_1(data):
    msg = f"他今年45岁了"
    # 必须返回字符结果
    return msg

# 插件函数示例2
@fun_my_plugin(name_space="test", function_type="parallel", post_type="message", user_state="插件问答", priority=4, block=True)
def fun_2(data):
    msg = f"他喜欢国学文化"
    return msg

# 插件函数示例3
@fun_my_plugin(name_space="test", function_type="parallel", post_type="message", user_state="插件问答", priority=5)
def fun_3(data):
    msg = f"元龙居士原来是一个养猪的人"
    return msg
```

总程序会将串行、并行两种模式的所有结果全部交给LLM综合分析推理。




