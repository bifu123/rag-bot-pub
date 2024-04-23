# 导入langchain_community包
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from sqlite_helper import *
# 语义检索
from langchain.schema.runnable import RunnableMap
from langchain_core.runnables import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
# 异步函数
import asyncio
import os
import sys

# 创建一个 Ollama 实例
llm = Ollama(
    base_url="http://192.168.66.26:11434",
    model="llama3:8b"
)

# 获取聊天记录
def get_chat_history(data):
    res = []
    history_size_old = sys.getsizeof(f"{data}")
    print("*" * 50)
    print(f"以前聊天记录大小：{history_size_old}")
    for item in data:
        res.append({"query": item[0], "answer": item[1]+'<|end_of_text|>'})
        print("*" * 50)
        print(f"以前聊天记录：{res}")
    return res

# 通用聊天
async def chat_generic_langchain(source_id, query, user_state="聊天"):
    print("*" * 50)
    print("当前使用的聊天LLM：", llm)
    # 从数据库中提取 source_id 的聊天记录
    data = fetch_chat_history(source_id, user_state)
    chat_history = get_chat_history(data)
    # 聊天
    # try:
    # 由模板生成 prompt
    prompt = ChatPromptTemplate.from_template("""
        你是一个热心的人，尽力为人们解答各种问题。请告诉我你的答案，不要添加其他格式。
        {chat_history}
        {question}
    """)
    
    # 创建链，将历史记录传递给链
    chain = {
        "question": RunnablePassthrough(), 
        "chat_history": lambda x: chat_history,
    } | prompt | llm | StrOutputParser()  

    # 调用链进行问答
    response_message = f"{chain.invoke(query)}"
    # 处理聊天记录 
    # await do_chat_history(chat_history, source_id, query, response_message, user_state)
    # except Exception as e:
    #     response_message = f"通用聊天 chat_generic_langchain 错误：{e}"
        
    return response_message
  
  
response_message = asyncio.run(chat_generic_langchain("415135222", "你好", "聊天"))
print(response_message)
