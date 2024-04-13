# 你现在唯一没有出错的版本是：

import asyncio
import websockets
import json
from aiohttp import web

# 全局变量，用于保存 WebSocket 连接
websocket_connections = []

async def http_handler(request):
    print("Received HTTP request:", request.method, request.path)
    return web.Response(text="Hello, world!")

async def send_private_msg(request):
    global websocket_connections
    try:
        data = await request.json()
        #print("Received POST request at /send_private_msg:", data)
        print(len(data))
        if data["post_type"]:
            # 存储 WebSocket 连接返回的消息
            websocket_responses = []
            # 向所有 WebSocket 连接发送消息
            for websocket in websocket_connections:
                await websocket.send(json.dumps(data)) 
        else:
            print("显示出来，不要发给WS")
            
        # 返回发送的数据的JSON格式
        #return web.Response(text=data["message"], content_type="text/plain")
        return web.Response(text="ok")
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return web.Response(text="Error decoding JSON")

async def websocket_handler(websocket, path):
    global websocket_connections
    print("WebSocket connection established")
    websocket_connections.append(websocket)
    
    try:
        async for message in websocket:
            print("Received WebSocket message:", message)
            # 在这里处理接收到的 WebSocket 消息
            # 这里只是简单打印接收到的消息
    finally:
        print("WebSocket connection closed")
        websocket_connections.remove(websocket)

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


# 请修改代码：让25533端同时可以接受get请求，请