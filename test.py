from langchain_community.document_loaders import BiliBiliLoader # BiliBili加载器
document = BiliBiliLoader(
    [
        "https://www.bilibili.com/video/BV1g84y1R7oE/",
    ],
    sessdata="f1f11371%2C1726411713%2C2f596%2A32CjAVzZwcm6eyDaYlhIWak_lvkXKzdpXqaj4j_py5N5qTAoi1BiRbDgdZR_MbQ554E54SVjRJQzhsblNGNEFVRUtXYnlsblpjQXZSOTF0dHlYam1qZEtsd1N1VjFCREhfaENSd3N5MTdEbW5xbmZwX29rdEVqM2pZZUYwdWF6RGNHRDVMUEMtbnF3IIEC",
    bili_jct="762e658697158034e9f52c80fda96ccf",
    buvid4="65005758-C554-45C8-DE6A-213EC845280220322-024031914-IPlHBbyY4urWMQtWdMoKRg%3D%3D",
)
loader = document.load()
print(loader)



# Traceback (most recent call last):
#   File "D:\YLBot\ylbot\rag-bot\test.py", line 2, in <module>
#     document = BiliBiliLoader(
#                ^^^^^^^^^^^^^^^
# TypeError: BiliBiliLoader.__init__() got an unexpected keyword argument 'sessdata'