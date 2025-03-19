# YLBot（元龙机器人QQ版）

## 简介
YLBot是一个以QQ聊天界面作为语言模型与用户交互端的RAG应用。一是它很方便地用QQ进行各种问答和控制操作，二是它借助了QQ强大的社交功能，使得它的推广和使用成本很低。三是支持群文档和个人文档，它在让个人可以用自己文档对话的同时，也让群就某一领域讨论与学习变得更加智能。

## 部分界面载图
![上传群文档](images/上传群文档.png)
![后台量化](images/后台量化.png)
![量化成功及回答](images/量化成功及回答.png)
![切换聊天](images/切换聊天.png)
![我的文档命令](images/我的文档命令.png)

## 怎样使用
### [安装vs_BuildTools]https://aka.ms/vs/17/release/vs_BuildTools.exe

### 登陆go-cqhttp
这部份内容请自补，在此不作赘述。

### 安装环境
- windows可以使用conda环境安装部署，linux不建议用
```bash
conda create -n rag-bot python=3.11
git clone https://github.com/bifu123/rag-bot-pub
cd rag-bot
conda activate rag-bot
pip install requirements.txt
```

### 创建环境变量
当前目录下新建文件.env，内容如下：
```
# 通义千问 api key 
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

### 状态
- 聊天：与大模型直接对话
- 文档问答：加载预置的文档，以文档内容来回复用户问题。
- 知识库问答：当作为知识的文档较大，超出了大模型每次允许的大小，则需要在本地分片检索，进行词量化嵌入，就是RAG，分私聊状态下创建的私有知识库和在群中创建的群知识库两种。
- 插件问答：这是机器的扩展功能，理论上只要python能实现的都能实现。
比如，要切换到“文档问答”状态，可使用操控命令“/文档问答”。

### 插件
 - [查看插件文档](plugin.md)
 插件是本机人最高级的应用，分两种模式：串行和并行。串行模式是上一函数的结果是下一函数的参数，最后一个函数结果作为LLM上下文的一部分；并行模式是所有函数返回的结果一并交给LLM。
 调用如：::test 。即执行所有name_space="test"的函数，而不会调用其它插件函数。
 插件视频教程：
 - [01-插件的实现原理(https://www.bilibili.com/video/BV1YH4y1P75r/)](https://www.bilibili.com/video/BV1YH4y1P75r/)
 - [02-插件的属性(https://www.bilibili.com/video/BV18m411C7XM/)](https://www.bilibili.com/video/BV18m411C7XM/)
 - [03-串行模式的插件(https://www.bilibili.com/video/BV14x4y1B7vd/)](https://www.bilibili.com/video/BV14x4y1B7vd/)
 - [04-插件实例(https://www.bilibili.com/video/BV1FC411n7Hp/)](https://www.bilibili.com/video/BV1FC411n7Hp/)

 ### 命名空间
命名空间是不同状态下不同语料背景的逻辑集合，比如在“插件问答”状态下，有命名空间“固定资产管理”、“记事本”，它们或者连接了本地业务系统、或者加载了本地文档，除了默认的“test”命名空间外，其余的都在插件中实现。比如，要切换到一个名为“记事本”的命名空间，先发送命令“/插件问答”，再发送“：：记事本”（：不分全角半角）即进入了该命名空间。元龙机器人是没有退出命名空间命令的，只能从一个命名空间切换到另一个命名空间，如果不想加载某个空间的功能和语料，可以使用“/聊天”切换到聊天状态，再用“：：test”切换到默认命名空间，直接与大模型对话。

### 分步式命令
分步式命令指的是一个命令需要多次交互。比如下面场景：
用户：/姓名
机器人：请输入姓
用户：张
机器人：请输入名
用户：三丰
机器人：你的姓名是张三丰
 - 分步式命令视频教程： [分步式命令(https://www.bilibili.com/video/BV1rx4y1B7Ez/)](https://www.bilibili.com/video/BV1rx4y1B7Ez/)

 ### 邀请
 假设在一个群聊环境中，用户A在某个状态和某个命名空间中，而另一个用户处在另一状态或另一命名空间中，机器人对于他们的问题将会使用不同的功能和语料背景来回复他们，为了让机器人能共同参与彼此（或者群中所有人）的同一话题，并在同一个语料背景、功能下讨论、聊天，可以使用邀请功能。比如A用户目前在群中处在“MCP学习”这一空间中，希望B也进入这一空间，可以使用“/邀请”命令，如果希望群中所有人全部进入此空间，可以使用“/邀请群”命令。邀请功能的命令属于分步式命令，发送“/邀请”或“/邀请群”指令后，会与机器人进行多步的交互。
 邀请功能视频教程：
 - [邀请功能(https://www.bilibili.com/video/BV1Vw4m117SY/)](https://www.bilibili.com/video/BV1Vw4m117SY/)

 元龙机器人有自己特有的概念和理念，需要在使用中进行体验。

### 联系作者
QQ: 415135222
 
