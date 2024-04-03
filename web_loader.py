from langchain.document_loaders.sitemap import SitemapLoader
from langchain_community.document_loaders import WebBaseLoader
import xml.dom.minidom
import datetime
from urllib import request
from bs4 import BeautifulSoup
# 解析站点地图
import xml.etree.ElementTree as ET

#!/usr/bin/python3
# -*- coding: utf-8 -*-


URL = 'https://typecho.work'

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

# 多页加载，添加到总的文档
def get_loaders(sitemap_path):
    urls = parse_sitemap(sitemap_path)
    documents = []
    for url in urls:
        print(f"正在加载：{url}")
        loader = WebBaseLoader(url)
        document = loader.load()
        documents.append(document[0])
        # print(documents)
    return documents

# 单页加载
def get_loader(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    return document

# # 根据站点地图加载网页
# loader = SitemapLoader(
#     "http://cho.freesky.sbs/sitemap.xml",
#     filter_urls=["https://typecho.work/archives/"]
# )
# documents = loader.load()
# print(len(documents))
# print(documents)