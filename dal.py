# 从内置模块导入
import os
import shutil
import json
import sys
from sys import argv

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
    elif chat_type == "private":
        source_id = user_id
        embedding_data_path = user_data_path
        embedding_db_path_tmp = user_db_path


    # 读取数据库当前source_id的存储路径
    if get_path_by_source_id(source_id) is None:
        insert_into_db_path(source_id, embedding_db_path_tmp) # 如果没有记录则插入
        embedding_db_path = embedding_db_path_tmp
    else:
        embedding_db_path = get_path_by_source_id(source_id) # 如果存在则直接使用



    print("="*40, "\n",f"source_id：{source_id}")     
    print("="*40, "\n",f"当前使用的文档路径：{embedding_data_path}")
    print("="*40, "\n",f"当前使用的数据库路径：{embedding_db_path}")

    # 以 | 分割找出其中的命令
    command_parts = message.split("|")
    command_name = command_parts[0]

    print("="*40, "\n",f"当前命令：{command_name}")   

    # 在允许回复的聊天类型中处理
    if chat_type in chat_type_allow:
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
                    response_message = "你还没有文档，请先给我发送你的文档"
            except:
                response_message = "你还没有文档，请先给我发送你的文档"

        # 命令： /删除文档 
        elif command_name in ("/删除文档", f"{at_string} /删除文档"):
            # 取得文件名
            try:
                file_path = command_parts[1]
                if os.path.exists(file_path):
                    os.remove(file_path)
                    response_message = f"文件 '{file_path}' 已成功删除。注：如果是群文档，只会删除服务器上的，群中同名文档不会被删除"
                else:
                    response_message = f"文件 '{file_path}' 不存在，无法删除"
            except:
                response_message = "命令错误"
            
        # 命令： /量化文档 
        elif command_name in ("/量化文档", f"{at_string} /量化文档"):
            try:
                # 新开窗口量化到新目录
                #command = f"start /wait cmd /c \"conda activate rag-bot && python new_embedding.py {embedding_data_path} {embedding_db_path} {source_id} {chat_type} {user_id} {group_id} {at}\"" # 等待新打开的窗口执行完成
                command = f"start cmd /c \"conda activate rag-bot && python new_embedding.py {embedding_data_path} {embedding_db_path} {source_id} {chat_type} {user_id} {group_id} {at}\"" # 不用等待新打开的窗口执行完成
                # 使用 os.system() 执行命令
                os.system(command)
                response_message = "正在量化，完成后另行通知，这期间你仍然可以使用你现在的文档知识库"
            except Exception as e:
                response_message = f"量化失败：{e}"
    
        # 命令： /上传文档 
        elif command_name in ("/上传文档", f"{at_string} /上传文档"):
            # 取得文件名
            response_message = "请直接发送文档"

        # 命令： /文档问答 
        elif command_name in ("/文档问答", f"{at_string} /文档问答"):
            # 切换到 文档问答 状态
            # 用数据库保存每个用户的状态
            switch_user_state(user_id, "文档问答")
            response_message = "你己切换到 【文档问答】 状态，如要切换为 【聊天】或【知识库问答】，请发送命令：/聊天 或 /知识库问答\n在这种模式下，你（你们）的文档目录下的所有文档不会被分割向量化，而直接发给LLM推理"   

        # 命令： /知识库问答 
        elif command_name in ("/知识库问答", f"{at_string} /知识库问答"):
            # 切换到 文档问答 状态
            # 用数据库保存每个用户的状态
            switch_user_state(user_id, "知识库问答")
            response_message = "你己切换到 【知识库问答】 状态，如要切换为 【聊天】或【文档问答】，请发送命令：/聊天 或 /文档问答"   

        # 命令： /聊天 
        elif command_name in ("/聊天", f"{at_string} /聊天"):
            # 切换到 聊天 状态
            # 用数据库保存每个用户的状态
            switch_user_state(user_id, "聊天")
            response_message = "你己切换到 【聊天】 状态，如要切换为 【知识库问答】或【文档问答】，请发送命令：/知识库问答 或 /文档问答"

        # 命令： /我的状态 
        elif command_name in ("/我的状态", f"{at_string} /我的状态"):
            # 从数据库中查找用户当前状态
            current_state = get_user_state(user_id)
            response_message = "【" + current_state + "】"
        
        # 命令： /开启群消息 
        elif command_name in ("/开启群消息", f"{at_string} /开启群消息"):
            try:
                switch_allow_state(str(data["group_id"]), "on")
                response_message = "群消息已经开启"
            except Exception as e:
                response_message = f"群消息开启失败：{e}"

        # 命令： /关闭群消息 
        elif command_name in ("/关闭群消息", f"{at_string} /关闭群消息"):
            try:
                switch_allow_state(str(data["group_id"]), "off")
                response_message = "群消息已经关闭"
            except Exception as e:
                response_message = f"群消息关闭失败：{e}"

        # 命令： /清空记录 
        elif command_name in ("/清空记录", f"{at_string} /清空记录"):
            try:
                current_state = get_user_state(user_id)
                delete_all_records(source_id, current_state)
                response_message = "消息已经清空"
            except Exception as e:
                response_message = f"消息清空失败：{e}"

        # 和 LLM 对话
        else:
            # 知识库问答，文档经过分割向量化
            current_state = get_user_state(user_id) # 先检查用户状态
            print(f"当前状态：{current_state}")
            # 当状态为文档问答
            if current_state == "知识库问答":
                # 调用RAG
                print(f"调用 {embedding_db_path} 进行文档问答...")
                retriever = load_retriever(embedding_db_path, embedding)
                # 准备问题
                query = data["message"]
                # 执行问答
                response_message = run_chain(retriever, source_id, query, current_state)
                #retriever.delete_collection()

            # 文档问答。文档未经过分割向量化，直接发给LLM推理
            elif current_state == "文档问答":
                # 调用 GEMIN 接口
                question = data["message"].replace(at_string, "")
                command = f"start cmd /c \"conda activate rag-bot && python docs_chat.py {embedding_data_path} {question} {chat_type} {user_id} {group_id} {at} {source_id} {current_state}\"" # 不用等待新打开的窗口执行完成
                # 使用 os.system() 执行命令
                os.system(command)
                response_message = ""

            # 聊天。
            else:
                query = f'{data["message"]}'
                response_message = chat_generic_langchain(source_id, query, current_state)

        
        # 发送消息
        print("="*40, "\n",f"答案：{response_message}")    
        try: 
            answer_action(chat_type, user_id, group_id, at, response_message)
        except Exception as e:
            print("="*40, "\n",f"发送消息错误：{e}")


#**************** 事件处理 ********************************************
def event_action(data):
    # 接收文件
    notice_type = data["notice_type"]
    user_id = str(data["user_id"])
    # 如果消息提醒是群文件和离线文件
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
        # 下载文件到用户目录
        
        response = download_file(file_url, file_name, user_data_path, allowed_extensions=allowed_extensions)
        # 定义一个处理提醒的反馈消息
        '''
        =============== Notice ===============
        {'post_type': 'notice', 'notice_type': 'offline_file', 'time': 1711607647, 'self_id': 1878085037, 'user_id': 415135222, 'file': {'name': 'tesla_p40.pdf', 'size': 106509, 'url': 'http://39.145.24.22/ftn_handler/5ad5075ff13463bc2cc7a6b2c8f8621bd15efb11953c58279f7830ae738fdb359f3cf19371d2b137843433fa5a71584023888c1f822a7962714c6f80268ab792'}}

        =============== Notice ===============
        {'post_type': 'notice', 'notice_type': 'group_upload', 'time': 1711608029, 'self_id': 1878085037, 'group_id': 499436648, 'user_id': 415135222, 'file': {'busid': 102, 'id': '/df9c709b-be79-4765-8d94-e1e1f2b13727', 'name': 'tesla_p40.pdf', 'size': 106509, 'url': 'http://223.109.208.144/ftn_handler/226e5a1946afd217ffcf5bee0f759dc6654d1dfc89512a268be65828a5aa23f7647bfbfb928a106f6d7de6321fd87743352758c00e9f518feb325812044651cf/?fname=2f64663963373039622d626537392d343736352d386439342d653165316632623133373237'}}


        =============== 批准入群 ==============
        {'post_type': 'notice', 'notice_type': 'group_increase', 'time': 1711826628, 'self_id': 3152246598, 'sub_type': 'approve', 'group_id': 222302526, 'operator_id': 0, 'user_id': 990154420}


        '''
    
    # 如果不包含文件的提醒
    else:
        response = "other notice"
    
    print("*" * 40)
    print(response)


    # 发送消息
    if data["notice_type"] == "offline_file": # 群文档
        url = http_url + "/send_private_msg"
        params = {
            "user_id": user_id, 
            "message": response
        } 
    elif data["notice_type"] == "group_upload": # 私人文档
        url = http_url + "/send_group_msg"
        params = {
            "group_id": str(data["group_id"]),
            "message": f"{at_string} " + response
            } 
        
    else:
        url = http_url + "/send_private_msg"
        params = {
            "user_id": user_id, 
            "message": "未知提醒类型，请联系管理员"
        }
  
    response = requests.post(url, params=params)  

    

# 生成站点地图的函数
URL = 'http://cho.freesky.sbs'
def build_sitemap(url):
    '''所有url列表'''
    URL_LIST = {}

    '''模拟header'''
    HEADER = {
        'Cookie': 'AD_RS_COOKIE=20080917',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \ AppleWeb\Kit/537.36 (KHTML, like Gecko)\ '
                      'Chrome/58.0.3029.110 Safari/537.36'}

    def get_http(url, headers=None, charset='utf8'):
        """
        发送请求
        :param url:
        :param headers:
        :param charset:
        :return:
        """
        if headers is None:
            headers = {}
        try:
            return request.urlopen(request.Request(url=url, headers=headers)).read().decode(charset)
        except Exception:
            pass
        return ''

    def open_url(url):
        """
        打开链接，并返回该链接下的所有链接
        :param url:
        :return:
        """
        soup = BeautifulSoup(get_http(url=url, headers=HEADER), 'html.parser')

        all_a = soup.find_all('a')
        url_list = {}
        for a_i in all_a:
            href = a_i.get('href')
            if href is not None and foreign_chain(href):
                url_list[href] = href
                URL_LIST[href] = href
        return url_list

    def foreign_chain(url):
        """
        验证是否是外链
        :param url:
        :return:
        """
        return url.find(URL) == 0

    '''首页'''
    home_all_url = open_url(URL)

    '''循环首页下的所有链接'''
    if isinstance(home_all_url, dict):
        # 循环首页下的所有链接
        for home_url in home_all_url:
            # 验证是否是本站域名
            if foreign_chain(home_url) is True:
                open_url(home_url)

    URL_LIST_COPY = URL_LIST.copy()

    for copy_i in URL_LIST_COPY:
        open_url(copy_i)

    # 创建文件
    doc = xml.dom.minidom.Document()
    root = doc.createElement('urlset')
    # 设置根节点的属性
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root.setAttribute('xsi:schemaLocation', 'http://www.sitemaps.org/schemas/sitemap/0.9 '
                                             'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
    doc.appendChild(root)

    for url_list_i in URL_LIST:
        nodeUrl = doc.createElement('url')
        nodeLoc = doc.createElement('loc')
        nodeLoc.appendChild(doc.createTextNode(str(url_list_i)))
        nodeLastmod = doc.createElement("lastmod")
        nodeLastmod.appendChild(doc.createTextNode(str(datetime.datetime.now().date())))
        nodePriority = doc.createElement("priority")
        nodePriority.appendChild(doc.createTextNode('1.0'))
        nodeUrl.appendChild(nodeLoc)
        nodeUrl.appendChild(nodeLastmod)
        nodeUrl.appendChild(nodePriority)
        root.appendChild(nodeUrl)

    with open('sitemap.xml', 'w', encoding="utf-8") as fp:
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n')

    return {"url":url, "sitemap":"./sitemap.xml"}

# # 调用函数并输出结果
# print(build_sitemap(URL))



