from browser_use import Agent, Browser, BrowserConfig
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import platform
import sys
load_dotenv()

async def execute_agent(prompt: str) -> str:
    # Determinar o caminho do executável do Chrome com base no sistema operacional
    chrome_path = None
    if platform.system() == "Windows":
        # Possíveis localizações do Chrome no Windows
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
    elif platform.system() == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif platform.system() == "Linux":
        # Possíveis localizações do Chrome no Linux
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
    
    if not chrome_path:
        print("ERRO: Não foi possível encontrar o executável do Chrome automaticamente.")
        chrome_path = input("Por favor, digite o caminho completo do Chrome: ")
        if not os.path.exists(chrome_path):
            raise Exception(f"O caminho fornecido não existe: {chrome_path}")
    
    print(f"Usando Chrome em: {chrome_path}")
    
    # Configurar o diretório de downloads
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # Configurar o Browser para usar uma instância existente do Chrome
    browser_config = BrowserConfig(
        headless=False,
        chrome_instance_path=chrome_path,
        extra_chromium_args=[
            f"--download.default_directory={download_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ],
        _force_keep_browser_alive=True  # Manter o navegador aberto após o script terminar
    )
    
    try:
        print("Iniciando o navegador...")
        browser = Browser(config=browser_config)
        
        print("Configurando o agente...")
        # Configurar e iniciar o agente
        agent = Agent(
            task=prompt,
            llm=ChatOpenAI(model="gpt-4o-mini"),
            browser=browser,
            generate_gif=False  # Desativar geração de GIF
        )
        
        print("Executando o agente...")
        # Executar o agente
        result = await agent.run()
        print("Agente concluiu a execução!")
        
        # Aguardar para manter o navegador aberto
        print("\nNavegador permanecerá aberto. Pressione Ctrl+C para encerrar ou digite 'exit' para sair.")
        
        while True:
            if sys.stdin in asyncio.get_event_loop()._ready:
                user_input = input()
                if user_input.lower() == 'exit':
                    break
            await asyncio.sleep(1)
            
        return str(result)
    
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        raise

# Executar o agente
if __name__ == "__main__":
    try:
        # Verificar se o Chrome está fechado antes de iniciar
        print("IMPORTANTE: Feche todas as janelas do Chrome antes de executar este script.")
        input("Pressione Enter quando o Chrome estiver completamente fechado...")
        
        asyncio.run(execute_agent("abra o google e pesquise por '2d consultores' e pegue o link do site, depois abra o site e pegue o telefone da empresa"))
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro fatal: {e}")