# 机器人 QQ 号
bot_qq = "3152246598"

# 管理员 QQ 号
admin_qq = "415135222"

# 允许的聊天回复
chat_type_allow = [
    "private",    # 私聊回复
    "group_at",   # 只有群中 @ 才回复
    "group" ,     # 回复群中所有聊天，这样机器人什么人说话它都会接话
    # "Unkown" ,  # 其它类型聊天也回复
    ]

# 群中@特征字符
at_string = f"[CQ:at,qq={bot_qq}]"

# 允许上传的文件类型
allowed_extensions = [
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".pdf",
    ".md",
    ".html",
    ".txt",
    ".htm"
]

# go-cqhttp Websocket 监听地址
ws_url = "ws://192.168.66.20:25522"  # 根据go-cqhttp配置文件中的地址修改

# go-cqhttp http API接口地址
http_url = "http://192.168.66.20:25533" # 根据go-cqhttp配置文件中的地址修改

# 源文档路径 
data_path = "./data"

# 分割文档的块大小
chunk_size = 800

# 分割文档时连续部分的重叠区大小
chunk_overlap = 128

# 量化后数据保存路径
db_path = "./chroma_db"

# gemini api key 
GOOGLE_API_KEY = "AIzaSyBgKE09ReHYbG2lqC_YmdsbEjF8yQGWrGM"
#gemini api key的申请地址：https://makersuite.google.com/app/prompts/new_freeform ，条件：拥有google帐号

# 通义千问 api key
DASHSCOPE_API_KEY  = "sk-7d48078fa897417c9cfa5cfa70d95f9a"

# 附赠我的 gemini 聊天 API：
GMI_SERVER = 'http://107.175.206.30:5001/chat'

# 模型配置 
## 本地量化模型
embedding_ollama_conf = {
    "base_url": "http://192.168.66.24:11434", 
    "model": "nomic-embed-text"
}
## goole量化模型
embedding_google_conf = {
    "model": "models/embedding-001"
} 
## 本地语言模型 
llm_ollama_conf = {
    "base_url": "http://192.168.66.26:11434", 
    "model": "qwen:7b"
}
## 线上google gemini语言模型
llm_gemini_conf = {
    "model": "gemini-pro",
    "temperature": 0.2
} 
## 线上 通义千问 语言模型
llm_tongyi_conf = {
    "model_name": "qwen-max-longcontext", # qwen-max-longcontext | qwen-max
    "temperature": 0.2,
    "streaming": False
} 

# 模型选择
model_choice = {
    "embedding":"ollama", # embedding: ollama | google
    "llm": "tongyi" # llm: ollama | gemini | tongyi
}






