import os
import sys
from sys import argv
import shutil


# 文档加工
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, PythonLoader 
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter # 分割文档
from langchain_community.vectorstores import Chroma # 量化文档数据库

from models_load import *
from send import *
from sqlite_helper import *

import time




print(f"接收到的参数：{sys.argv}")

'''
['new_embedding.py', './data\\415135222', './chroma_db\\415135222_1', "model='models/embedding-001'", 'task_type=None', 'google_api_key=None', 'client_options=None', 'transport=None', '1500', '200']

{"chatType":chatType, "user_id": str(user_id), "group_id": str(group_id), "at": at}

接收到的参数：['new_embedding.py', './data\\415135222', './chroma_db\\415135222_1', '415135222', 'private', '415135222', 'no', 'no']
'''


embedding_data_path = sys.argv[1]
embedding_db_path = sys.argv[2]
source_id = str(sys.argv[3])
chat_type = str(sys.argv[4])
user_id = str(sys.argv[5])
group_id = str(sys.argv[6])
at = str(sys.argv[7])


print("*" * 40)

print(f"embedding_data_path:",embedding_data_path)
print(f"embedding_db_path:",embedding_db_path)
print(f"source_id:",source_id)
print(f"chat_type:",chat_type)
print(f"user_id:",user_id)
print(f"group_id:",group_id)
print(f"at:",at)

print("*" * 40)





# 将 gemini api 加入环境变量
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY #将GOOGLE_API_KEY加载到环境变量中

# 本地量化模型
embedding_ollama = OllamaEmbeddings(
    base_url = embedding_ollama_conf["base_url"], 
    model = embedding_ollama_conf["model"]
) 

# 线上google量化模型
embedding_google = GoogleGenerativeAIEmbeddings(
    model = embedding_google_conf["model"]
) 
# embedding_google.embed_query("hello, world!")


# 选择量化模型
if model_choice["embedding"] == "ollama":
    embedding = embedding_ollama
else:
    embedding = embedding_google

# embedding_data_path = ".\\data\\415135222"
# embedding_db_path = ".\\chroma_db\\415135222_1"
# embedding = embedding_google
# chunk_size = 1500
# chunk_overlap = 200





# # os.system(f"start cmd /k conda activate rag-bot && python new_embedding.py {embedding_data_path} {embedding_db_path} {embedding} {chunk_size} {chunk_overlap}")


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
update_db_path(source_id, new_embedding_db_path)





# 量化文档的类
class DocumentProcessor:
    # 使用示例
    # processor = DocumentProcessor(data_path, db_path, embedding, chunk_size, chunk_overlap)
    # processor.update_database()
    def __init__(self, data_path, db_path, embedding, chunk_size, chunk_overlap):
        self.data_path = data_path
        self.db_path = db_path
        self.embedding = embedding
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    # 加载文档
    def load_documents(self):
        print("正在加载" + self.data_path + "下的所有文档...")
        loader = DirectoryLoader(self.data_path, show_progress=True, use_multithreading=True)
        loaders = loader.load()
        print(loaders)
        return loaders
    
    # 分割文档
    def split_documents(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_overlap, chunk_overlap=chunk_overlap)
        return text_splitter.split_documents(docs)
    
    # 更新向量
    def update_database(self):
        docs = self.load_documents()
        all_splits = self.split_documents(docs)

        Chroma.from_documents(
            documents=all_splits,
            embedding=self.embedding,
            persist_directory=self.db_path
        )
        #vectorstore_to_db.delete_collection()
        result_msg = f"量化执行结束，已迁移至新知识库：{self.db_path}"
        return result_msg


# 执行量化
try:
    processor = DocumentProcessor(embedding_data_path, new_embedding_db_path, embedding, chunk_size, chunk_overlap)
    response_message = processor.update_database()

    print("*" * 40)
    print(response_message)
except Exception as e:
    print("*" * 40)
    response_message = f"执行量化错误：{e} 请先上传文档"
    print(response_message)


# time.sleep(1000000)
# input("Press Enter to exit...")



answer_action(chat_type, user_id, group_id, at, response_message)

