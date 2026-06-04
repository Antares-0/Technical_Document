# astream_chain.py
import asyncio
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="sk-YWadJFOooXNpA7PaukPXIZItf3iP4hbZ5dK52YoSveY6l3mE",
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
