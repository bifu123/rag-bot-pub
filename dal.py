# 从内置模块导入
import os
import shutil
import json
import sys
from sys import argv
import re
import base64
import importlib.util
import inspect


# 从文件导入
from models_load import *
from send import *
from sqlite_helper import *
from models_load import *

# 文档加工
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, PythonLoader 
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter # 分割文档
from langchain_community.vectorstores import Chroma # 量化文档数据库


# 链结构
from langchain.chains import RetrievalQA #链

# 语义检索
from langchain.schema.runnable import RunnableMap
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# 站点地图
import xml.dom.minidom
import datetime
from urllib import request
from bs4 import BeautifulSoup


from pathlib import Path

# 异步函数
import asyncio
import aiohttp





# 加载 embedding 过程
def load_retriever(db_path, embedding):
    vectorstore_from_db = Chroma(
        persist_directory = db_path,         # Directory of db
        embedding_function = embedding       # Embedding model
    )
    retriever = vectorstore_from_db.as_retriever()
    return retriever

# 检查文件的函数
def check_file_extension(file_name, allowed_extensions):
    # # 示例用法
    # file_name = "example.docx"
    # if check_file_extension(file_name）:
    #     print("File extension is allowed.")
    # else:
    #     print("File extension is not allowed.")
    file_ext = file_name[file_name.rfind("."):].lower()
    return file_ext in allowed_extensions

# 定义下载文件的函数
def download_file(url: str, file_name: str, download_path: str, allowed_extensions):
    allowed_extensions = allowed_extensions
    if check_file_extension(file_name, allowed_extensions):
        # 下载文件
        response = requests.get(url)

        if response.status_code == 200:
            # 检查下载目录是否存在，如果不存在则创建
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            
            # 将文件保存到指定路径
            file_path = os.path.join(download_path, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            msg = f"文件成功保存: {file_path}"
        else:
            msg = f"文件上传失败： {response.status_code}"
    else:
        extensions_string = ", ".join(allowed_extensions)
        msg = f"你上传的文件我将不会保存到服务器上，它只会保存在群文件里。我能为你保存这些文件类型：{extensions_string}"
    return msg

# 显示文件夹下所有文件的函数
def get_files_in_directory(directory):
    directory_path = Path(directory)
    files = []
    for item in directory_path.iterdir():
        if item.is_file():
            files.append(str(item.resolve()))  # 将文件的绝对路径添加到列表中
        elif item.is_dir():
            files.extend(get_files_in_directory(item))  # 递归获取子文件夹中的文件
    return files

# 从数据库中读取当前群的允许状态
def get_allow_state(data):
    # 读取群消息开关
    try:
       allow_state = get_allow_state_from_db(str(data["group_id"]))
       if allow_state == "on":
           chat_type_allow = ["private", "group", "group_at"]
       else:
           chat_type_allow = ["private", "group_at"]
    except:
        chat_type_allow = ["private", "group_at"]
    return chat_type_allow

# 匹配URL的函数
def get_urls(text):
    # 定义一个正则表达式模式，用于匹配URL
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/\S*'
    # 使用findall函数查找文本中所有匹配的URL
    urls = re.findall(url_pattern, text)
    # 如果找到了URL，则返回True，否则返回False
    if urls:
        # # 打印找到的所有URL
        # for url in urls:
        #     print(url)
        # 将URL列表编码为BASE64字符串
        encoded_urls = base64.b64encode(json.dumps(urls).encode()).decode()   
        return "yes", encoded_urls
    else:
        return "no", "nourl"

# 匹配图片的函数
def get_image(text):
    # 使用正则表达式进行匹配
    pattern = r'\[CQ:image,file=(.*?),subType=\d+,url=(.*?)\]'
    matches = re.findall(pattern, text)

    # 如果匹配成功，返回 URL 地址和 True
    if matches:
        url = matches[0][1]
        return True, url
    else:
        return False, None

# 匹配命名空间命令
def get_name_space(text):
    pattern = r"::[^:]+"
    matches = re.findall(pattern, text)
    if matches:
        return True, matches[0]
    else:
        return False, None


# 加载插件、构建query的函数
def get_response_from_plugins(name_space_p, post_type_p, user_state_p, data):
    # 存储每个函数的结果
    try:
        message = str(data["message"])
    except:
        message = ""

    plugin_dir = 'plugins'


    results = []
    # 遍历plugins目录下的所有文件
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py'):
            plugin_path = os.path.join(plugin_dir, filename)
            # 动态导入模块
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # 获取模块中的所有函数及其优先级
            functions_with_priority = [(getattr(plugin_module, func), getattr(plugin_module, func)._name_space, getattr(plugin_module, func)._priority, getattr(plugin_module, func)._function_type, getattr(plugin_module, func)._post_type, getattr(plugin_module, func)._user_state) for func in dir(plugin_module) if callable(getattr(plugin_module, func)) and hasattr(getattr(plugin_module, func), '_priority')]
            
            # 根据优先级对函数进行排序
            functions_with_priority.sort(key=lambda x: x[1])
            
            result_serial = None  # 初始值设为None
            result_parallel = ''  # 用于并行执行的结果串联
            # 依次执行函数
            for function, name_space, priority, function_type, post_type, user_state in functions_with_priority:
                # 判断function_type、post_type和user_state是否满足特定条件
                if function_type == "serial" and post_type == post_type_p and user_state == user_state_p and name_space == name_space_p:
                    if result_serial is None:
                        # 如果result为None，则根据函数参数类型设定初始值
                        if 'dict' in str(function.__annotations__.values()):
                            result_serial = {}
                        elif 'str' in str(function.__annotations__.values()):
                            result_serial = ''
                        # 可以根据其他可能的参数类型继续添加条件
                    result_serial = function(data=result_serial)  # 将data作为参数传递给函数
                    # 如果block=True，则结束循环，不再执行后续函数
                    if getattr(function, '_block', False):
                        break
                elif function_type == "parallel" and post_type == post_type_p and user_state == user_state_p and name_space == name_space_p:
                    result_parallel += f"{function(data)}"
                    result_parallel += "\n"
            
            # 将每个函数的结果存储起来
            results.append(f"{result_parallel}" + "\n" + f"{result_serial}")
    
    # 将所有结果组合起来
    result = "\n".join(results)

    # 输出结果
    print(f"插件返回结果：{result}")
    # 准备问题（将从插件获取的结果与当前问题拼接成上下文供LLM推理)
    query = f"{result}" + f"{message}"
    return query


# 获取当前用户状态
def get_user_state_from_db(user_id, source_id):
    # 获取当前用户状态
    user_state = get_user_state(user_id, source_id)
    if user_state is None:
        user_state = "聊天"
        switch_user_state(user_id, source_id, "聊天")
    return user_state

#**************** 消息处理 ********************************************
def message_action(data):

    # 获取当前群允许的聊天类型
    chat_type_allow = get_allow_state(data)
    print("="*40, "\n","当前允许的聊天消息类型：", chat_type_allow)

    # 判断聊天类型、获得必要参数
    '''
    {'chatType': 'group_at', 'user_id': '415135222', 'group_id': '499436648', 'at': True}
    '''
    chat_type = get_chat_type(data)["chatType"]
    at = get_chat_type(data)["at"]
    user_id = get_chat_type(data)["user_id"]
    group_id = get_chat_type(data)["group_id"]
  
    print("="*40)
    print(f"chat_type:{chat_type}\nat:{at}\nuser_id:{user_id}\ngroup_id:{group_id}")

    # 组装文件路径
    message = data["message"]
    print("="*40, "\n",f"问题：{message}")
    user_data_path = os.path.join(data_path, user_id)
    user_db_path = os.path.join(db_path, user_id)
    
    # 确定用户数据库目录和文档目录
    if chat_type in ("group_at", "group"):
        source_id = group_id
        embedding_data_path = os.path.join(data_path, "group_"+ group_id)
        embedding_db_path_tmp = os.path.join(db_path, "group_"+ group_id)
        embedding_db_path_tmp_site = os.path.join(db_path, "group_"+ group_id + "_site")
    elif chat_type == "private":
        source_id = user_id
        embedding_data_path = user_data_path
        embedding_db_path_tmp = user_db_path
        embedding_db_path_tmp_site = user_db_path + "_site"

    # 获取name_space
    print("="*40)
    name_space = get_user_name_space(user_id, source_id)
    print("当前命名空间：", name_space)

    # 读取数据库当前source_id的存储路径
    if get_path_by_source_id(source_id) is None:
        insert_into_db_path(source_id, embedding_db_path_tmp) # 如果没有记录则插入
        insert_into_db_path_site(source_id, embedding_db_path_tmp_site)
        embedding_db_path = embedding_db_path_tmp
        embedding_db_path_site = embedding_db_path_tmp_site
    else:
        embedding_db_path = get_path_by_source_id(source_id) # 如果存在则直接使用
        embedding_db_path_site = get_path_by_source_id_site(source_id) # 如果存在则直接使用



    print("="*40, "\n",f"source_id：{source_id}")     
    print("="*40, "\n",f"当前使用的文档路径：{embedding_data_path}")
    print("="*40, "\n",f"当前使用的数据库路径：{embedding_db_path}")
    print("="*40, "\n",f"当前使用的网站向量路径：{embedding_db_path_site}")

    # 以 | 分割找出其中的命令
    command_parts = message.split("|")
    command_name = command_parts[0]
    print("="*40, "\n",f"当前命令：{command_name}") 


    # 如果字符中包含URL，但不包含图片则启动URL解读
    matches = get_image(message)[0]
    print("是否包含图片：", matches)  
    if get_urls(message)[0] == "yes" and matches == False:
        current_state = get_user_state_from_db(user_id, source_id)
        try:
            question = "请用中文对以上内容解读，并输出一个结论"
            command = f"start cmd /c \"conda activate rag-bot && python url_chat.py {get_urls(message)[1]} {question} {chat_type} {user_id} {group_id} {at} {source_id} {current_state}\"" # 不用等待新打开的窗口执行完成
            os.system(command)
        except Exception as e:
            print(f"URL错误：{e}")
        response_message = ""


    # 如果包含命名空间命令，则切换命名空间
    is_name_space_command, name_space_command = get_name_space(message)


    # 在允许回复的聊天类型中处理
    if chat_type in chat_type_allow and get_urls(message)[0] == "no": 
       
        if is_name_space_command == True:
            # 切换当前用命名空间
            name_space_command = name_space_command.replace("::", "")
            switch_user_name_space(user_id, source_id, name_space_command)
            response_message = f"已切换到 【{name_space_command}】 命名空间"
            
        else: 
            # 命令： /我的文档 
            if command_name in ("/我的文档", f"{at_string} /我的文档"):
                print("命令匹配！")
                try:
                    all_file = get_files_in_directory(embedding_data_path)
                    files_str = "\n".join(all_file)  # 将文件列表转换为单一的字符串，每个文件路径占一行
                    if len(files_str) > 0:
                        if chat_type in ("group_at", "group"):
                            response_message = "以下是你们的知识库文档：\n\n" + files_str + "\n\n如果要删除，请输使用删除命令： /删除文档|完整路径的文件名"
                        else:
                            response_message = "以下是你的知识库文档：\n\n" + files_str + "\n\n如果要删除，请输使用删除命令： /删除文档|完整路径的文件名"
                    else:
                        response_message = "你还没有文档，请先给我发送你的文档。（必须在【文档问答】或者【知识库问答】状态下，我才会保存）"
                except:
                    response_message = "你还没有文档，请先给我发送你的文档。（必须在【文档问答】或者【知识库问答】状态下，我才会保存）"

            # 命令： /删除文档 
            elif command_name in ("/删除文档", f"{at_string} /删除文档"):
                # 取得文件名
                try:
                    file_path = command_parts[1]
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        response_message = f"文件 '{file_path}' 已成功删除。注：聊天软件里的同名文档不会被清除，请手动删除"
                    else:
                        response_message = f"文件 '{file_path}' 不存在，无法删除"
                except:
                    response_message = "命令错误"

            # 命令： /清空文档 
            elif command_name in ("/清空文档", f"{at_string} /清空文档"):
                # 取得文件名
                try:
                    if os.path.exists(user_data_path):
                        shutil.rmtree(user_data_path)
                        response_message = f"文件 '{user_data_path}' 下所有文件已成功删除。注：聊天软件里的同名文档不会被清除，请手动删除"
                    else:
                        response_message = f"文件夹 '{user_data_path}' 不存在，无法删除"
                except:
                    response_message = "命令错误"
                            
            # 命令： /量化文档 
            elif command_name in ("/量化文档", f"{at_string} /量化文档"):
                embedding_type = "file"
                try:
                    # 新开窗口量化到新目录
                    #command = f"start /wait cmd /c \"python new_embedding.py {embedding_data_path} {embedding_db_path} {source_id} {chat_type} {user_id} {group_id} {at}\"" # 等待新打开的窗口执行完成
                    command = f"start cmd /c \"conda activate rag-bot && python new_embedding.py {embedding_data_path} {embedding_db_path} {source_id} {chat_type} {user_id} {group_id} {at} {embedding_type}\"" # 不用等待新打开的窗口执行完成
                    # 使用 os.system() 执行命令
                    os.system(command)
                    response_message = "正在量化，完成后另行通知，这期间你仍然可以使用你现在的文档知识库"
                except Exception as e:
                    response_message = f"量化失败：{e}"

            # 命令： /量化网站 
            elif command_name in ("/量化网站", f"{at_string} /量化网站"):
                embedding_type = "site"
                site_url = base64.b64encode(json.dumps(command_parts[1]).encode()).decode()
                try:
                    # question = "请对以上内容解读，并输出一个结论"
                    command = f"start cmd /c \"conda activate rag-bot && python new_embedding.py {embedding_data_path} {embedding_db_path_site} {source_id} {chat_type} {user_id} {group_id} {at} {embedding_type} {site_url}\""
                    os.system(command)
                except Exception as e:
                    print(f"URL错误：{e}")
                response_message = "这将需要很长、很长的时间...不过你可以问我些其它事"

            # 命令： /上传文档 
            elif command_name in ("/上传文档", f"{at_string} /上传文档"):
                # 取得文件名
                response_message = "请直接发送文档"

            # 命令： /文档问答 
            elif command_name in ("/文档问答", f"{at_string} /文档问答"):
                # 切换到 文档问答 状态
                # 用数据库保存每个用户的状态
                switch_user_state(user_id, source_id, "文档问答")
                response_message = "你己切换到 【文档问答】 状态。其它状态命令：\n/聊天\n/网站问答\n/知识库问答"
            
            # 命令： /网站问答 
            elif command_name in ("/网站问答", f"{at_string} /网站问答"):
                # 切换到 文档问答 状态
                # 用数据库保存每个用户的状态
                switch_user_state(user_id, source_id, "网站问答")
                response_message = "你己切换到 【网站问答】 状态。其它状态命令：\n/聊天\n/文档问答\n/知识库问答\n插件问答" 

            # 命令： /知识库问答 
            elif command_name in ("/知识库问答", f"{at_string} /知识库问答"):
                # 切换到 文档问答 状态
                # 用数据库保存每个用户的状态
                switch_user_state(user_id, source_id, "知识库问答")
                response_message = "你己切换到 【知识库问答】 状态。其它状态命令：\n/聊天\n/文档问答\n/网站问答\n插件问答"   

            # 命令： /聊天 
            elif command_name in ("/聊天", f"{at_string} /聊天"):
                # 切换到 聊天 状态
                # 用数据库保存每个用户的状态
                switch_user_state(user_id, source_id, "聊天")
                response_message = "你己切换到 【聊天】 状态。其它状态命令：\n/网站问答\n/文档问答\n/知识库问答\n插件问答" 

            # 命令： /插件问答
            elif command_name in ("/插件问答", f"{at_string} /插件问答"):
                switch_user_state(user_id, source_id, "插件问答")
                response_message = "你己切换到 【插件问答】 状态。其它状态命令：\n聊天\n/网站问答\n/文档问答\n/知识库问答" 

            # 命令： /我的状态 
            elif command_name in ("/我的状态", f"{at_string} /我的状态"):
                # 从数据库中查找用户当前状态
                current_state = get_user_state_from_db(user_id, source_id)
                response_message = f"【{current_state}】"
            
            # 命令： /我的命名空间 
            elif command_name in ("/我的命名空间", f"{at_string} /我的命名空间"):
                # 从数据库中查找用户当前状态
                current_state = get_user_name_space(user_id, source_id)
                if current_state == "no":
                    response_message = "你当前所在聊天对象中还没有插件，你可以创建插件，或用 ::命名空间 的命令切换到已有的插件命名空间"
                else:
                    response_message = "【" + current_state + "】"
            
            # 命令： /开启群消息 
            elif command_name in ("/开启群消息", f"{at_string} /开启群消息"):
                try:
                    switch_allow_state(str(data["group_id"]), "on")
                    response_message = "现在不管谁说话，我都会在群里回答，如果嫌小的话多，你就发 /关闭群消息"
                except Exception as e:
                    response_message = f"群消息开启失败：{e}"

            # 命令： /关闭群消息 
            elif command_name in ("/关闭群消息", f"{at_string} /关闭群消息"):
                try:
                    switch_allow_state(str(data["group_id"]), "off")
                    response_message = "好的，小的先行告退，就不插嘴各位大人的聊天了，有需要时@我"
                except Exception as e:
                    response_message = f"群消息关闭失败：{e}"

            # 命令： /清空记录 
            elif command_name in ("/清空记录", f"{at_string} /清空记录"):
                try:
                    current_state = get_user_state_from_db(user_id, source_id)
                    delete_all_records(source_id, current_state)
                    response_message = "消息已经清空"
                except Exception as e:
                    response_message = f"消息清空失败：{e}"

            # 和 LLM 对话
            else:
                current_state = get_user_state_from_db(user_id, source_id) # 先检查用户状态
                print(f"当前状态：{current_state}")
                # 当状态为文档问答
                if current_state == "知识库问答":
                    # 调用RAG
                    print(f"加载 {embedding_db_path} 的向量知识库...")
                    retriever = load_retriever(embedding_db_path, embedding)
                    # 准备问题
                    query = data["message"]
                    # 执行问答
                    response_message = asyncio.run(run_chain(retriever, source_id, query, current_state))

                # 当状态为插件问答
                if current_state == "插件问答":
                    post_type =  data["post_type"]
                    query = get_response_from_plugins(name_space, post_type, current_state, data)
                    # 执行问答
                    response_message = asyncio.run(chat_generic_langchain(source_id, query, current_state))
    
                # 当状态为网站问答
                if current_state == "网站问答":
                    # 调用RAG
                    print(f"加载 {embedding_db_path_site} 的向量知识库...")
                    retriever = load_retriever(embedding_db_path_site, embedding)
                    # 准备问题
                    query = data["message"]
                    # 执行问答
                    response_message = asyncio.run(run_chain(retriever, source_id, query, current_state))
                    #retriever.delete_collection()           

                # 文档问答。文档未经过分割向量化，直接发给LLM推理
                elif current_state == "文档问答":
                    question = data["message"].replace(at_string, "")
                    command = f"start cmd /c \"conda activate rag-bot && python docs_chat.py {embedding_data_path} {question} {chat_type} {user_id} {group_id} {at} {source_id} {current_state}\"" # 不用等待新打开的窗口执行完成
                    os.system(command)
                    response_message = ""

                # 聊天。
                else:
                    query = f'{data["message"]}'
                    response_message = asyncio.run(chat_generic_langchain(source_id, query, current_state))
            
        # 发送消息
        print("="*40, "\n",f"答案：{response_message}")    
        try: 
            asyncio.run(answer_action(chat_type, user_id, group_id, at, response_message))
            # answer_action(chat_type, user_id, group_id, at, response_message)
        except Exception as e:
            print("="*40, "\n",f"发送消息错误：{e}")


#**************** 事件处理 ********************************************
def event_action(data):
    # 判断事件类型
    notice_type = data["notice_type"]

    # 获取当前群允许的聊天类型
    chat_type_allow = get_allow_state(data)
    print("="*40, "\n","当前允许的聊天消息类型：", chat_type_allow)

    # 判断聊天类型、获得必要参数（函数在send.py中）
    chat_type = get_chat_type(data)["chatType"]
    at = get_chat_type(data)["at"]
    user_id = get_chat_type(data)["user_id"]
    group_id = get_chat_type(data)["group_id"]
    
    # 获取name_space
    name_space = get_user_name_space(user_id, source_id)

    if chat_type in ("group_at", "group"):
        source_id = group_id
    elif chat_type == "private":
        source_id = user_id
    else:
        source_id = user_id

    current_state = get_user_state_from_db(user_id, source_id) # 先检查用户状态
  
    print("="*40)
    print(f"chat_type:{chat_type}\nat:{at}\nuser_id:{user_id}\ngroup_id:{group_id}\nsource_id:{source_id}\ncurrent_state:{current_state}")
   

    # 如果消息提醒是群文件和离线文件，下载后返回下载成功消息
    if notice_type in ("offline_file", "group_upload"):
        file_name = data["file"]["name"]
        file_size = data["file"]["size"]
        file_url = data["file"]["url"]
        try:
            # 群文件路径名
            user_data_path = os.path.join(data_path, "group_" + str(data["group_id"]))
        except:
            # 用户文件路径名
            user_data_path = os.path.join(data_path, user_id)
        
        # 启动文件解读
        if current_state == "聊天":
            file_path_temp = f"{user_data_path}_chat_temp_{user_id}"
            response_message = download_file(file_url, file_name, file_path_temp, allowed_extensions=allowed_extensions)
            question = "请用中文进行解读，并输出一个总结"
            command = f"start cmd /c \"conda activate rag-bot && python docs_chat.py {file_path_temp} {question} {chat_type} {user_id} {group_id} {at} {source_id} {current_state}\"" # 不用等待新打开的窗口执行完成
            os.system(command)
            response_message = ""
        else:
            response_message = download_file(file_url, file_name, user_data_path, allowed_extensions=allowed_extensions)

    # 如果不包含文件的提醒
    else:
        # 当状态为插件问答
        if current_state == "插件问答":
            post_type =  data["post_type"]
            query = get_response_from_plugins(name_space, post_type, current_state, data)
            # 执行问答
            response_message = asyncio.run(chat_generic_langchain(source_id, query, current_state))
        else:
            response_message = f"{notice_type}"
    
    print("*" * 40)
    print(response_message)

    # 发送消息
    asyncio.run(answer_action(chat_type, user_id, group_id, at, response_message))
    
