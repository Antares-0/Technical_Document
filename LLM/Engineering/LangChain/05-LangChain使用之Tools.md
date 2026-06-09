# 第05章：LangChain使用之Tools


***

## 1、Tools概述

### 1.1 介绍

要构建更强大的AI工程应用，只有生成文本这样的“`纸上谈兵`”能力自然是不够的。工具Tools不仅仅是“肢体”的延伸，更是为“大脑”插上了想象力的“翅膀”。借助工具，才能让AI应用的能力真正具备无限的可能，才能从“`认识世界`”走向“`改变世界`”。



Tools 用于扩展大语言模型（LLM）的能力，使其能够与外部系统、API 或自定义函数交互，从而完成仅靠文本生成无法实现的任务（如搜索、计算、数据库查询等）。

Tools 本质上是封装了特定功能的可调用模块，是Agent、Chain或LLM可以用来与世界互动的接口。

![image-20250530140905346](images/image-20250530140905346.png)

![image-20250619163714339](images/image-20250619163714339.png)

**特点：**

- `增强 LLM 的功能`：让 LLM 突破纯文本生成的限制，执行实际操作（如调用搜索引擎、查询数据库、运行代码等）
- `支持智能决策`：在Agent 工作流中，LLM 根据用户输入动态选择最合适的 Tool 完成任务。
- `模块化设计`：每个 Tool 专注一个功能，便于复用和组合（例如：搜索工具 + 计算工具 + 天气查询工具）



LangChain 拥有大量第三方工具。请访问工具集成查看可用工具列表。

[https://python.langchain.com/v0.2/docs/integrations/tools/](https://python.langchain.com/v0.2/docs/integrations/tools/)

### 1.2 Tool 的要素

**Tool 通常包含如下几个要素：**

- `name`：工具的名称
- `description`：工具的功能描述
- 该工具输入的`JSON模式`
- 要调用的函数
- `return_direct`：是否应将工具结果直接返回给用户（仅对Agent相关）

**实操步骤：**

- 步骤1：将name、description 和 JSON模式作为上下文提供给LLM
- 步骤2：LLM会根据提示词推断出`需要调用哪些工具`，并提供具体的调用参数信息
- 步骤3：用户需要根据返回的工具调用信息，自行触发相关工具的回调

> 注意：
>
> 如果工具具有`精心选择`的名称、描述和JSON模式，则模型的性能将更好。
>
> 下一章内容我们可以看到工具的调用动作可以通过Agent自主接管。



![img](images/bc62fa326ee4bac68bedc6ed7e4b8b6b.png)



## 2、自定义工具

### 2.1 两种自定义方式

**第1种：**使用[@tool装饰器](https://api.python.langchain.com/en/latest/tools/langchain_core.tools.tool.html#langchain_core.tools.tool)（自定义工具的最简单方式）

装饰器默认使用函数名称作为工具名称，但可以通过传递字符串作为第一个参数来覆盖此设置。

同时，装饰器将使用函数的`文档字符串`作为`工具的描述`，因此必须提供文档字符串。



**第2种：**使用StructuredTool.from_function类方法

这类似于`@tool`装饰器，但允许更多配置和同步/异步实现的规范。



### 2.2 几个常用属性

Tool由几个常用属性组成：

| 属性            | 类型               | 描述                                                         |
| --------------- | ------------------ | ------------------------------------------------------------ |
| `name`          | str                | `必选的`，在提供给LLM或Agent的工具集中必须是唯一的。         |
| `description`   | str                | `可选但建议`，描述工具的功能。LLM或Agent将使用此描述作为上下文，使用它确定工具的使用 |
| `args_schema`   | Pydantic BaseModel | `可选但建议`，可用于提供更多信息（例如，few-shot示例）或验证预期参数。 |
| `return_direct` | boolean            | 仅对Agent相关。当为True时，在调用给定工具后，Agent将停止并将结果直接返回给用户。 |

### 2.3 具体实现

#### 方式1：@tool 装饰器

举例1：

```python
from langchain.tools import tool

@tool
def add_number(a:int,b:int)->int:
    """两个整数相加"""
    return a + b


print(f"name = {add_number.name}")
print(f"args = {add_number.args}")
print(f"description = {add_number.description}")
print(f"return_direct = {add_number.return_direct}")

res = add_number.invoke({"a":10,"b":20})
print(res)
```

> name = add_number
> description = 两个整数相加
> args = {'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
> return_direct = False
> 30

说明：`return_direct参数`的默认值是False。当return_direct=False时，工具执行结果会返回给Agent，让Agent决定下一步操作；而return_direct=True则会中断这个循环，直接结束流程，返回结果给用户。

举例2：通过@tool的参数设置进行重置

```python
from langchain.tools import tool


@tool(name_or_callable="add_two_number",description="two number add",return_direct=True)
def add_number(a:int,b:int)->int:
    """两个整数相加"""
    return a + b


print(f"name = {add_number.name}")
print(f"description = {add_number.description}")
print(f"args = {add_number.args}")
print(f"return_direct = {add_number.return_direct}")

res = add_number.invoke({"a":10,"b":20})
print(res)
```

> name = add_two_number
> description = two number add
> args = {'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
> return_direct = True
> 30

补充：还可以修改参数的说明

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class FieldInfo(BaseModel):
    a :int = Field(description="第1个参数")
    b :int = Field(description="第2个参数")

@tool(name_or_callable="add_two_number",description="two number add",args_schema=FieldInfo,return_direct=True)
def add_number(a:int,b:int)->int:
    """两个整数相加"""
    return a + b


print(f"name = {add_number.name}")
print(f"description = {add_number.description}")
print(f"args = {add_number.args}")
print(f"return_direct = {add_number.return_direct}")

res = add_number.invoke({"a":10,"b":20})
print(res)
```

> name = add_two_number
> description = two number add
> args = {'a': {'description': '第1个参数', 'title': 'A', 'type': 'integer'}, 'b': {'description': '第2个参数', 'title': 'B', 'type': 'integer'}}
> return_direct = True
> 30



#### 方式2：StructuredTool的from_function()

`StructuredTool.from_function` 类方法提供了比`@tool`装饰器更多的可配置性，而无需太多额外的代码。

举例1：

```python
from langchain_core.tools import StructuredTool


def search_function(query: str):
    return "LangChain"


search = StructuredTool.from_function(
    func=search_function,
    name="Search1",
    description="useful for when you need to answer questions about current events"
)

print(search.name)
print(search.description)
print(search.args)

search.invoke("hello")
```

> Search1
> useful for when you need to answer questions about current events
> {'query': {'title': 'Query', 'type': 'string'}}
>
> 'LangChain'



### 2.4 工具调用举例

我们通过大模型分析用户需求，判断是否需要调用指定工具。

注意：这里需要将工具转换为函数，再将函数传入模型调用。

#### 步骤1：判断是否需要调用工具

```python
#1.导入相关依赖
from langchain_community.tools import MoveFileTool
from langchain_core.messages import HumanMessage
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI
import os
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY1")
os.environ['OPENAI_BASE_URL'] = os.getenv("OPENAI_BASE_URL")

# 2.定义LLM模型
model =ChatOpenAI(model="gpt-4o-mini",temperature=0)

# 3.定义工具
tools = [MoveFileTool()]

# 4.将工具转换为函数
functions = [convert_to_openai_function(t) for t in tools]

# print(functions[0])

# 4.模型使用函数
message = model.invoke(
    [HumanMessage(content="move file foo to bar")], 
    functions=functions
)

print(message)
```

> AIMessage(content='', `additional_kwargs={'function_call': {'arguments': '{"source_path":"foo","destination_path":"bar"}', 'name': 'move_file'}, 'refusal': None}`, response_metadata={'token_usage': {'completion_tokens': 21, 'prompt_tokens': 74, 'total_tokens': 95, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_57db37749c', 'id': 'chatcmpl-Bqwp5tcWiNKJeh23MtCmRGBiBhuZj', 'service_tier': None, 'finish_reason': 'function_call', 'logprobs': None}, id='run--c4b8631f-8224-41ee-a589-bc8bdadcaef9-0', usage_metadata={'input_tokens': 74, 'output_tokens': 21, 'total_tokens': 95, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})

模型绑定工具，调用模型，传入Message对象。

作为对照，修改代码：

```python
message = model.invoke(
    [HumanMessage(content="how is the weather in beijing")], 
    functions=functions
)
print(message)
```

> AIMessage(content="I don't have real-time weather data access. To get the current weather in Beijing, I recommend checking a reliable weather website or app for the most up-to-date information.", `additional_kwargs={'refusal': None}`, response_metadata={'token_usage': {'completion_tokens': 36, 'prompt_tokens': 76, 'total_tokens': 112, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_efad92c60b', 'id': 'chatcmpl-Bqws7xl0NGhArHJt1Qwaf1Fi4Br2K', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None}, id='run--8415e8a0-04aa-40b4-9fba-065e673e5384-0', usage_metadata={'input_tokens': 76, 'output_tokens': 36, 'total_tokens': 112, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})

#### 补充：返回值说明

**两种形式：**

**(1) 模型决定调用工具**

如果模型认为需要调用工具（如 `MoveFileTool`），返回的 `message` 会包含：

- **`content`**: 通常为空（因为模型选择调用工具，而非生成自然语言回复）。

- **`additional_kwargs`**: 包含工具调用的详细信息：

  ```python
  AIMessage(
      content='',  # 无自然语言回复
      additional_kwargs={
          'function_call': {
              'name': 'move_file',  # 工具名称
              'arguments': '{"source_path":"foo","destination_path":"bar"}'  # 工具参数
          }
      }
  )
  ```


**(2) 模型不调用工具**

如果模型认为无需调用工具（例如用户输入与工具无关），返回的 `message` 会是普通文本回复：

```python
AIMessage(
    content='我没有找到需要移动的文件。',  # 自然语言回复
    additional_kwargs={}  # 无工具调用
)
```



#### 步骤2：调用工具

```python
message = model.invoke(
    [HumanMessage(content="move file 'abc.txt' to 'C:\\Users\\shkst\\Desktop'")], 
    functions=functions
)
print(message)
```

> content='' additional_kwargs={'function_call': {'arguments': '{"source_path":"abc.txt","destination_path":"C:\\\\Users\\\\shkst\\\\Desktop\\\\abc.txt"}', 'name': 'move_file'}, 'refusal': None} response_metadata={'token_usage': {'completion_tokens': 32, 'prompt_tokens': 86, 'total_tokens': 118, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_efad92c60b', 'id': 'chatcmpl-C0VovYCSwz4rPSd6vFlOZ4iGdM6P3', 'service_tier': None, 'finish_reason': 'function_call', 'logprobs': None} id='run--f8191da7-6093-4ea0-ae28-17e703676392-0' usage_metadata={'input_tokens': 86, 'output_tokens': 32, 'total_tokens': 118, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}

**(1) 检查是否需要调用工具**

```python
import json

if "function_call" in message.additional_kwargs:
    tool_name = message.additional_kwargs["function_call"]["name"]
    tool_args = json.loads(message.additional_kwargs["function_call"]["arguments"])
    print(f"调用工具: {tool_name}, 参数: {tool_args}")
else:
    print("模型回复:", message.content)
```

> 调用工具: move_file, 参数: {'source_path': 'abc.txt', 'destination_path': 'C:\\Users\\shkst\\Desktop\\abc.txt'}

**(2) 实际执行工具调用**

```python
from langchain.tools import MoveFileTool

if "move_file" in message.additional_kwargs["function_call"]["name"]:
    tool = MoveFileTool()
    result = tool.run(tool_args)  # 执行工具
    print("工具执行结果:", result)
```

> 工具执行结果: File moved successfully from abc.txt to C:\Users\shkst\Desktop\abc.txt.





------
参考资料
1. 尚硅谷B站视频：https://www.bilibili.com/video/BV1ZppNzHEY4
2. 

