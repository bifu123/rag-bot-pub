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

# kimi 模型
from langchain_community.llms.moonshot import Moonshot

# groq api 模型
from langchain_groq import ChatGroq

# 异步函数
import asyncio




############################# API KEY #################################
# 将各个在线模型 API key 加入环境变量
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
os.environ["MOONSHOT_API_KEY"] = MOONSHOT_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
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
# 在线语言模型 kimi
llm_kimi = Moonshot(
    model_name = llm_kimi_conf["model_name"],
    temperature = llm_kimi_conf["temperature"]
) 
# 在线语言模型 groq
llm_groq = ChatGroq(
    model_name = llm_groq_conf["model_name"],
    temperature = llm_groq_conf["temperature"]
) 
# 本地语言模型 ChatGLM3
llm_chatGLM = ChatGLM3(
    endpoint_url = llm_chatGLM_conf["endpoint_url"],
    max_tokens = llm_chatGLM_conf["max_tokens"],
    top_p = llm_chatGLM_conf["top_p"]
)

############################# 模型选择 #################################
# 读取数据库
def get_models_on_request():
    models = get_models_table()
    must_use_llm_rag = models["must_use_llm_rag"]
    # 选择量化模型
    if models["embedding"] == "ollama":
        embedding = embedding_ollama
    else:
        embedding = embedding_google

    # 选择聊天语言模型
    if models["llm"] == "ollama":
        llm = llm_ollama
    elif models["llm"] == "gemini": 
        llm = llm_gemini
    elif models["llm"] == "tongyi": 
        llm = llm_tongyi
    elif models["llm"] == "kimi": 
        llm = llm_kimi
    elif models["llm"] == "groq": 
        llm = llm_groq
    else:
        llm = llm_chatGLM

    # 选择知识库语言模型
    if models["llm_rag"] == "ollama":
        llm_rag = llm_ollama
    elif models["llm_rag"] == "gemini": 
        llm_rag = llm_gemini
    elif models["llm_rag"] == "tongyi": 
        llm_rag = llm_tongyi
    elif models["llm_rag"] == "kimi": 
        llm_rag = llm_kimi
    elif models["llm_rag"] == "groq": 
        llm_rag = llm_groq
    else:
        llm_rag = llm_chatGLM
        
    return embedding, llm, llm_rag, must_use_llm_rag



############################# 模型方法 #################################
# gemini 聊天
async def chat_gemini(wxid, content, GMI_SERVER_URL):
    print("*" * 40)
    print("正在向llm提交...")
    try:
        response_text = requests.get(GMI_SERVER_URL).text
        json_response = json.loads(response_text)
        reply = json_response.get('reply')
        print("=" * 50, "\n",type(reply), reply)
        response_message = reply
    except Exception as e:
        response_message = f"LLM响应错误: {e}"
    return response_message

# 格式化聊天记录
def format_history(bot_nick_name, history):
    system_prompt = {"user": "system", "content": f"你好，我的名字叫{bot_nick_name}，我会尽力解答大家的问题."}
    result = []
    result.append(system_prompt)
    for item in history:
        result.append({"user": item[0], "content": item[1].replace(at_string, "")})
    return result

# 处理聊天记录
async def do_chat_history(chat_history, source_id, user, content, user_state, name_space):
    history_size_now = sys.getsizeof(f"{chat_history}")
    # 如果超过预定字节大小就放弃写入
    if not history_size_now > chat_history_size_set:
        # 插入当前数据表 source_id、query、result
        insert_chat_history(source_id, user, content, user_state, name_space)
        # 将聊天记录入旧归档记录表history_old.xlsx表中
        insert_chat_history_xlsx(source_id, user, content, user_state, name_space)
    else:
        print("记录过大，放弃写入")

# 向量检索聊天（执行向量链）
async def run_chain(bot_nick_name, user_nick_name, retriever, source_id, query, user_state="聊天", name_space="test"):
    embedding, llm, llm_rag, must_use_llm_rag = get_models_on_request()
    if query !="" and query is not None:
        print("=" * 50)
        print("当前使用的知识库LLM：", llm_rag)
        template_cn = """请根据上下文和对话历史记录用简体中文完整地回答问题 Please answer in Simplified Chinese:
        {context}
        {question}
        """
        

        # 处理聊天记录
        data = fetch_chat_history(source_id, user_state, name_space) # 从数据库中提取source_id的聊天记录
        chat_history = format_history(bot_nick_name, data)
        
        history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}") # 如果超过预定字节大小，删除记录
        print("=" * 50)
        print(f"预计聊天记录大小：{history_size_now}\n聊天记录：\n{chat_history}")
        
        while history_size_now > chat_history_size_set:
            if history_size_now > chat_history_size_set:
                delete_oldest_records(source_id, user_state, name_space) # 删除数据库中时间最旧的1条记录
                if chat_history and len(chat_history) > 1:
                    data.pop(0) # 删除chat_history中时间最旧的1条记录
                    chat_history = format_history(bot_nick_name, data)
                    history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}")
                    print("历史记录及问题字节之和超过预定值，删除时间最旧的1条记录")
                else:
                    print("聊天记录为空，无需删除")
                    break
            else:
                break  # 如果条件不再满足，则跳出循环
            
            
        # 由模板生成prompt
        prompt = ChatPromptTemplate.from_template(template_cn) 
        
        # 创建chain
        chain = RunnableMap({
            "context": lambda x: retriever.get_relevant_documents(x["question"]),
            "question": RunnablePassthrough(),
            "chat_history": lambda x: chat_history  # 使用历史记录的步骤
        }) | prompt | llm_rag | StrOutputParser()
        
        # 执行问答
        request = f'{{"user":"{user_nick_name}", "content":"{query}"}}'
        try:
            response_message = chain.invoke(request)
            # 处理聊天记录 
            await do_chat_history(chat_history, source_id, user_nick_name, query, user_state, name_space)
            await do_chat_history(chat_history, source_id, bot_nick_name, response_message, user_state, name_space)
        except Exception as e:
            response_message = f"LLM响应错误: {e}"
            print(f"LLM响应错误: {e}")
            
        # 返回结果
        return response_message + "😊"

# 通用聊天
async def chat_generic_langchain(bot_nick_name, user_nick_name, source_id, query, user_state="聊天",name_space="test"):
    embedding, llm, llm_rag, must_use_llm_rag = get_models_on_request()
    if query !="" and query is not None:
        # 处理聊天记录
        data = fetch_chat_history(source_id, user_state, name_space) # 从数据库中提取source_id的聊天记录
        chat_history = format_history(bot_nick_name, data)
        
        history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}") # 如果超过预定字节大小，删除记录
        print("=" * 50)
        print(f"预计聊天记录大小：{history_size_now}\n聊天记录：\n{chat_history}")
        
        while history_size_now > chat_history_size_set:
            if history_size_now > chat_history_size_set:
                delete_oldest_records(source_id, user_state, name_space) # 删除数据库中时间最旧的1条记录
                if chat_history and len(chat_history) > 1:
                    data.pop(0) # 删除chat_history中时间最旧的1条记录
                    chat_history = format_history(bot_nick_name, data)
                    history_size_now = sys.getsizeof(f"{chat_history}") + sys.getsizeof(f"{query}")
                    print("历史记录及问题字节之和超过预定值，删除时间最旧的1条记录")
                else:
                    print("聊天记录为空，无需删除")
                    break
            else:
                break  # 如果条件不再满足，则跳出循环

    
        # 由模板生成 prompt
        prompt = ChatPromptTemplate.from_template("""
            你是一个热心的人，尽力为人们解答问题，请用简体中文回答。Please answer in Simplified Chinese:
            {chat_history}
            {question}
        """)
        print("=" * 50)
        
        # 创建链，将历史记录传递给链
        if user_state != "聊天" and must_use_llm_rag == 1:
            chain = {
                "question": RunnablePassthrough(), 
                "chat_history": lambda x: chat_history,
            } | prompt | llm_rag | StrOutputParser()  
            print("当前使用的聊天LLM：", llm_rag)
        else:
            chain = {
                "question": RunnablePassthrough(), 
                "chat_history": lambda x: chat_history,
            } | prompt | llm | StrOutputParser()  
            print("当前使用的聊天LLM：", llm)

        # 执行问答
        request = f'{{"user":"{user_nick_name}", "content":"{query}"}}'
        try:
            response_message = chain.invoke(request)
            # 处理聊天记录 
            await do_chat_history(chat_history, source_id, user_nick_name, query, user_state, name_space)
            await do_chat_history(chat_history, source_id, bot_nick_name, response_message, user_state, name_space)
        except Exception as e:
            response_message = f"LLM响应错误: {e}"
            print(f"LLM响应错误: {e}")
            
        return response_message + "😊"



