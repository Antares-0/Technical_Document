# 第03章：LangChain使用之Chains


## 一、`Chains`的基本使用
1. `Chain`的基本概念
   - `Chain`：链，用于将多个组件（提示模板、LLM模型、记忆、工具等）连接起来，形成可复用的`工作流`，完成复杂的任务
   - `Chain`的核心思想是通过组合不同的模块化单元，实现比单一组件更强大的功能。
2. 构建一个典型的链式服务主要包括如下4个部分
   - 将`LLM`与`Prompt Template`（提示模板）结合 
   - 将`LLM`与`外部数据`结合，例如用于问答
   - 将`LLM`与`长期记忆`结合，例如用于聊天历史记录
   - 通过将`第一个LLM`的输出作为`第二个LLM`的输入，将多个`LLM`按顺序结合在一起
3. `LCEL`（`LangChain Expression Languag`）：`LangChain`表达式语言是一种声明式方法，可以轻松地将多个组件链接成AI工作流。它通过`Python`原生操作符（如管道符`|`）将组件连接成可执行流程，显著简化了AI应用的开发
   - `LCEL`的基本构成：提示（`Prompt`）+ 模型（`Model`）+ 输出解析器（`OutputParser`）
   - 案例：
     ```python
     chain = prompt | model | output_parser
     chain.invoke({"input":"What's your name?"})
     ```
     - `Prompt`：`Prompt`是一个`BasePromptTemplate`，这意味着它接受一个模板变量的字典并生成一个` PromptValue`。`PromptValue`可以传递给`LLM`（它以字符串作为输入）或`ChatModel`（它以消息序列作为输入）
     - `Model`：将`PromptValue`传递给`model`。如果我们的`model`是一个`ChatModel`，这意味着它将输出一个`BaseMessage`
     - `OutputParser`：将`model`的输出传递给`output_parser`，它是一个`BaseOutputParser`，意味着它可以接受字符串或`BaseMessage`作为输入
     - `chain`：我们可以使用`|`运算符轻松创建这个`Chain`，`|`运算符在`LangChain`中用于将两个元素组合在一起。 
     - `invoke`：所有`LCEL`对象都实现`Runnable`协议，保证一致的调用方式（`invoke`/`batch`/`stream`）
   - 原理：`Runnable`是`LangChain`定义的一个抽象接口（`Protocol`），它`强制要求`所有`LCEL`组件实现一组标准方法：
     ```python
     class Runnable(Protocol):
         def invoke(self, input: Any) -> Any: ...        # 单输入单输出
         def batch(self, inputs: List[Any]) -> List[Any]: ...  # 批量处理
         def stream(self, input: Any) -> Iterator[Any]: ...    # 流式输出
         # 还有其他方法如 ainvoke（异步）等...
     ```
   - `Runnable`协议统一的好处：
     - 一致性：无论组件的功能多复杂（模型/提示词/工具），调用方式完全相同
     - 组合性：管道操作符 `|` 背后自动处理类型匹配和中间结果传递
   - 完整示例：
     ```python
     from dotenv import load_dotenv
     from langchain_core.output_parsers import StrOutputParser
     
     load_dotenv()
     chat_model = ChatOpenAI(model="gpt-4o-mini")
     prompt_template = PromptTemplate.from_template(
        template = "给我讲一个关于{topic}话题的简短笑话"
     )
     parser = StrOutputParser()

     # 构建链式调用（LCEL语法）
     chain = prompt_template | chat_model | parser
     out_put = chain.invoke({"topic": "ice cream"})
     print(out_put)
     print(type(out_put))
     ```

## 二、传统`Chain`的使用（驼峰式命名）（新版本已废弃）
1. `LLMChain`：这个链至少包括一个提示模板（`PromptTemplate`），一个语言模型（LLM或聊天模型）
   - 用于单次问答，输入一个`Prompt`，输出`LLM`的响应
   - 适合无上下文的简单任务（如翻译、摘要、分类等）
   - 无记忆：无法自动维护聊天历史
2. 使用主要步骤
   - 配置任务链：使用`LLMChain`类将任务与提示词结合，形成完整的任务链
     ```python
     chain = LLMChain(llm = llm, prompt = prompt_template)
     ```
   - 执行任务链：使用`invoke()`等方法执行任务链，并获取生成结果。可以根据需要对输出进行处理和展示
     ```python
     result = chain.invoke(...)
     print(result)
     ```
3. 样例
   ```python
   from langchain.chains.llm import LLMChain
   from langchain_core.prompts import PromptTemplate
   
   import os
   import dotenv
   from langchain_openai import ChatOpenAI
   
   dotenv.load_dotenv()
   
   os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY1")
   os.environ['OPENAI_BASE_URL'] = os.getenv("OPENAI_BASE_URL")
   
   # 1、创建大模型实例
   chat_model = ChatOpenAI(model="gpt-4o-mini")
   
   # 2、原始字符串模板
   template = "桌上有{number}个苹果，四个桃子和 3 本书，一共有几个水果?"
   prompt = PromptTemplate.from_template(template)
   
   # 3、创建LLMChain
   llm_chain = LLMChain(
       llm=chat_model,
       prompt=prompt
   )
   
   # 4、调用LLMChain，返回结果
   result = llm_chain.invoke({"number": 2})
   print(result)
   ```

## 三、基于`LCEL`构建的`Chains`的类型（小写 + 下划线命名方式）
1. `create_sql_query_chain`：`SQL`查询链，是创建生成`SQL`查询的链，用于将**自然语言转换成数据库的SQL查询**
   ```python
   from langchain_community.utilities import SQLDatabase
   from langchain_openai import ChatOpenAI
   
   # 创建大模型实例
   llm = ChatOpenAI(model="gpt-4o-mini")
   
   # 连接 MySQL 数据库
   db_user = "root"
   db_password = "abc123"  #根据自己的密码填写
   db_host = "127.0.0.1"
   db_port = "3306"
   db_name = "atguigudb"
   
   # mysql+pymysql://用户名:密码@ip地址:端口号/数据库名
   db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
   
   print("哪种数据库：", db.dialect)
   print("获取数据表：", db.get_usable_table_names())
   # 执行查询
   res = db.run("SELECT count(*) FROM employees;")
   print("查询结果：", res)
   ```
   ```python
   chain = create_sql_query_chain(llm=llm, db=db)
   # response = chain.invoke({"question": "数据表employees中哪个员工工资高？"})
   # print(response)
   # response = chain.invoke({"question": "查询departments表中一共有多少个部门？"})
   # print(response)
   # response = chain.invoke({"question": "查询last_name叫King的基本情况"})
   # print(response)
   # # 限制使用的表
   response = chain.invoke({"question": "一共有多少个员工？", "table_names_to_use": ["employees"]})
   print(response)
   ```
2. `create_stuff_documents_chain`用于将多个文档内容合并成单个长文本的链式工具，并一次性传递给`LLM`处理
   - 适合场景：适合需要全局理解所有文档内容的任务，主要是少量/中等长度文档的场景
   - 样例
     ```python
     from langchain.chains.combine_documents import create_stuff_documents_chain
     from langchain_core.prompts import PromptTemplate
     from langchain_openai import ChatOpenAI
     from langchain_core.documents import Document
     
     # 定义提示词模板
     prompt = PromptTemplate.from_template("""
        如下文档{docs}中说，香蕉是什么颜色的？
     """)
     
     # 创建链
     llm = ChatOpenAI(model="gpt-4o-mini")
     chain = create_stuff_documents_chain(llm, prompt, document_variable_name="docs")
     
     # 文档输入
     docs = [
         Document(
             page_content="苹果，学名Malus pumila Mill.，别称西洋苹果、柰，属于蔷薇科苹果属的植物。苹果是全球最广泛种植和销售的水果之一，具有悠久的栽培历史和广泛的分布范围。苹果的原始种群主要起源于中亚的天山山脉附近，尤其是现代哈萨克斯坦的阿拉木图地区，提供了所有现代苹果品种的基因库。苹果通过早期的贸易路线，如丝绸之路，从中亚向外扩散到全球各地。"
         ),
         Document(
             page_content="香蕉是白色的水果，主要产自热带地区。"
         ),
         Document(
             page_content="蓝莓是蓝色的浆果，含有抗氧化物质。"
         )
     ]
     # 执行摘要
     chain.invoke({"docs": docs})
     # 香蕉是黄色的水果，通常在成熟时呈现明亮的黄色。你提到的描述“白色的水果”可能是对香蕉未成熟状态的误解。在成熟阶段，它们大多数情况下是黄色的。'
     ```


------
参考资料：
1. 尚硅谷B站视频：https://www.bilibili.com/video/BV1ZppNzHEY4
2. LangChain数据相关工具：https://www.aidoczh.com/langchain/v0.2/docs/integrations/toolkits/sql_database/
