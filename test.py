import base64
import json
import re

def get_urls(text):
    # 定义一个正则表达式模式，用于匹配URL
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    # 使用findall函数查找文本中所有匹配的URL
    urls = re.findall(url_pattern, text)
    # 如果找到了URL，则返回True，否则返回False
    if urls:
        # 打印找到的所有URL
        for url in urls:
            print(url)
            # 将URL列表编码为BASE64字符串
        encoded_urls = base64.b64encode(json.dumps(urls).encode()).decode()   
        return "yes", encoded_urls
    else:
        print("未找到任何URL。")
        return "no", "nourl"

# 要处理的文本
text = "百度搜索https://zwfw.guizhou.gov.cn/bsznindex.do?otheritemcode=11520000009390359W252201102600001&orgcode=-7353064029638146384&areacode=520000。可以搜索很多东西"

# 调用get_urls函数并获取结果
matched, urls = get_urls(text)

# 将URL列表编码为BASE64字符串
encoded_urls = base64.b64encode(json.dumps(urls).encode()).decode()
print("BASE64编码后的URL字符串:", encoded_urls)

# 将BASE64编码后的字符串解码还原为URL列表
decoded_urls = json.loads(base64.b64decode(encoded_urls).decode())
print("还原后的URL列表:", decoded_urls)
