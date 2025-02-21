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

async def execute_agent(prompt: str) -> str:
    agent = Agent(
        task=prompt,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    return result

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
        result = asyncio.run(execute_agent(prompt))
        output_widget.after(0, lambda: update_output(output_widget, result, send_button, prompt, history_listbox))
    except Exception as e:
        output_widget.after(0, lambda: update_output(output_widget, f"Ocorreu um erro: {e}", send_button, prompt, history_listbox))

def on_send(prompt_widget, output_widget, send_button, history_listbox):
    prompt = prompt_widget.get(1.0, tk.END).strip()
    if prompt:
        send_button.config(state='disabled')
        output_widget.config(state='normal')
        output_widget.delete(1.0, tk.END)
        output_widget.insert(tk.END, "Processando...")
        output_widget.config(state='disabled')
        threading.Thread(target=run_agent_in_thread, args=(prompt, output_widget, send_button, history_listbox), daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Interface do Agent")
    root.geometry("800x600")
    
    frame_key = tk.Frame(root)
    frame_key.pack(pady=10)
    
    lbl_key = tk.Label(frame_key, text="Digite sua OpenAI API Key:")
    lbl_key.pack(side=tk.LEFT, padx=5)
    
    entry_key = tk.Entry(frame_key, width=50)
    entry_key.pack(side=tk.LEFT, padx=5)
    
    btn_save_key = tk.Button(frame_key, text="Salvar Key", command=lambda: save_openai_key(entry_key.get().strip()))
    btn_save_key.pack(side=tk.LEFT, padx=5)
    
    frame_prompt = tk.Frame(root)
    frame_prompt.pack(pady=10)
    
    lbl_prompt = tk.Label(frame_prompt, text="Digite o prompt abaixo:")
    lbl_prompt.pack(side=tk.TOP, pady=5)
    
    prompt_text = scrolledtext.ScrolledText(frame_prompt, width=80, height=10)
    prompt_text.pack(side=tk.LEFT, pady=5)
    
    # lbl_history = tk.Label(frame_prompt, text="Histórico de prompts:")
    # lbl_history.pack(side=tk.TOP, pady=5)
    
    # history_listbox = tk.Listbox(frame_prompt, width=30, height=10)
    # history_listbox.pack(side=tk.LEFT, pady=5)
    # history_listbox.bind('<<ListboxSelect>>', lambda event: load_selected_prompt(event, prompt_text, history_listbox))
    
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)
    
    btn_send = tk.Button(frame_buttons, text="Executar", command=lambda: on_send(prompt_text, result_text, btn_send))
    btn_send.pack(side=tk.LEFT, padx=5)
    
    btn_save = tk.Button(frame_buttons, text="Salvar", command=lambda: save_prompt_and_result(prompt_text.get(1.0, tk.END).strip(), result_text.get(1.0, tk.END).strip()))
    btn_save.pack(side=tk.LEFT, padx=5)
    
    lbl_result = tk.Label(root, text="Resultado:")
    lbl_result.pack(pady=10)
    
    result_text = scrolledtext.ScrolledText(root, width=80, height=10, state='disabled')
    result_text.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()