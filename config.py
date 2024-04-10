# 机器人 QQ 号
bot_qq = "123456789"

# 管理员 QQ 号
admin_qq = "987654321"

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
    ".htm",
    ".py"
]

# go-cqhttp Websocket 监听地址
ws_url = "ws://127.0.0.1:25522"  # 根据go-cqhttp配置文件中的地址修改

# go-cqhttp http API接口地址
http_url = "http://127.0.0.1:25533" # 根据go-cqhttp配置文件中的地址修改

# 源文档路径 
data_path = "./data"

# 分割文档的块大小
chunk_size = 800

# 分割文档时连续部分的重叠区大小
chunk_overlap = 128

# 保存聊天记录的大小
chat_history_size_set = 8192 # 记录越大，每次发给大模型分析的数据越多，上下文越全面。但是会增加响应的时间，而且随着话题的多样复杂，会降低大模型分析的精准度

# 量化后数据保存路径
db_path = "./chroma_db"

# gemini api key 
GOOGLE_API_KEY = "your GOOGLE_API_KEY" #gemini api key的申请地址：https://makersuite.google.com/app/prompts/new_freeform ，条件：拥有google帐号

# 通义千问 api key
DASHSCOPE_API_KEY  = "your DASHSCOPE_API_KEY"

# moonshot ai kimi api key
MOONSHOT_API_KEY = "your MOONSHOT_API_KEY" # 在这里申请: https://platform.moonshot.cn/console/api-keys

# 附赠我的 gemini 聊天 API：
GMI_SERVER = 'http://107.175.206.30:5001/chat'

# 模型配置 
## 本地量化模型
embedding_ollama_conf = {
    "base_url": "http://192.168.66.26:11434", 
    "model": "mofanke/dmeta-embedding-zh" # nomic-embed-text | mofanke/dmeta-embedding-zh
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
    "temperature": 0.7
} 
## 线上 通义千问 语言模型
llm_tongyi_conf = {
    "model_name": "qwen-plus", # qwen-max-longcontext | qwen-max |qwen-plus |roger/minicpm:latest
    "temperature": 0.7,
    "streaming": False
} 
## 线上 moonshot ai kimi 语言模型
llm_kimi_conf = {
    "model_name": "moonshot-v1-128k",
    "temperature": 0.3
} 
# 本地 chatGLM3-6b
llm_chatGLM_conf = {
    "endpoint_url": "http://192.168.66.26:8000/v1/chat/completions",
    "max_tokens": 80000,
    "top_p": 0.9
}
# 模型选择
model_choice = {
    # 本地向量模型
    "embedding":"ollama", # embedding: ollama | google
    # 聊天模型
    "llm": "tongyi", # llm: ollama | gemini | tongyi | chatglm | kimi
    # 知识库模型
    "llm_rag": "ollama" # llm: ollama | gemini | tongyi | chatglm | kimi 
}







