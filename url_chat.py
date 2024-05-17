import os
import sys
from sys import argv
import shutil
import requests
import json
import time
import base64
import re

from langchain_community.document_loaders.sitemap import SitemapLoader # 站点地图加载 
from langchain_community.document_loaders import WebBaseLoader # 单个URL加载
from langchain_community.document_loaders import UnstructuredURLLoader # 多URL列表加载
from langchain_community.document_loaders import SeleniumURLLoader

import xml.dom.minidom
import datetime
from urllib import request
from bs4 import BeautifulSoup

# 解析站点地图
import xml.etree.ElementTree as ET

# 从文件导入
from send import *
from models_load import *
# from dal import get_user_state_from_db

# 异步函数
import asyncio

print(f"接收到的参数：{sys.argv}")

encoded_urls = sys.argv[1]
# 将BASE64编码后的字符串解码还原为URL列表
decode_urls = json.loads(base64.b64decode(encoded_urls).decode())

question = sys.argv[2]
chat_type = str(sys.argv[3])
user_id = str(sys.argv[4])
group_id = str(sys.argv[5])
at = str(sys.argv[6])
source_id = str(sys.argv[7])
user_state = str(sys.argv[8])
bot_nick_name = str(sys.argv[9])
user_nick_name = str(sys.argv[10])

print("*" * 40)
print("decode_urls:", decode_urls)
print("question:", question)
print("chat_type:", chat_type)
print("user_id:", user_id)
print("group_id:", group_id)
print("at:", at)
print("source_id:", source_id)
print("user_state:", user_state)
print("bot_nick_name:", bot_nick_name)
print("user_nick_name:", user_nick_name)
print("*" * 40)


# 制作站点地图
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

# 解析站点地图
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

# url列表加载-使用SeleniumURLLoader
def get_loaders(urls):
    documents = SeleniumURLLoader(urls)
    loaders = documents.load()
    return loaders

# 站点地图加载
def get_loaders_from_sitemap(sitemap_path):
    urls = parse_sitemap(sitemap_path)
    documents = UnstructuredURLLoader(urls=urls)
    return documents

# 加载内容
try:
    loader = get_loaders(decode_urls)
    print(loader)
except Exception as e:
    print(f"错误：{e}")



name_space = get_user_name_space(user_id, source_id)



# 将聊天请求写入记录
if at == "yes":
    query_insert = "@" + bot_nick_name + " " + question
else:
    query_insert = question
insert_chat_history(query_insert, source_id, user_nick_name, user_state, name_space)

# 调用通用聊天得出答案
try:
    # 清除原来的聊天历史
    # delete_all_records(source_id, user_state, name_space)
    query = f"{loader}\n{question}"
    response_message = asyncio.run(chat_generic_langchain(bot_nick_name, user_nick_name, source_id, query, user_state, name_space))
except Exception as e:
    response_message = f"错误：{e}"


# 打印答案，发送消息
print("*" * 40)
print(f"答案： {response_message}")
# 发送消息
asyncio.run(answer_action(chat_type, user_id, group_id, at, response_message))

    
# # 获取user_state和name_space
# name_space = get_user_name_space(user_id, source_id)
# # from dal import get_user_state_from_db
# user_state = get_user_state_from_db(user_id, source_id)

# 将聊天回复写入聊天历史记录
if at == "yes":
    response_message_insert = "@" + user_nick_name + " " + response_message
else:
    response_message_insert = response_message
insert_chat_history(response_message_insert, source_id, bot_nick_name, user_state, name_space)








