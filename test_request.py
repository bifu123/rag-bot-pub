import requests

while True:
    input_data = input("请输入请求：")
    # 定义要发送的数据
    data1 = {
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
        "message": input_data
    }

    data2 = {
        "user_id": 415135222,
        "message": input_data
    }

    # 发送POST请求
    response = requests.post("http://127.0.0.1:25533/send_private_msg", json=data2)


    # 显示返回数据
    print(response.text)
