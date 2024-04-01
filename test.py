from send import * 

data = {
    'post_type': 'message',
    'message_type': 'group',
    'time': 1711672670,
    'self_id': 3152246598,
    'sub_type': 'normal',
    'font': 0,
    'raw_message': '[CQ:at,qq=3152246598] 你好',
    'sender': {
        'age': 0,
        'area': '',
        'card': '',
        'level': '',
        'nickname': '不知道是谁',
        'role': 'owner',
        'sex': 'unknown',
        'title': '',
        'user_id': 415135222
    },
    'message_id': -1260026132,
    'anonymous': None,
    'group_id': 499436648,
    'message': '[CQ:at,qq=3152246598] 你好',
    'message_seq': 17524,
    'user_id': 415135222
}


print(get_chat_type(data))

'''
{'chatType': 'group_at', 'user_id': '415135222', 'group_id': '499436648', 'at': True}
'''