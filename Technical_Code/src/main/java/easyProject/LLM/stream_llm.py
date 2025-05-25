from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="sk-YWadJFOooXNpA7PaukPXIZItf3iP4hbZ5dK52YoSveY6l3mE",
    base_url="https://ai.nengyongai.cn/v1",
    model="gpt-4",
)

chunks=[]

for chunk in llm.stream("天空是什么颜色？"):
    chunks.append(chunk)
    print(chunk.content, end="|", flush=True)


