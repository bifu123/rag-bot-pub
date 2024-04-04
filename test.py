import os
import sys
from sys import argv
import shutil
import base64
import re
import time


# 文档加工
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, PythonLoader # 文档类加载器
from langchain.document_loaders.sitemap import SitemapLoader # 站点地图加载 
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


# 异步函数
import asyncio

# 解析站点地图
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
from urllib import request
from bs4 import BeautifulSoup



####################### 函数 
def build_sitemap(URL):
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

    with open('sitemap.xml', 'w', encoding="utf-8") as fp:
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n')

    return {"url":URL, "sitemap":"sitemap.xml"}

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
    loaders = UnstructuredURLLoader(urls=urls)
    return loaders
# 加载文档的函数
def get_loads_from_dir(new_embedding_db_path):
    print("正在加载" + new_embedding_db_path + "下的所有文档...")
    loader = DirectoryLoader(new_embedding_db_path, show_progress=True, use_multithreading=True)
    loaders = loader.load()
    print(loaders)
    return loaders


sitemap_file = "sitemap.xml"


# url列表加载-使用SeleniumURLLoader
def get_loaders(urls):
    documents = SeleniumURLLoader(urls)
    loaders = documents.load()
    return loaders

# # url列表加载-使用UnstructuredURLLoader
# def get_loaders(urls):
#     documents = UnstructuredURLLoader(urls=urls)
#     loaders = documents.load()
#     return documents

# 解析站点地图
print(f"正在解析站点地图...{sitemap_file}")
urls = parse_sitemap(sitemap_file)
# loaders = []
# for url in urls:
#     print(f"正在加载：{url}")
#     try:
#         loader = WebBaseLoader(url)
#         document = loader.load()
#     except:
#         print(f"加载失败：{url}")
#         pass
    
#     loaders.append(document)
loaders = get_loaders(urls)
    
print(loaders)