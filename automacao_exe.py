import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
import os
import sys
import platform
from pathlib import Path
from datetime import datetime

def caminho_executavel():
    if getattr(sys, 'frozen', False):
        caminho_base = os.path.dirname(sys.executable)
    else:
        caminho_base = os.path.dirname(os.path.abspath(__file__))
    return caminho_base

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(base_path, "ms-playwright")

caminho_base = caminho_executavel()
env_path = os.path.join(caminho_base, '.env')
load_dotenv(env_path)

def save_openai_key(key: str):
    try:
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={key}\n")
        os.environ["OPENAI_API_KEY"] = key
        messagebox.showinfo("Sucesso", "OpenAI API Key salva com sucesso!")
        load_dotenv(env_path)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar a chave: {e}")

def get_chrome_path():
    """Obtém o caminho do executável do Chrome com base no sistema operacional"""
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
    
    return chrome_path

async def execute_agent(prompt: str) -> str:
    # Obter caminho do Chrome
    chrome_path = get_chrome_path()
    if not chrome_path:
        return "ERRO: Não foi possível encontrar o Chrome automaticamente. Verifique se o Chrome está instalado."
    
    # Configurar diretório de downloads
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # Configurar Browser para usar instância existente do Chrome
    browser_config = BrowserConfig(
        headless=False,
        chrome_instance_path=chrome_path,
        extra_chromium_args=[
            f"--download.default_directory={download_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ],
        _force_keep_browser_alive=True  # Manter navegador aberto após terminar
    )
    
    try:
        # Iniciar navegador
        browser = Browser(config=browser_config)
        
        # Criar e executar agente
        agent = Agent(
            task=prompt,
            llm=ChatOpenAI(model="gpt-4o-mini"),
            browser=browser,
            generate_gif=False  # Desativar geração de GIF
        )
        
        # Executar agente e retornar resultado
        result = await agent.run()
        return str(result)
    except Exception as e:
        return f"Erro durante a execução: {str(e)}"

prompt_history = []

def save_prompt_and_result(prompt, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prompt_result_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write("Prompt:\n")
        f.write(prompt + "\n\n")
        f.write("Resultado:\n")
        f.write(result + "\n")
    messagebox.showinfo("Salvo", f"Prompt e resultado salvos em {filename}")

def add_to_history(prompt, history_listbox):
    if prompt not in prompt_history:
        prompt_history.append(prompt)
        history_listbox.insert(tk.END, prompt)

def load_selected_prompt(event, prompt_text, history_listbox):
    selection = history_listbox.curselection()
    if selection:
        index = selection[0]
        selected_prompt = history_listbox.get(index)
        prompt_text.delete(1.0, tk.END)
        prompt_text.insert(tk.END, selected_prompt)

def update_output(text_widget, text, button, prompt, history_listbox):
    text_widget.config(state='normal')
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, text)
    text_widget.config(state='disabled')
    button.config(state='normal')
    add_to_history(prompt, history_listbox)

def run_agent_in_thread(prompt, output_widget, send_button, history_listbox):
    try:
        # Aviso sobre fechamento do Chrome
        output_widget.config(state='normal')
        output_widget.delete(1.0, tk.END)
        output_widget.insert(tk.END, "Processando... IMPORTANTE: Feche todas as janelas do Chrome antes de continuar.")
        output_widget.config(state='disabled')
        
        result = asyncio.run(execute_agent(prompt))
        output_widget.after(0, lambda: update_output(output_widget, result, send_button, prompt, history_listbox))
    except Exception as e:
        output_widget.after(0, lambda: update_output(output_widget, f"Ocorreu um erro: {e}", send_button, prompt, history_listbox))

def on_send(prompt_widget, output_widget, send_button, history_listbox):
    prompt = prompt_widget.get(1.0, tk.END).strip()
    if prompt:
        # Mostrar aviso sobre Chrome
        result = messagebox.askokcancel("Aviso", "Antes de continuar, feche todas as janelas do Chrome. Deseja prosseguir?")
        if not result:
            return
            
        send_button.config(state='disabled')
        output_widget.config(state='normal')
        output_widget.delete(1.0, tk.END)
        output_widget.insert(tk.END, "Processando... Iniciando o Chrome...")
        output_widget.config(state='disabled')
        threading.Thread(target=run_agent_in_thread, args=(prompt, output_widget, send_button, history_listbox), daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Interface do Agent - Navegador Normal")
    root.geometry("800x600")
    
    frame_key = tk.Frame(root)
    frame_key.pack(pady=10)
    
    lbl_key = tk.Label(frame_key, text="Digite sua OpenAI API Key:")
    lbl_key.pack(side=tk.LEFT, padx=5)
    
    entry_key = tk.Entry(frame_key, width=50)
    entry_key.pack(side=tk.LEFT, padx=5)
    
    btn_save_key = tk.Button(frame_key, text="Salvar Key", command=lambda: save_openai_key(entry_key.get().strip()))
    btn_save_key.pack(side=tk.LEFT, padx=5)
    
    # Verificar caminho do Chrome
    chrome_path = get_chrome_path()
    if chrome_path:
        lbl_chrome_status = tk.Label(root, text=f"Chrome detectado em: {chrome_path}", fg="green")
    else:
        lbl_chrome_status = tk.Label(root, text="Chrome não encontrado! Instale o Chrome para usar este aplicativo.", fg="red")
    lbl_chrome_status.pack(pady=5)
    
    frame_prompt = tk.Frame(root)
    frame_prompt.pack(pady=10)
    
    lbl_prompt = tk.Label(frame_prompt, text="Digite o prompt abaixo:")
    lbl_prompt.pack(side=tk.TOP, pady=5)
    
    prompt_text = scrolledtext.ScrolledText(frame_prompt, width=80, height=10)
    prompt_text.pack(side=tk.LEFT, pady=5)
    
    lbl_history = tk.Label(frame_prompt, text="Histórico de prompts:")
    lbl_history.pack(side=tk.TOP, pady=5)
    
    history_listbox = tk.Listbox(frame_prompt, width=30, height=10)
    history_listbox.pack(side=tk.LEFT, pady=5)
    history_listbox.bind('<<ListboxSelect>>', lambda event: load_selected_prompt(event, prompt_text, history_listbox))
    
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)
    
    btn_send = tk.Button(
        frame_buttons,
        text="Executar",
        command=lambda: on_send(prompt_text, result_text, btn_send, history_listbox)
    )
    btn_send.pack(side=tk.LEFT, padx=5)
    
    btn_save = tk.Button(frame_buttons, text="Salvar", command=lambda: save_prompt_and_result(prompt_text.get(1.0, tk.END).strip(), result_text.get(1.0, tk.END).strip()))
    btn_save.pack(side=tk.LEFT, padx=5)
    
    lbl_result = tk.Label(root, text="Resultado:")
    lbl_result.pack(pady=10)
    
    result_text = scrolledtext.ScrolledText(root, width=80, height=10, state='disabled')
    result_text.pack(pady=5)
    
    # Adicionar aviso sobre uso do Chrome
    lbl_warning = tk.Label(root, text="NOTA: Este aplicativo abrirá o Chrome em modo regular. Feche todas as janelas do Chrome antes de executar.", fg="blue")
    lbl_warning.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()