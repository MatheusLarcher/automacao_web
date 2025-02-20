import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

def caminho_executavel():
    if getattr(sys, 'frozen', False):
        # Caminho quando executado como .exe (por exemplo, via PyInstaller)
        caminho_base = os.path.dirname(sys.executable)
    else:
        # Caminho quando executado como script .py
        caminho_base = os.path.dirname(os.path.abspath(__file__))
    return caminho_base


# Define o caminho base e carrega o .env, se existir
caminho_base = caminho_executavel()
env_path = os.path.join(caminho_base, '.env')
load_dotenv(env_path)

def save_openai_key(key: str):
    """
    Salva a OpenAI API Key no arquivo .env e atualiza a variável de ambiente.
    """
    try:
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={key}\n")
        os.environ["OPENAI_API_KEY"] = key
        messagebox.showinfo("Sucesso", "OpenAI API Key salva com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar a chave: {e}")

async def execute_agent(prompt: str) -> str:
    """
    Função assíncrona que cria o agente com o prompt informado e retorna o resultado.
    """
    agent = Agent(
        task=prompt,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    return result

def update_output(text_widget, text, button):
    """
    Atualiza a área de resultado e reabilita o botão.
    """
    text_widget.config(state='normal')
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, text)
    text_widget.config(state='disabled')
    button.config(state='normal')

def run_agent_in_thread(prompt, output_widget, send_button):
    """
    Executa a função assíncrona em uma thread separada para não travar a interface.
    """
    try:
        result = asyncio.run(execute_agent(prompt))
        output_widget.after(0, lambda: update_output(output_widget, result, send_button))
    except Exception as e:
        output_widget.after(0, lambda: update_output(output_widget, f"Ocorreu um erro: {e}", send_button))

def on_send(prompt_widget, output_widget, send_button):
    """
    Lê o prompt, exibe "Processando..." e dispara a execução do agente em uma thread.
    """
    prompt = prompt_widget.get(1.0, tk.END).strip()
    if prompt:
        send_button.config(state='disabled')
        output_widget.config(state='normal')
        output_widget.delete(1.0, tk.END)
        output_widget.insert(tk.END, "Processando...")
        output_widget.config(state='disabled')
        threading.Thread(target=run_agent_in_thread, args=(prompt, output_widget, send_button), daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Interface do Agent")
    root.geometry("800x600")
    
    # Frame para a OpenAI API Key
    frame_key = tk.Frame(root)
    frame_key.pack(pady=10)
    
    lbl_key = tk.Label(frame_key, text="Digite sua OpenAI API Key:")
    lbl_key.pack(side=tk.LEFT, padx=5)
    
    entry_key = tk.Entry(frame_key, width=50)
    entry_key.pack(side=tk.LEFT, padx=5)
    
    btn_save_key = tk.Button(frame_key, text="Salvar Key", command=lambda: save_openai_key(entry_key.get().strip()))
    btn_save_key.pack(side=tk.LEFT, padx=5)
    
    # Área para digitar o prompt
    lbl_prompt = tk.Label(root, text="Digite o prompt abaixo:")
    lbl_prompt.pack(pady=10)
    
    prompt_text = scrolledtext.ScrolledText(root, width=80, height=10)
    prompt_text.pack(pady=5)
    
    btn_send = tk.Button(root, text="Executar", command=lambda: on_send(prompt_text, result_text, btn_send))
    btn_send.pack(pady=10)
    
    lbl_result = tk.Label(root, text="Resultado:")
    lbl_result.pack(pady=10)
    
    result_text = scrolledtext.ScrolledText(root, width=80, height=10, state='disabled')
    result_text.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
