from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()



async def main():
    agent = Agent(
        task=" abra o google e pesquise por '2d consultores' e pegue o link do site, depois abra o site e pegue o telefone da empresa",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    print(result)

asyncio.run(main())