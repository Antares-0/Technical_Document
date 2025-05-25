# 引入提示词模版
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 引入OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    api_key="sk-YWadJFOooXNpA7PaukPXIZItf3iP4hbZ5dK52YoSveY6l3mE",
    base_url="https://ai.nengyongai.cn/v1"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是世界级的专家"),
    ("user", "{input}")
])

parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"input": "帮我简单介绍python，50字以内"})
print(result)

# content='Python是一种易学、强大的高级编程语言，广泛用于数据分析、人工智能、Web开发等领域。'
# additional_kwargs = {'refusal': None}
# response_metadata = {'token_usage': {'completion_tokens': 27, 'prompt_tokens': 26, 'total_tokens': 53, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-3.5-turbo-0125', 'system_fingerprint': 'fp_17d1f82c3e', 'id': 'chatcmpl-BaFiYxPAUNxlv6n6iicacalTCkR6V', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None} id='run--faab4876-4861-43fa-92da-a73713d8f398-0' usage_metadata={'input_tokens': 26, 'output_tokens': 27, 'total_tokens': 53, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}




