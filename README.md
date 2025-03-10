# YLBot
## 简介
YLBot是一个以QQ聊天界面作为语言模型与用户交互端的RAG应用。做这样一个应用，早有想法。从元龙山回来后，心神俱废，日渐消沉，需要拾起以前感兴趣的东西来调节自己，虽然年事己高，仍然觉得hello word是一个不错的东西。于是一直研究nonebot，可是弄了个来月，不得所以，于是明白：它经过高度封装后有了自己的一套，对于个人而言，学习它将付出更大的学习成本，于是决定自己写一个bot。现在这个bot有这些好处：一是它很方便地用QQ进行各种问答和控制操作，二是它借助了QQ强大的社交功能，使得它的推广和使用成本很低。三是支持群文档和个人文档，它在让个人可以用自己文档对话的同时，也让群就某一领域讨论与学习变得更加智能。
## 免责申明
本应用旨在研究语言模型交流及onebot标准，请勿用于违法犯罪活动，一切资源均来自网络，不提供任何破解服务。如需生产使用，请申请官方QQ机器人。
## 部分界面载图
![上传群文档](images/上传群文档.png)
![后台量化](images/后台量化.png)
![量化成功及回答](images/量化成功及回答.png)
![切换聊天](images/切换聊天.png)
![我的文档命令](images/我的文档命令.png)
## 怎样使用
### [安装vs_BuildTools]https://aka.ms/vs/17/release/vs_BuildTools.exe
### 安装环境
- windows可以使用conda环境安装部署，linux不建议用
```bash
conda create -n rag-bot python=3.11
git clone https://github.com/bifu123/rag-bot
cd rag-bot
conda activate rag-bot
pip install requirements.txt
# 如果安装 requirements.txt失败，或者安装后运行有问题，请尝试执行以下命令:
pip install websocket-client bs4 dashscope langchain_google_genai langchain_community langchain openpyxl requests langchain_groq webdriver-manager selenium==4.9.0 python-docx "unstructured[xlsx]" unstructured[pdf] python-dotenv
```
### 创建环境变量
当前目录下新建文件.env，内容如下：
```
# deepseek api key 
DEEPSEEK_API_KEY = "你的 deepseek api key" # 申请地址：https://platform.deepseek.com/
# gemini api key 
GOOGLE_API_KEY = "你的 gemini api key" # gemini api key 的申请地址：https://makersuite.google.com/app/prompts/new_freeform ，条件：拥有google帐号
# 通义千问 api key
DASHSCOPE_API_KEY  = "你的 DASHSCOPE_API_KEY"
# moonshot ai kimi api key
MOONSHOT_API_KEY = "你的 moonshot ai kimi api key" # 在这里申请: https://platform.moonshot.cn/console/api-keys
# groq
GROQ_API_KEY = "你的 groq api key" # 在这里申请: https://console.groq.com/keys
# cohere 重排模型 API KEY
COHERE_API_KEY = "你的 cohere api key" # 申请地址：https://dashboard.cohere.com/api-keys
```
以上的KEY的并不全部都必须，使用哪个模型就填写哪个KEY

此外，还需要安装chrome和firefox
windows下，直接下载安装chrome和firefox
linux请用下面命令：
```bash
sudo apt install chromium-browser chromium-chromedriver firefox # 不过一般LINUX都预装了firefox
```

### 修改配置文件config.py
请根据文件中提示，结合你的实际情况修改，其中涉及了对接ollama和go-cqhttp的部分，如果不会，先补上这部分知识，可以参看我在b站上的视频，也可以加QQ群：222302526 

### 启动程序
```bash
python listen_ws.py
```
程序启动后，它会用socket监听go-cqhttp的事件和消息，并根据这些事件和消息运行程序逻辑，作出响应。

### 操控命令
| 命令名称   | 作用                                       | 备注                                                 |
|------------|--------------------------------------------|------------------------------------------------------|
| /我的文档   | 列出当前用户保存在服务器上的所有私人文档或所在群中公共文档 | 自动判断用户所处环境加载不同文档路径               |
| /删除文档   | 删除某个文档                                 | 用法：/删除文档|要删除的文档完整路径                     |
| /量化文档   | 将当前用户私人文档或用户所在群的公共文档量化 | 量化时需要程序进程处于闲置，否则无法更新向量库，如何解决这个问题，请众爱卿献策！ |
| /上传文档   | 上传文档到服务器                             | 允许常规的文档                                       |
| /文档问答   | 就当前用户的文档或其所在群的文档进行问答     | 答案仅限于文档内容中                                 |
| /插件问答   | 加载执行插件返回的结果为上下文供LLM推理     | 插件可以自由扩展                                 |
| /聊天      | 使用大模型进行对话，不加载文档知识库        | 模型可以在config.py中设置更换                         |
| /我的状态   | 显示当前用户处理文档问答还是聊天状态         | 可以根据命令提示切换状态                             |
| /开启群消息 | 所有群成员的发言，机器人都会回答            | 可以用于活跃群或具有足够针对性的知识，但也会给群带来骚扰，请酌情使用 |
| /关闭群消息 | 关闭之后，在群中除非@它，否则机器人不会作任何反应 | 一般群的默认值即为群消息关闭                         |
| /清空记录 | 清空用户私有或者群中公共的问答历史记录 | 在聊天历史过多或话题繁杂而影响了机器人分析回复质量时使用                         |
| /我的命名空间 | 显示当前用户所处的插件命名空间 | 插件命名空间用于插件功能的隔离，精准定位到某个关键词下一个或多个插件                        |
| /帮助 | 请切换至“插件问答”状态，再进入“help”命名空间 | 根据README.MD文件回答提问                       |

 
 ## 重要更新
  ### 2025-3-10
 - 增加了deepseek支持
 - 将 api key 存入在.env文件中
 - 升级了lanchain和库
 - 更正了ollama调用方式
 - 开源了本项目
 - 删除了“网站问答”这个状态
 - 编写了“帮助”插件
 ### 2025-2-13
 - 解决新消息类型guid带来的变量未赋值错误
### 2024-4-30
 - 解决新开窗口运行后不会自动关闭的bug
### 2024-4-29
 - 解决分步式命令bug
### 2024-4-23
 - 增加了对ollama llama3的支持
 - 增加了对groq的支持
 - 增加分步式命令功能，比如：/邀请
 注意：必须更新langchian、langchain_community到最新版，否则llama3会发送大量乱码字符。删除user.db，重新运行程序，因为数据表结构发生了改变。
### 2024-4-13
 - ![增加插件支持](plugin.md)
 插件分两种模式：串行和并行。串行模式是上一函数的结果是下一函数的参数，最后一个函数结果作为LLM上下文的一部分；并行模式是所有函数返回的结果一并交给LLM。
 调用如：::test 。即执行所有name_space="test"的函数，而不会调用其它插件函数。
 - 更新状态bug
请停止程序，删除user.db，重新运行程序，否则出错

 ### 2024-4-10
 - 增加 moonshot ai kimi 模型 API 

### 2024-4-3
 - 发送文档后立即解读，并保持有该文档的记忆。
 - 使用异步函数调用，减少并发访问时的阻塞。

### 2024-4-1
 - 默认使用通义千问长文本模型。
 - 增加问答历史记录记忆功能

 ### 2024-3-29 
 - 经过实验发现google的embedding模型embedding-001对中文支持确实存在不稳定的问题，从而导致LLM推理检索出错，推荐使用ollama的embedding
 - 将 /文档问答 命令改为 /知识库问答 。这种模式下，用户文档目录下的文档经过分割向量由 langchain交LLM推理。
 - 增加 /文档问答 功能。这种模式下，用户文档目录下的文档不经过分割向量直接发给LLM推理。
