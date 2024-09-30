import tkinter as tk
from tkinter import scrolledtext, Menu, Listbox, Button, StringVar, OptionMenu, ttk
import json
import os
import re
import openai
import anthropic

class ChatBot:
    def __init__(self):
        self.system_message = "You are a friendly chatbot called BBot."
        self.conversation = []
        self.api_key = ""
        self.api_provider = ""
        self.model = ""
        self.create_history_directory()
        self.initialize_api_key_window()

    def create_history_directory(self):
        os.makedirs("history", exist_ok=True)

    def initialize_api_key_window(self):
        self.api_key_window = tk.Tk()
        self.api_key_window.title("API Key Input")

        self.api_provider_var = StringVar(value="OpenAI")
        self.model_var = StringVar(value="o1-mini")

        tk.Label(self.api_key_window, text="Enter your Anthropic/OpenAI API key:").pack()
        self.api_key_entry = tk.Entry(self.api_key_window)
        self.api_key_entry.pack()
        self.api_key_entry.focus_set()

        tk.Label(self.api_key_window, text="Select API Provider:").pack()
        self.api_provider_var.trace("w", self.update_model_options)
        OptionMenu(self.api_key_window, self.api_provider_var, "Anthropic", "OpenAI").pack()

        tk.Label(self.api_key_window, text="Select Model:").pack()
        self.model_option_menu = OptionMenu(self.api_key_window, self.model_var, "o1-mini")
        self.model_option_menu.pack()

        Button(self.api_key_window, text="Set API Key and Model", command=self.set_api_key_and_model).pack()

        self.api_key_entry.bind('<Return>', lambda event: self.set_api_key_and_model())

        self.api_key_window.mainloop()

    def update_model_options(self, *args):
        selected_provider = self.api_provider_var.get()
        self.model_option_menu['menu'].delete(0, 'end')

        models = {
            "Anthropic": ["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"],
            "OpenAI": ["o1-mini", "gpt-4o-mini"]
        }

        for model in models.get(selected_provider, []):
            self.model_option_menu['menu'].add_command(label=model, command=tk._setit(self.model_var, model))
        
        self.model_var.set(models[selected_provider][0])

    def set_api_key_and_model(self):
        self.api_key = self.api_key_entry.get()
        self.api_provider = self.api_provider_var.get()
        self.model = self.model_var.get()

        if self.api_provider == "OpenAI":
            openai.api_key = self.api_key
        elif self.api_provider == "Anthropic":
            self.anthropic_client = anthropic.Client(api_key=self.api_key)

        self.api_key_window.destroy()
        self.initialize_chat_window()

    def send_message(self):
        user_message = self.user_input.get("1.0", tk.END).strip()
        self.user_input.delete("1.0", tk.END)

        if not self.conversation:
            self.conversation.append({"role": "system", "content": self.system_message})

        self.conversation.append({"role": "user", "content": user_message})

        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"You: {user_message}\n", "user")
        self.chat_log.config(state=tk.DISABLED)

        self.get_ai_response(user_message)

    def get_ai_response(self, user_message):
        try:
            if self.api_provider == "OpenAI":
                completion = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.conversation
                )
                ai_response = completion['choices'][0]['message']['content']
            elif self.api_provider == "Anthropic":
                messages = [{"role": "user", "content": user_message}]
                completion = self.anthropic_client.messages.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=100
                )
                ai_response = completion.content[0].text if completion.content else "No response from AI."

            self.conversation.append({"role": "assistant", "content": ai_response})
            self.update_chat_log()
        except Exception as e:
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.insert(tk.END, f"Error: {str(e)}\n", "error")
            self.chat_log.config(state=tk.DISABLED)

    def update_chat_log(self):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete(1.0, tk.END)
        for message in self.conversation:
            self.chat_log.insert(tk.END, f"{message['role'].capitalize()}: {message['content']}\n", message['role'])
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(tk.END)

    def regenerate_response(self):
        if len(self.conversation) >= 2:
            last_user_message = next((msg for msg in reversed(self.conversation) if msg['role'] == 'user'), None)
            if last_user_message:
                self.conversation = self.conversation[:-2]  # Remove the last user message and AI response
                self.update_chat_log()
                self.get_ai_response(last_user_message['content'])

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[^\w\s-]', '', filename).replace(' ', '_').replace('\n', '')[:20]

    def save_conversation(self):
        if not self.conversation:
            return

        user_message = self.conversation[1]["content"]
        sanitized_user_message = self.sanitize_filename(user_message)
        file_path = os.path.join("history", sanitized_user_message)

        counter = 1
        while os.path.exists(file_path + ".json"):
            file_path = os.path.join("history", f"{sanitized_user_message}_{counter}")
            counter += 1

        with open(file_path + ".json", 'w') as f:
            json.dump(self.conversation, f, indent=2)
        
        self.update_file_listbox()

    def load_conversation_from_file(self, filename):
        with open(os.path.join("history", filename), 'r') as f:
            self.conversation = json.load(f)
        self.update_chat_log()

    def delete_json_file(self):
        selected = self.file_listbox.curselection()
        if selected:
            filename = self.file_listbox.get(selected)
            os.remove(os.path.join("history", filename))
            self.update_file_listbox()

    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for filename in os.listdir("history"):
            if filename.endswith('.json'):
                self.file_listbox.insert(tk.END, filename)

    def on_file_select(self, event):
        selected_file_index = self.file_listbox.curselection()
        if selected_file_index:
            selected_file = self.file_listbox.get(selected_file_index)
            self.load_conversation_from_file(selected_file)

    def start_new_chat(self):
        # Save the current conversation if any
        self.save_conversation()

        # Clear the conversation and chat log
        self.conversation = []
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete(1.0, tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def show_message_pane_context_menu(self, event):
        self.message_context_menu.post(event.x_root, event.y_root)

    def show_chat_log_context_menu(self, event):
        self.chat_log_context_menu.post(event.x_root, event.y_root)

    def initialize_chat_window(self):
        self.chat_window = tk.Tk()
        self.chat_window.title("BBot Chat")
        self.chat_window.geometry("1200x800")

        # Main paned window
        main_paned = ttk.PanedWindow(self.chat_window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=1)

        # Left frame (history)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Right paned window
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=3)

        # History pane
        history_frame = ttk.Frame(left_frame)
        history_frame.pack(fill=tk.BOTH, expand=1)

        self.file_listbox = Listbox(history_frame)
        self.file_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(history_buttons_frame, text="Load", command=lambda: self.on_file_select(None)).pack(side=tk.LEFT, fill=tk.X, expand=1)
        ttk.Button(history_buttons_frame, text="Save", command=self.save_conversation).pack(side=tk.LEFT, fill=tk.X, expand=1)
        ttk.Button(history_buttons_frame, text="Delete", command=self.delete_json_file).pack(side=tk.LEFT, fill=tk.X, expand=1)

        # Chat log pane
        chat_frame = ttk.Frame(right_paned)
        right_paned.add(chat_frame, weight=3)

        self.chat_log = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_log.pack(fill=tk.BOTH, expand=1)

        # Add right-click context menu for chat log
        self.chat_log_context_menu = Menu(self.chat_window, tearoff=0)
        self.chat_log_context_menu.add_command(label="Select All", command=lambda: self.chat_log.tag_add('sel', '1.0', 'end'))
        self.chat_log_context_menu.add_command(label="Copy", command=lambda: self.chat_log.event_generate("<<Copy>>"))
        self.chat_log.bind("<Button-3>", self.show_chat_log_context_menu)

        # User input pane
        input_frame = ttk.Frame(right_paned)
        right_paned.add(input_frame, weight=1)

        # Simple tk.Text widget for message input
        self.user_input = tk.Text(input_frame, wrap=tk.WORD, height=5)
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(button_frame, text="Send", command=self.send_message).pack(fill=tk.X)
        ttk.Button(button_frame, text="Regenerate", command=self.regenerate_response).pack(fill=tk.X)
        ttk.Button(button_frame, text="New", command=self.start_new_chat).pack(fill=tk.X)  # New Chat button

        self.update_file_listbox()

        self.chat_window.mainloop()

if __name__ == "__main__":
    ChatBot()
