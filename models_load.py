import os
import sys
import requests
import json

from config import *
from sqlite_helper import *


# ollama模型
from langchain_community.embeddings import OllamaEmbeddings # 量化文档
from langchain_community.llms import Ollama #模型

# 提示词模板
from langchain_core.prompts import ChatPromptTemplate

# gemini模型
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# 通义千问模型
from langchain_community.llms import Tongyi
import dashscope

# 语义检索
from langchain.schema.runnable import RunnableMap
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# chatGLM3-6B 模型
from langchain_community.llms.chatglm3 import ChatGLM3

# 异步函数
import asyncio




############################# API KEY #################################
# 将各个在线模型 API key 加入环境变量
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
############################# 量化模型 #################################
# 本地量化模型
embedding_ollama = OllamaEmbeddings(
    base_url = embedding_ollama_conf["base_url"], 
    model = embedding_ollama_conf["model"]
) 
# 线上google量化模型
embedding_google = GoogleGenerativeAIEmbeddings(
    model = embedding_google_conf["model"]
) 
# embedding_google.embed_query("hello, world!")
############################# 语言模型 #################################
# 本地语言模型
llm_ollama = Ollama(
    base_url = llm_ollama_conf["base_url"], 
    model = llm_ollama_conf["model"]
)
# 在线语言模型 gemini
llm_gemini = ChatGoogleGenerativeAI(
    model = llm_gemini_conf["model"],
    temperature = llm_gemini_conf["temperature"]
) 
# 在线语言模型 通义千问
llm_tongyi = Tongyi(
    model_name = llm_tongyi_conf["model_name"],
    temperature = llm_tongyi_conf["temperature"],
    streaming = llm_tongyi_conf["streaming"]
    #enable_search = True
) 
# 本地语言模型 ChatGLM3
llm_chatGLM = ChatGLM3(
    endpoint_url = llm_chatGLM_conf["endpoint_url"],
    max_tokens = llm_chatGLM_conf["max_tokens"],
    top_p = llm_chatGLM_conf["top_p"]
)

############################# 模型选择 #################################
# 选择量化模型
if model_choice["embedding"] == "ollama":
    embedding = embedding_ollama
else:
    embedding = embedding_google
# 选择语言模型
if model_choice["llm"] == "ollama":
    llm = llm_ollama
elif model_choice["llm"] == "gemini": 
    llm = llm_gemini
elif model_choice["llm"] == "tongyi": 
    llm = llm_tongyi
else:
    llm = llm_chatGLM



############################# 模型方法 #################################
# gemini 聊天
async def chat_gemini(wxid, content, GMI_SERVER_URL):
    print("*" * 40)
    print("正在向llm提交...")
    try:
        response_text = requests.get(GMI_SERVER_URL).text
        json_response = json.loads(response_text)
        reply = json_response.get('reply')
        print("="*40, "\n",type(reply), reply)
        response_message = reply
    except Exception as e:
        response_message = "LLM响应错误"
    return response_message

# 获取聊天记录
def get_chat_history(data) -> list:
    res = []
    history_size_old = sys.getsizeof(f"{data}")
    print("*" * 50)
    print(f"以前聊天记录大小：{history_size_old}")
    for item in data:
        res.append({"query": item[0], "answer": item[1]})
        print("*" * 50)
        print(f"以前聊天记录：{res}")
    return res

# 处理聊天记录
async def do_chat_history(chat_history, source_id, query, answer, user_state):
    # 插入当前数据表 source_id、query、result
    insert_chat_history(source_id, query, answer, user_state)
    # 将聊天记录入旧归档记录表history_old.xlsx表中
    insert_chat_history_xlsx(source_id, query, answer, user_state)
    # 当聊天记录数量超过2048时，删除数据库记录表history_now中时间最晚的两条记录
    history_size_now = sys.getsizeof(f"{chat_history}")
    print("*" * 50)
    print(f"当前聊天记录大小：{history_size_now}")
    # 如果超过预定字节大小，就删除数据库中时间最旧的两条记录
    if history_size_now > chat_history_size_set:
        delete_oldest_records()
        print("删除了数据库中时间最旧的两条记录")

# 向量检索聊天（执行向量链）
async def run_chain(retriever, source_id, query, user_state="聊天"):
    template_cn = """请根据上下文和对话历史记录完整地回答问题:
    {context}
    {question}
    """
    # 从数据库中提取source_id的聊天记录
    data = fetch_chat_history(source_id, user_state)
    if data:
        chat_history = get_chat_history(data)
    else:
        chat_history = []
    # 由模板生成prompt
    prompt = ChatPromptTemplate.from_template(template_cn) 
    # 创建chain
    chain = RunnableMap({
        "context": lambda x: retriever.get_relevant_documents(x["question"]),
        "question": RunnablePassthrough(),
        "chat_history": lambda x: chat_history  # 使用历史记录的步骤
    }) | prompt | llm | StrOutputParser()
    # 执行问答
    request = {"question": query}
    answer = chain.invoke(request)
    # 处理聊天记录 
    await do_chat_history(chat_history, source_id, query, answer, user_state)
    # 返回结果
    return answer

# 通用聊天
async def chat_generic_langchain(source_id, query, user_state="聊天"):
    # 从数据库中提取 source_id 的聊天记录
    data = fetch_chat_history(source_id, user_state)
    chat_history = get_chat_history(data)
    # 聊天
    # try:
    # 由模板生成 prompt
    prompt = ChatPromptTemplate.from_template("""
        你是一个热心的人，尽力为人们解答各种问题。请回答下面的问题：
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
    await do_chat_history(chat_history, source_id, query, response_message, user_state)
    # except Exception as e:
    #     response_message = f"通用聊天 chat_generic_langchain 错误：{e}"
        
    return response_message



