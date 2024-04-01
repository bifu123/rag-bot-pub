import threading
import websocket
import json
from config import ws_url

from dal import *

def on_message(ws, message):
    # 处理收到的消息
    #print("Received message:", message)
    # 解析消息
    data = json.loads(message)
    # 处理不同类型的事件
    if "post_type" in data:
        post_type = data["post_type"]
        if post_type == "message":  # 私聊消息或群聊消息
            handle_message_thread(data)
        elif post_type == "notice":  # 通知类型的事件，比如好友申请、群邀请等
            handle_notice_thread(data)
        elif post_type == "request":  # 请求类型的事件，比如加好友请求、加群请求等
            handle_request(data)
        # 其他类型的事件可以继续添加处理逻辑
    else:
        print("Unknown message format:", message)

def handle_message_thread(data):
    threading.Thread(target=handle_message, args=(data,)).start()

def handle_notice_thread(data):
    threading.Thread(target=handle_notice, args=(data,)).start()

def handle_message(data):
    # 处理私聊消息或群聊消息
    print("\n", "="*15, "Message","="*15, "\n", data)
    message_action(data)

def handle_notice(data):
    # 处理通知类型的事件
    print("\n", "="*15, "Notice", "="*15, "\n", data)
    event_action(data)

def handle_request(data):
    # 处理请求类型的事件
    print("Request:", data)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection established")

# 建立 WebSocket 连接
ws_url = ws_url
ws = websocket.WebSocketApp(ws_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
