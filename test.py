import asyncio
import websockets
import json
from aiohttp import web

async def websocket_handler(websocket, path):
    data = {
        "post_type": "message",
        "message_type": "private",
        "time": 1712140345,
        "self_id": 3152246598,
        "sub_type": "friend",
        "raw_message": "hello",
        "font": 0,
        "sender": {
            "age": 0,
            "nickname": "不知道是谁",
            "sex": "unknown",
            "user_id": 415135222
        },
        "message_id": -1518347102,
        "user_id": 415135222,
        "target_id": 3152246598,
        "message": "张三考了多少分"
    }
    await websocket.send(json.dumps(data))

async def http_handler(request):
    print("Received HTTP request:", request.method, request.path)
    return web.Response(text="Hello, world!")

async def send_private_msg(request):
    data = {}
    try:
        data = await request.json()
        print("Received POST request at /send_private_msg:", data)
        
        # 获取查询参数
        user_id = request.query.get('user_id', '')
        message = request.query.get('message', '')
        print(f"User ID: {user_id}, Message: {message}")
        
        return web.Response(text="OK")
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return web.Response(text="Error decoding JSON")

async def main():
    websocket_server = await websockets.serve(websocket_handler, "0.0.0.0", 25522)
    print("WebSocket server running on 0.0.0.0:25522")
    
    http_app = web.Application()
    http_app.router.add_route('GET', '/', http_handler)
    http_app.router.add_route('POST', '/send_private_msg', send_private_msg)
    http_runner = web.AppRunner(http_app)
    await http_runner.setup()
    http_site = web.TCPSite(http_runner, "0.0.0.0", 25533)
    print("HTTP server running on 0.0.0.0:25533")
    await http_site.start()
    
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())




# 发送方发送是这样的：
# url = "http://127.0.0.1:25533/send_private_msg"
# params = {
#     "user_id": "415135222", 
#     "message": "你好"
# } 

# 在这页上怎把params获取并显示出来