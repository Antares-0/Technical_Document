#astream_event.py
import asyncio

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="sk-YWadJFOooXNpA7PaukPXIZItf3iP4hbZ5dK52YoSveY6l3mE",
    base_url="https://ai.nengyongai.cn/v1",
)



async def async_stream():
    events = []
    async for event in llm.astream_events("hello", version="v2"):
        events.append(event)
    print(events)

asyncio.run(async_stream())

# 输出：
# [
# {'event': 'on_chat_model_start', 'data': {'input': 'hello'}, 'name': 'ChatOpenAI', 'tags': [], 'run_id': 'd797b939-1b31-42bd-a9d3-1400a6d817b0', 'metadata': {'ls_provider': 'openai', 'ls_model_name': 'gpt-3.5-turbo', 'ls_model_type': 'chat', 'ls_temperature': None}, 'parent_ids': []},
# {'event': 'on_chat_model_stream', 'run_id': 'd797b939-1b31-42bd-a9d3-1400a6d817b0', 'name': 'ChatOpenAI', 'tags': [], 'metadata': {'ls_provider': 'openai', 'ls_model_name': 'gpt-3.5-turbo', 'ls_model_type': 'chat', 'ls_temperature': None}, 'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={}, id='run--d797b939-1b31-42bd-a9d3-1400a6d817b0')}, 'parent_ids': []},
# {'event': 'on_chat_model_stream', 'run_id': 'd797b939-1b31-42bd-a9d3-1400a6d817b0', 'name': 'ChatOpenAI', 'tags': [], 'metadata': {'ls_provider': 'openai', 'ls_model_name': 'gpt-3.5-turbo', 'ls_model_type': 'chat', 'ls_temperature': None}, 'data': {'chunk': AIMessageChunk(content='Hello, how may I assist you?', additional_kwargs={}, response_metadata={}, id='run--d797b939-1b31-42bd-a9d3-1400a6d817b0')}, 'parent_ids': []},
# {'event': 'on_chat_model_stream', 'run_id': 'd797b939-1b31-42bd-a9d3-1400a6d817b0', 'name': 'ChatOpenAI', 'tags': [], 'metadata': {'ls_provider': 'openai', 'ls_model_name': 'gpt-3.5-turbo', 'ls_model_type': 'chat', 'ls_temperature': None}, 'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'gpt-3.5-turbo-0125'}, id='run--d797b939-1b31-42bd-a9d3-1400a6d817b0')}, 'parent_ids': []},
# {'event': 'on_chat_model_end', 'data': {'output': AIMessageChunk(content='Hello, how may I assist you?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'gpt-3.5-turbo-0125'}, id='run--d797b939-1b31-42bd-a9d3-1400a6d817b0')}, 'run_id': 'd797b939-1b31-42bd-a9d3-1400a6d817b0', 'name': 'ChatOpenAI', 'tags': [], 'metadata': {'ls_provider': 'openai', 'ls_model_name': 'gpt-3.5-turbo', 'ls_model_type': 'chat', 'ls_temperature': None}, 'parent_ids': []}
# ]