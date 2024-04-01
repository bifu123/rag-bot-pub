# #pip install python-docx
# from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, PythonLoader 
# import os

# data_path = './data'

# loader = DirectoryLoader(data_path, show_progress=True, use_multithreading=True)
# docs = loader.load()


# print(len(docs),docs)

####################################
'''
DirectoryLoader 默认使用 UnstructedLoader ，它包含了：

文件类型	加载器	支持情况
HTML文件	UnstructuredHTMLLoader	可以加载
RTF文件	UnstructuredRTFLoader	可以加载
Markdown文件	UnstructuredMarkdownLoader	可以加载
EPub文件	UnstructuredEPubLoader	可以加载
Excel文件	UnstructuredExcelLoader	可以加载
CSV文件	UnstructuredCSVLoader	可以加载
JSON文件	JSONLoader	可以加载
图像文件	UnstructuredImageLoader	可以加载PNG和JPG
音频文件	YoutubeAudioLoader	可以加载YouTube音频
视频字幕文件	BiliBiliLoader	可以加载BiliBili视频字幕
源代码文件	PythonLoader	可以加载Python源代码文件

原文链接：https://blog.csdn.net/qq_56591814/article/details/134835702

所以我们先使用 DirectoryLoader，它可递归文件夹加载上述类型文件，然后再加上UnstructuredWordDocumentLoader，让它支持world（必须pip install python-docx），这样其实基本的办公文档就齐全了，同理我们再加上UnstructuredHTMLLoader、UnstructuredMarkdownLoader，让它再支持markdown、html。
'''

from langchain.document_loaders.sitemap import SitemapLoader

loader = SitemapLoader(
    "http://cho.freesky.sbs/sitemap.xml",
    # filter_urls=["https://docs.chainstack.com/docs/"]
)

documents = loader.load()
print(len(documents))
print(documents[0])