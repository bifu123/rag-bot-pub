

from config import *
import requests
import json


    
def get_nickname_by_user_id(user_id):
    data = requests.get(http_url+"/get_friend_list").text
    data = json.loads(data)
    # print(data)
    for item in data["data"]:
        # print(item["user_id"])
        if str(item["user_id"]) == str(user_id):
            print(item["nickname"])
            # return item["nickname"]
    # return None


get_nickname_by_user_id("415135222")

# bot_nick_name = get_nickname_by_user_id("3152246598")
# print(bot_nick_name)