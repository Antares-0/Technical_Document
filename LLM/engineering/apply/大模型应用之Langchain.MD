# 大模型应用之Langchain

Langchain是一个用于将大模型快速部署对外提供服务的工具

## 一、环境搭建
1. AnaConda是一个python环境管理工具，可以理解为Java中的JDK，并支持自己手动配置；
   - 与python自带的pip包管理工具功能类似，但是比它更自动化一些
   - Anaconda生成的目录通常在/opt/anaconda3/envs/{env_name}/python，选择对应的python文件
2. Pycharm中将从AnaConda配置的环境在settings-project里配置好
3. 环境搭建可以参考[1]
4. LangChain基本架构
   - 基本架构
   
   ![LangChain架构](../../fig/langChainArc.svg)
   - LangSmith：用于观测，相当于监控工具
   - LangServe：将LangChain的功能封装成Rest风格的请求
   - Templates：LangChain官方提供的一些AI任务模板
   - LangChain库
     - LangChain-Community：第三方集成，主要包括langchain集成的第三方组件，可以理解为社区贡献
     - LangChain-Core：基础抽象和 LangChain 表达语言。
     - LangChain：主要包括链(chain)、代理(agent)和检索策略。

## 二、LangChain初体验
1. 在Python中编写如下代码
   ```python
   # 引入提示词模版
   from langchain_core.prompts import ChatPromptTemplate
   
   # 引入OpenAI
   from langchain_openai import ChatOpenAI
   llm = ChatOpenAI(
       api_key="{my API Token}",
       base_url="https://ai.nengyongai.cn/v1"
   )
   
   # 编写prompt
   prompt = ChatPromptTemplate.from_messages([
       ("system", "你是世界级的专家"),
       ("user", "{input}")
   ])
   
   # 链式反应，将prompt作为llm的输入传输给LLM
   chain = prompt | llm
   result = chain.invoke({"input": "帮我简单介绍python，50字以内"})
   print(result)
   ```
2. 调用大模型接口需要配置自己的APIkey，可以选择以下两种方案
   - 找到大模型官网，注册账号生成APIlkey
   - 在国内的中转软件中实现，个人用的是[4]，在工作台配置新的key，在模型列表页面选取可用模型列表，具体使用参考[5]
3. 总结：
   - python对大模型的调用相关功能已经封装到langChain
   - 需要APIkey才能调用大模型`export OPENAI_API_KEY="sk-mykey"`
4. 使用解析器对文本进行美化，引入了parser
   ```python
   # 引入提示词模版
   from langchain_core.output_parsers import StrOutputParser
   from langchain_core.prompts import ChatPromptTemplate
   
   # 引入OpenAI
   from langchain_openai import ChatOpenAI
   llm = ChatOpenAI(
       api_key="apikey",
       base_url="https://ai.nengyongai.cn/v1"
   )
   
   prompt = ChatPromptTemplate.from_messages([
       ("system", "你是世界级的专家"),
       ("user", "{input}")
   ])
   
   # 引入了parser进行输出美化
   parser = StrOutputParser()
   
   chain = prompt | llm | parser
   
   result = chain.invoke({"input": "帮我简单介绍python，50字以内"})
   print(result)
   # 输出结果：
   # Python是一种简洁易学的高级编程语言，广泛用于数据分析、人工智能和Web开发。
   ```
5. 代码可以参考`src/main/java/easyProject/LLM/langchain_test.py`

## 三、LangChain提示词工程
1. 聊天提示词工程模版
   - 代码
   ```python
   from langchain_core.prompts import ChatPromptTemplate

   chat_template = ChatPromptTemplate.from_messages([
       ("system", "你是一位人工智能助手，你的名字是{name}。"),
       ("human", "你好"),
       ("ai", "我很好，谢谢！"),
       ("human", "{user_input}")
   ])
   
   # 通过模板参数格式化模板内容
   messages = chat_template.format_messages(name="Bob", user_input="你的名字叫什么？")
   print(messages)
   ```
   - 说明
     - 聊天模型（Chat Model）以聊天消息列表作为输入，这个聊天消息列表的消息内容也可以通过提示词模板进行管理。这些聊天消息与原始字符串不同，因为每个消息都与“角色(role)”相关联。
     - 在OpenAI的Chat Completion API中，Openai的聊天模型，给不同的聊天消息定义了三种角色类型分别是助手(assistant)、人类（human）或系统（system）角色：
       - 助手(Assistant) 消息指的是当前消息是AI回答的内容
       - 人类（user）消息指的是你发给AI的内容
       - 系统（system）消息通常是用来给AI身份进行描述
2. 简单字符串提示词工程模版
   - 代码
   ```python
   from langchain.prompts import PromptTemplate

   prompt_template = PromptTemplate.from_template(
       "给我讲一个关于{content}的{adjective}笑话。"
   )
   
   # 通过模板参数格式化提示模板
   result = prompt_template.format(adjective="冷", content="猴子")
   print(result)
   ```
   - 说明
     - 这个模版就是简单的字符串占位拼接逻辑
3. 添加示例
   - 代码
   ```python
   from langchain.prompts.few_shot import FewShotPromptTemplate
   from langchain.prompts.prompt import PromptTemplate

   examples = [
       {
           "question": "谁的寿命更长，穆罕默德·阿里还是艾伦·图灵？",
           "answer":
           """
           这里需要跟进问题吗：是的。
           跟进：穆罕默德·阿里去世时多大？
           中间答案：穆罕默德·阿里去世时74岁。
           跟进：艾伦·图灵去世时多大？
           中间答案：艾伦·图灵去世时41岁。
           所以最终答案是：穆罕默德·阿里
           """
       },
       {
           "question": "craigslist的创始人是什么时候出生的？",
           "answer":
           """
           这里需要跟进问题吗：是的。
           跟进：craigslist的创始人是谁？
           中间答案：craigslist由Craig Newmark创立。
           跟进：Craig Newmark是什么时候出生的？
           中间答案：Craig Newmark于1952年12月6日出生。
           所以最终答案是：1952年12月6日
           """
       }
   ]
   
   example_prompt = PromptTemplate(input_variables=["question", "answer"], template="问题：{question}\\n{answer}")

   print(example_prompt.format(**examples[0]))
   
   ```
   - 说明：相当于给模型“打个样”，告诉模型应该以什么样的格式输出，有点像一个小型的RAG，大模型会按照上面的模版输出问答流程
4. 示例选择器（使用向量化模型，类似RAG）

## 四、LangChain的工作流编排机制
1. LangChain使用API流式返回，代码可参考`src/main/java/easyProject/LLM/stream_llm.py`
   - ```python
     from langchain_openai import ChatOpenAI
     llm = ChatOpenAI(
         api_key="key",
         base_url="https://ai.nengyongai.cn/v1",
         model="gpt-4",
     )
     chunks=[]
     for chunk in llm.stream("天空是什么颜色？"):
         chunks.append(chunk)
         print(chunk.content, end="|", flush=True)
     ```
   - 说明
     - 流式返回底层上使用的SSE协议，SSE与传统的webSocket之间的区别可以参考`ComputerNetwork/SSE与WebSocket.MD`
     - SSE返回的每个报文被转换成chunk
2. 链式调用，代码可参考`src/main/java/easyProject/LLM/astream_llm.py`
   - ```python
     # astream_chain.py
     import asyncio
     from langchain_core.output_parsers import StrOutputParser
     from langchain_core.prompts import ChatPromptTemplate
     from langchain_openai import ChatOpenAI
     
     llm = ChatOpenAI(
         api_key="mykey",
         base_url="https://ai.nengyongai.cn/v1",
     )
     
     prompt = ChatPromptTemplate.from_template("给我讲一个关于{topic}的笑话")
     parser = StrOutputParser()
     # 链式调用
     chain = prompt | llm | parser
     
     async def async_stream():
         async for chunk in chain.astream({"topic": "鹦鹉"}):
             print(chunk, end="|", flush=True)
     
     asyncio.run(async_stream())

     ```
   - 说明：`chain = prompt | llm | parser`就是所谓的链式调用
   - 上述所谓的流式就是通过SSE的基础原理实现的
3. 事件驱动【Event驱动】，代码参考`src/main/java/easyProject/LLM/event_llm.py`
   - ```python
     import asyncio
     from langchain_openai import ChatOpenAI
     
     llm = ChatOpenAI(
         api_key="mykey",
         base_url="https://ai.nengyongai.cn/v1",
     )

     # 开启异步方法
     async def async_stream():
         events = []
         async for event in llm.astream_events("hello", version="v2"):
             events.append(event)
         print(events)
     
     asyncio.run(async_stream())
     ```
   - 说明：所谓的事件驱动，就是将调用大模型的过程按照事件的形式标准化起来，方便进行日志排查和定位问题
4. 总结：
   LangChain的工作流编排机制，包含三种基本类型，也就是LangChain调用大模型的三种方式：
   - 同步方式：stream、invoke、batch
   - 异步方式：astream、ainvoke、abatch
   - 事件驱动方式：astream_events

## 五、LangChain服务部署和链路监控
1. 环境配置
   ```bash
   # 安装langchain的包管理工具
   #安装pipx，参考：https://pipx.pypa.io/stable/installation/
   pip install pipx
   #加入到环境变量，需要重启PyCharm
   pipx ensurepath
   
   # 安装poetry，参考：https://python-poetry.org/docs/
   pipx install poetry
   
   #安装 langchain-openai 库，例如：poetry add [package-name]
   poetry add langchain
   poetry add langchain-openai
   
   # 安装langserve
   pip install --upgrade "langserve[all]
   
   # 启动LangServe项目
   pip install -U langchain-cli
   
   # 创建一个名为myapp的langserve项目
   langchain app new myapp
   
   # 启动服务
   poetry run langchain serve --port=8000
   ```
2. poetry可以理解为是langchain的包管理工具
3. travily可以先检索搜索引擎，再将引擎的内容传给LLM
4. langserve还有一些日志组件，用于检索问题等
5. langserve就是集成了类似SpringBoot的一个组件

## 六、Langchain消息管理和聊天历史存储
1. 通过session_id来实现上下文的管理
   - 代码
     ```python
     with_message_history.invoke(
         {"ability": "math", "input": "余弦是什么意思？"},
         config={"configurable": {"session_id": "abc123"}},
     )
     
     # 记住
     with_message_history.invoke(
         {"ability": "math", "input": "什么?"},
         config={"configurable": {"session_id": "abc123"}},
     )
     
     # 新的 session_id --> 不记得了。
     with_message_history.invoke(
         {"ability": "math", "input": "什么?"},
         config={"configurable": {"session_id": "def234"}},
     )
     ```
   - 说明：通过config中的session_id来匹配对话，实现对话管理
2. 聊天消息存储：可以将对话历史存储到Redis中
   - 代码
     ```python
     from langchain_community.chat_message_histories import RedisChatMessageHistory
     def get_message_history(session_id: str) -> RedisChatMessageHistory:
         return RedisChatMessageHistory(session_id, url=REDIS_URL)
     with_message_history = RunnableWithMessageHistory(
         runnable,
         get_message_history,
         input_messages_key="input",
         history_messages_key="history",
     )
     ```


## 七、多模态输入和自定义格式输出
1. 图片作为输入
   - 第一种传输方式就是传输图片的url，但是如果大模型访问不到就很尴尬了，需要大模型自己去访问图片
   ```python
   message = HumanMessage(
       content=[
           {"type": "text", "text": "用中文描述这张图片中的天气"},
           {"type": "image_url", "image_url": {"url": image_url}},
       ],
   )
   response = model.invoke([message])
   print(response.content)
   ```
   - 第二种传输方式base64，将图片的二进制数据转换为base64编码的数据表示，直接传给大模型
   ```python
   import base64
   import httpx

   image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
   message = HumanMessage(
       content=[
           {"type": "text", "text": "用中文描述这张图片中的天气"},
           {
               "type": "image_url",
               "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
           },
       ],
   )
   response = model.invoke([message])
   print(response.content)
   ```
   - 注意多模态输入，模型必须支持多模态
2. 自定义格式输出，指定parser【<font color='yellow'>参考[7]</font>】
   - JSON格式输出：
   ```python
   ## json_output_parser_no_pydantic.py
   joke_query = "Tell me a joke."
   parser = JsonOutputParser()
   prompt = PromptTemplate(
       template="Answer the user query.\n{format_instructions}\n{query}\n",
       input_variables=["query"],
       partial_variables={"format_instructions": parser.get_format_instructions()},
   )
   chain = prompt | model | parser
   chain.invoke({"query": joke_query})
   ```
   - XML格式输出：甚至可以自己指定标签的name
   ```python
   # xml_output_parser.py
   parser = XMLOutputParser()
   # 我们将在下面的提示中添加这些指令
   parser.get_format_instructions()
   ```

## 八、自定义工具调用
1. Langchain提供了三种创建工具的方式
   - `@tool`注解
     ```python
     from langchain_core.tools import tool
  
     @tool
     def multi(a: int, b: int) -> int:
     """twuuu"""
     return a * b
     
     print(multi.name)
     print(multi.description)
     print(multi.args)
     ```
   - `StructuredTool.from_function`包装
     ```python
     from langchain_core.tools import StructuredTool
     import asyncio
     
     # 同步模式
     def multi(a: int, b: int) -> int:
         """twuuu"""
         return a * b
     
     # 异步模式
     async def amulti(a: int, b: int) -> int:
         """twuuu"""
         return a * b
     
     # coroutine异步调用的方法 multi同步调用的方法
     async def main():
         calculator = StructuredTool.from_function(func=multi, coroutine=amulti)
         print(calculator.invoke({"a": 2, "b": 3}))
         print(await calculator.ainvoke({"a": 2, "b": 5}))
     
     asyncio.run(main())
     ```
   - 子类化`BaseTool`

2. 处理工具错误
   - 引入ToolException
   ```python
   from langchain_core.tools import ToolException, StructuredTool

   def get_weather(city: str) -> int:
       """获取给定城市的天气。"""
       raise ToolException(f"错误：没有名为{city}的城市。")
   
   get_weather_tool = StructuredTool.from_function(
       func=get_weather,
       # 设置为True，返回异常文本，设置为False，直接将异常抛出去
       handle_tool_error=True,
   )
   
   print(get_weather_tool.invoke({"city": "foobar"}))
   # 错误：没有名为foobar的城市。
   ```
   - 引入异常处理函数
   - 引入异常处理文本
3. 调用外部工具
   - 引入外部工具并调用，简单来说就是使用`tool.invoke()`
   ```python
   from langchain_community.tools import WikipediaQueryRun
   from langchain_community.utilities import WikipediaAPIWrapper
   api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
   tool = WikipediaQueryRun(api_wrapper=api_wrapper)
   print(tool.invoke({"query": "langchain"}))
   ```

## 九、基于Langchain快速开发Agent应用









参考文档  
[1] AnaConda和Pycharm环境配置：https://blog.csdn.net/matt45m/article/details/134595417
[2] B站参考教程：https://www.bilibili.com/video/BV1BgfBYoEpQ
[3] https://www.bilibili.com/video/BV1g1CKYUExu
[4] 能用AI官网：https://ai.nengyongai.cn/panel
[5] 能用AI使用指南：https://blog.csdn.net/zhouzongxin94/article/details/144021130
[6] B站资源文档：https://www.yuque.com/monkeyyuanma/iv3tgl/qgrry0x280n29c32 ，密码cm5k
[7] Langchain的parser文档：https://python.langchain.com/v0.1/docs/modules/model_io/output_parsers/types/yaml/
[8] Langchain官方文档：https://python.langchain.com/docs/versions/v0_2/overview/

