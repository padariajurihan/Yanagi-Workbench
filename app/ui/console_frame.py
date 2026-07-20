import customtkinter as ctk
from tkinter.constants import END

from app.tools.console import ConsoleLogic
from app.shared.shared import MSG_COLORS, configure_text_tags


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(master=self, text='Terminal')
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.console = ctk.CTkTextbox(master=self, corner_radius=0)
        configure_text_tags(self.console, MSG_COLORS)
        self._write_console_message('Welcome to Yanagi Workbench\n', 'default')
        self._write_console_message('Created by Juri Han Padaria\n', 'default')
        self.console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='nsew')

        self.console_entry = ctk.CTkEntry(master=self, placeholder_text='Type your command here')
        self.console_entry.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.console_entry.bind('<Return>', self._on_enter)

        self.logic = ConsoleLogic(self)

    def _on_enter(self, event):
        self.logic.handle_command(self.console_entry.get())
        return 'break'

    def _write_console_message(self, text, level='default'):
        self.console.configure(state='normal')
        self.console.insert(END, text, level)
        self.console.configure(state='disabled')
        self.console.see(END)
