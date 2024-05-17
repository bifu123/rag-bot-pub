import os
import sys
from sys import argv
import shutil
import base64
import re
import time


# 文档加工
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, PythonLoader # 文档类加载器
from langchain_community.document_loaders import SitemapLoader # 站点地图加载 
from langchain_community.document_loaders import WebBaseLoader # 单个URL加载
from langchain_community.document_loaders import UnstructuredURLLoader # 多URL列表加载
from langchain_community.document_loaders import SeleniumURLLoader # 多URL列表加载（含JS）

from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter # 分割文档
from langchain_community.vectorstores import Chroma # 量化文档数据库

# 从文件导入
from models_load import *
from send import *
from sqlite_helper import *
from dal import get_user_state_from_db


# 异步函数
import asyncio

# 解析站点地图
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
from urllib import request
from bs4 import BeautifulSoup




####################### 处理传参 
# 获取传参
print(f"接收到的参数：{sys.argv}")
embedding_data_path = sys.argv[1]
embedding_db_path = sys.argv[2]
source_id = str(sys.argv[3])
chat_type = str(sys.argv[4])
user_id = str(sys.argv[5])
group_id = str(sys.argv[6])
at = str(sys.argv[7])
embedding_type = str(sys.argv[8])
bot_nick_name = str(sys.argv[9])
user_nick_name = str(sys.argv[10])
try:
    site_url = str(sys.argv[11])
    site_url = json.loads(base64.b64decode(site_url).decode())
except:
    site_url = False



# 打印参数
print("*" * 40)
print("embedding_data_path:",embedding_data_path)
print("embedding_db_path:",embedding_db_path)
print("source_id:",source_id)
print("chat_type:",chat_type)
print("user_id:",user_id)
print("group_id:",group_id)
print("at:",at)
print("embedding_type:",embedding_type)
print("bot_nick_name:",bot_nick_name)
print("user_nick_name:",user_nick_name)
print("site_url:",site_url)
print("*" * 40)


####################### 量化模型 

# 本地量化模型
embedding_ollama = OllamaEmbeddings(
    base_url = embedding_ollama_conf["base_url"], 
    model = embedding_ollama_conf["model"]
) 


# 选择量化模型
if model_choice["embedding"] == "ollama":
    embedding = embedding_ollama
# else:
#     embedding = embedding_google




####################### 函数 
def build_sitemap(URL, source_id):
    '''所有url列表'''
    URL_LIST = {}

    '''模拟header'''
    HEADER = {
        'Cookie': 'AD_RS_COOKIE=20080917',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \ AppleWeb\Kit/537.36 (KHTML, like Gecko)\ '
                      'Chrome/58.0.3029.110 Safari/537.36'}

    def get_http(url, headers=None, charset='gbk'):
        if headers is None:
            headers = {}
        try:
            response = request.urlopen(request.Request(url=url, headers=headers))
            return response.read().decode(charset, errors='ignore')
        except Exception as e:
            print("Error occurred while fetching URL:", e)
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

    sitemap_file = f'{source_id}.xml'

    with open(f'{sitemap_file}', 'w', encoding="utf-8") as fp:
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n')

    return {"url":URL, "sitemap": f"{sitemap_file}"}

# 解析站点地图的函数
def parse_sitemap(xml_file):
    urls = []
    # 解析 XML 文件
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # 定义 XML 命名空间
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    # 查找所有 URL 条目
    for url in root.findall('ns:url', namespace):
        print(f"正在解析：{url}")
        loc = url.find('ns:loc', namespace).text
        lastmod = url.find('ns:lastmod', namespace).text
        priority = url.find('ns:priority', namespace).text
        #urls.append({'loc': loc, 'lastmod': lastmod, 'priority': priority})
        urls.append(loc)
    print(f"解析完毕：{url}")
    return urls
# 加载站点地图的函数
def get_loaders_from_sitemap(urls):
    documents = SeleniumURLLoader(urls)
    loaders = documents.load()
    return loaders
# 加载文档的函数
def get_loads_from_dir(new_embedding_db_path):
    print("正在加载" + new_embedding_db_path + "下的所有文档...")
    loader = DirectoryLoader(new_embedding_db_path, show_progress=True, use_multithreading=True)
    loaders = loader.load()
    print(loaders)
    return loaders



####################### 执行过程
# 确定量化存储路径
if os.path.exists(embedding_db_path) and os.path.isdir(embedding_db_path):
    try:
        shutil.rmtree(embedding_db_path)
        print(f"文件夹 '{embedding_db_path}' 已成功删除，即将更新数据...\n")
        new_embedding_db_path = embedding_db_path
    except OSError as e:
        # 判断当前路径中是否包含"_1"
        if "_1" in f"{embedding_db_path}":
            new_embedding_db_path = embedding_db_path.replace("_1", "")
        else:
            new_embedding_db_path = embedding_db_path + "_1"
            print(f"删除文件夹 '{embedding_db_path}' 时发生错误：{e}，将更改路径为{new_embedding_db_path}\n")
else:
    new_embedding_db_path = embedding_db_path
print(f"{embedding_db_path} 不存在，不需删除。将使用 {new_embedding_db_path} 作为向量存储路径")


# 将新路径更新到数据库
if site_url:
    update_db_path_site(source_id, new_embedding_db_path)
else:
    update_db_path(source_id, new_embedding_db_path)




# 根据传参决定加载器来加载文档
if embedding_type == "site":
    # 制作站点地图
    print(f"正在制作站点地图...{site_url}")
    sitemap_file = build_sitemap(site_url, source_id)["sitemap"]
    # 解析站点地图
    print(f"正在解析站点地图...{sitemap_file}")
    urls = parse_sitemap(sitemap_file)
    # 加载网站URL列表
    print(f"加载网站URL列表...")
    loaders = get_loaders_from_sitemap(urls)
elif embedding_type == "file":
    try:
        loaders = get_loads_from_dir(embedding_data_path)
    except Exception as e:
        print(f"get_loads_from_dir出错：{e}")
        #time.sleep(1000000)
print(loaders)
#time.sleep(1000000)


# 分割文档
print("正在分割文档...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_overlap, chunk_overlap=chunk_overlap)
all_splits = text_splitter.split_documents(loaders)

# 保存向量
print("正在保存向量...")
Chroma.from_documents(
    documents =all_splits,
    embedding = embedding,
    persist_directory = new_embedding_db_path
)

# 构建消息内容
response_message = f"量化执行结束，已迁移至新知识库：{new_embedding_db_path}"

# 发送消息
asyncio.run(answer_action(chat_type, user_id, group_id, at, response_message))

# 获取user_state和name_space
name_space = get_user_name_space(user_id, source_id)
# from dal import get_user_state_from_db
user_state = get_user_state_from_db(user_id, source_id)

# 将聊天回复写入聊天历史记录
if at == "yes":
    response_message_insert = "@" + user_nick_name + " " + response_message
insert_chat_history(response_message_insert, source_id, bot_nick_name, user_state, name_space)
