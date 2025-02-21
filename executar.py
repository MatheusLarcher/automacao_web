import asyncio
from playwright.async_api import async_playwright
from browser_use import AgentHistoryList, Agent  # Certifique-se de importar Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

async def execute_automation_from_result(result: AgentHistoryList):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False para visualização
        page = await browser.new_page()

        # Corrigido: chamar result.model_outputs() para obter a lista
        for model_output in result.model_outputs():  # Adicionado ()
            if "search_google" in model_output:
                query = model_output["search_google"]["query"]
                print(f"Pesquisando no Google: {query}")
                await page.goto(f"https://www.google.com/search?q={query}")
                await page.wait_for_load_state("domcontentloaded")

            elif "click_element" in model_output:
                element_info = model_output.get("interacted_element", {})
                xpath = element_info.get("xpath")
                href = element_info.get("attributes", {}).get("href")

                if xpath:
                    print(f"Clicando no elemento com XPath: {xpath}")
                    try:
                        await page.wait_for_selector(f"xpath={xpath}", timeout=10000)
                        await page.click(f"xpath={xpath}")
                        await page.wait_for_load_state("domcontentloaded")
                    except Exception as e:
                        print(f"Erro ao clicar pelo XPath: {e}")
                        if href:
                            print(f"Tentando acessar diretamente: {href}")
                            await page.goto(href)
                            await page.wait_for_load_state("domcontentloaded")
                elif href:
                    print(f"Acessando diretamente: {href}")
                    await page.goto(href)
                    await page.wait_for_load_state("domcontentloaded")
                else:
                    print("Nenhum XPath ou href disponível para clicar")

            elif "done" in model_output:
                result_text = model_output["done"]["text"]
                print(f"Resultado final: {result_text}")

        await browser.close()

async def main():
    agent = Agent(
        task="abra o google e pesquise por '2d consultores' e pegue o link do site, depois abra o site e pegue o telefone da empresa",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    await execute_automation_from_result(result)

if __name__ == "__main__":
    asyncio.run(main())