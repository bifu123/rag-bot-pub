import sqlite3
import threading
import os

from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime


# 创建一个全局的数据库连接池
db_lock = threading.Lock()
db_connections = {}


# 数据库文件路径
DATABASE_FILE = 'users.db'

def get_database_connection():
    thread_id = threading.get_ident()
    if thread_id not in db_connections:
        if not os.path.exists(DATABASE_FILE):
            # 如果数据库文件不存在，则创建数据库和表
            conn = sqlite3.connect(DATABASE_FILE)
            create_tables(conn)
            db_connections[thread_id] = conn
        else:
            # 如果数据库文件存在，则直接连接数据库
            conn = sqlite3.connect(DATABASE_FILE)
            db_connections[thread_id] = conn
    return db_connections[thread_id]

def create_tables(connection):
    cursor = connection.cursor()
    # 创建用户状态表
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_states (
                      user_id TEXT PRIMARY KEY,
                      state TEXT)''')
    # 创建群消息开关状态表
    cursor.execute('''CREATE TABLE IF NOT EXISTS allow_states (
                      group_id TEXT PRIMARY KEY,
                      state TEXT)''')
    # 创建路径表
    cursor.execute('''CREATE TABLE IF NOT EXISTS db_path (
                      source_id TEXT PRIMARY KEY,
                      path_site TEXT,
                      path TEXT)''')
    # 创建当前聊天历史记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS history_now (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_id TEXT NOT NULL,
                        query TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_state TEXT DEFAULT '聊天'
                    )''')
    
    connection.commit()


# def get_database_connection():
#     thread_id = threading.get_ident()
#     if thread_id not in db_connections:
#         db_connections[thread_id] = sqlite3.connect('users.db')
#     return db_connections[thread_id]

def close_database_connection():
    thread_id = threading.get_ident()
    if thread_id in db_connections:
        db_connections[thread_id].close()
        del db_connections[thread_id]

# 函数用于切换用户状态
def switch_user_state(user_id, new_state):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO user_states (user_id, state)
                          VALUES (?, ?)''', (user_id, new_state))
        conn.commit()

# 函数用于切换群消息开关状态
def switch_allow_state(group_id, new_state):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO allow_states (group_id, state)
                          VALUES (?, ?)''', (group_id, new_state))
        conn.commit()

# 函数用于获取用户状态
def get_user_state(user_id):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT state FROM user_states WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "聊天"

# 函数用于获取群消息开关状态
def get_allow_state_from_db(group_id):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT state FROM allow_states WHERE group_id = ?''', (group_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

# 函数用于插入记录到db_path表
def insert_into_db_path(source_id, path):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO db_path (source_id, path)
                          VALUES (?, ?)''', (source_id, path))
        conn.commit()

# 函数用于插入记录到db_path表
def insert_into_db_path_site(source_id, path):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO db_path (source_id, path_site)
                          VALUES (?, ?)''', (source_id, path))
        conn.commit()

# 函数用于更新数据表db_path中source_id的值
def update_db_path(source_id, new_path):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE db_path SET path = ? WHERE source_id = ?''', (new_path, source_id))
        conn.commit()

# 函数用于获取source_id的path字段值
def get_path_by_source_id(source_id):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT path FROM db_path WHERE source_id = ?''', (source_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
# 函数用于更新网站路径
def update_db_path_site(source_id, new_path):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE db_path SET path_site = ? WHERE source_id = ?''', (new_path, source_id))
        conn.commit()

# 函数用于获取网站路径
def get_path_by_source_id_site(source_id):
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT path_site FROM db_path WHERE source_id = ?''', (source_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

def insert_chat_history(source_id, query, answer, user_state):
    # 插入当前聊天历史记录
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history_now (source_id, query, answer, user_state) VALUES (?, ?, ?, ?)", (source_id, query, answer, user_state))
        conn.commit()

def insert_chat_history_xlsx(source_id, query, answer,user_state="聊天"):
    # 检查文件是否存在
    filename = 'history_old.xlsx'
    if not os.path.isfile(filename):
        # 如果文件不存在，创建新文件并写入表头
        wb = Workbook()
        ws = wb.active
        ws.append(["source_iD", "query", "answer", "create_time", "user_state"])
        wb.save(filename)

    # 打开工作簿并插入新记录
    wb = load_workbook(filename)
    ws = wb.active
    ws.append([source_id, query, answer, datetime.now(), user_state])
    wb.save(filename)


def delete_oldest_records():
    # 从当前聊天历史记录表中删除时间最晚的两条记录
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM history_now WHERE id IN (SELECT id FROM history_now ORDER BY timestamp ASC LIMIT 2);"
        cursor.execute(sql)
        conn.commit()

def delete_all_records(source_id, user_state):
    # 从当前聊天历史记录表中删除符合条件的所有记录
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history_now WHERE source_id = ? and user_state = ?", (source_id, user_state))
        conn.commit()

def fetch_chat_history(source_id, user_state):
    # 从数据库中提取聊天历史记录
    with db_lock:
        conn = get_database_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT query, answer FROM history_now WHERE source_id = ? and user_state = ?", (source_id, user_state))
            return cursor.fetchall()
        except:
            return []




# # 示例调用
# update_db_path("415135222", r"D:\projects\rag-bot\chroma_db\415135222_1")
# print(get_path_by_source_id("415135222"))
