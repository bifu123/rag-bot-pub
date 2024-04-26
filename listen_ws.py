import threading
import websocket
import json
from config import ws_url
from dal import *

def on_message(ws, message):
    # 处理收到的消息
    # print("Received message:", message)
    data = json.loads(message)
    if "post_type" in data:
        post_type = data["post_type"]
        if post_type == "message":  
            handle_message_thread(data)
        elif post_type == "notice":  
            handle_notice_thread(data)
        elif post_type == "request":  
            handle_request(data)
    else:
        print("Unknown message format:", message)

def handle_message_thread(data):
    threading.Thread(target=handle_message, args=(data,)).start()

def handle_notice_thread(data):
    threading.Thread(target=handle_notice, args=(data,)).start()

def handle_message(data):
    # 处理私聊消息或群聊消息
    print("\n", "="*20, "Message","="*20, "\n", data)
    message_action(data)

def handle_notice(data):
    # 处理通知类型的事件
    print("\n", "="*20, "Notice", "="*20, "\n", data)
    event_action(data)

def handle_request(data):
    # 处理请求类型的事件
    print("Request:", data)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    # 连接关闭时重新连接
    print("Connection closed")
    ws.run_forever()

def on_open(ws):
    print("Connection established")

# 设置自动重连
def create_connection():
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# 建立 WebSocket 连接
create_connection()
