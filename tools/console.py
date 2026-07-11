import customtkinter as ctk
from tkinter.constants import END
from tools.shared import MSG_COLORS, configure_text_tags, safe_echo_eval

class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(master=self, text='Terminal')
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.console = ctk.CTkTextbox(master=self, corner_radius=0)

        # -- CONSOLE COLOR SCHEME --
        # Use global MSG_COLORS and configure tags on the textbox
        configure_text_tags(self.console, MSG_COLORS)
        self._write_console_message('Welcome to Yanagi Workbench\n', 'default')
        self._write_console_message('Created by Juri Han Padaria\n', 'default')
        self.console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='nsew')

        self.console_entry = ctk.CTkEntry(master=self, placeholder_text='Type your command here')
        self.console_entry.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.console_entry.bind('<Return>', command=self.send_cmd)


        # -- COMMAND MAPPING --
        self.commands = {'help': self.cmd_help,
                         'echo': self.cmd_echo,
                         'clear': self.cmd_clear,
                         'clearfilelog': self.cmd_clearfilelog,
                         'clearbackuplog': self.cmd_clearbackuplog}

    def _configure_console_tags(self): # kept for backward compatibility (no-op)
        # Tags are configured at initialization with `configure_text_tags`
        return

    def _write_console_message(self, text, level='default'):
        self.console.configure(state='normal')
        self.console.insert(END, text, level)
        self.console.configure(state='disabled')
        self.console.see(END)

    def send_cmd(self, event):
        user_cmd = self.console_entry.get()
        self.console_entry.delete(0, END)

        self._write_console_message(f'>>> {user_cmd}\n', 'default')

        parts = user_cmd.split()
        cmd = parts[0].lower()
        args = parts[1:]

        handler = self.commands.get(cmd, self.cmd_unknown)
        handler(args=args)

        return "break"

    def cmd_help(self, args):
        help_text = (
            "Available commands:\n"
            "help - Show this help message\n"
            "echo <text> - Echo the provided text\n"
            "clear - Clear the console\n"
            "clearfilelog - Clear the file log in the File Converter tab\n"
            "clearbackuplog - Clear the backup log in the Backup tab\n"
        )
        self._write_console_message(help_text, 'info')

    def cmd_echo(self, args):
        echo_text = ' '.join(args)

        # If there is an odd number of unescaped double quotes, treat it as invalid.
        if echo_text.count('"') % 2 == 1:
            self._write_console_message('Invalid string: unmatched quote\n', 'error')
            return

        try:
            result = safe_echo_eval(echo_text)
        except Exception:
            result = echo_text

        if isinstance(result, str):
            escaped = result.replace('"', '\\"')
            result = f'"{escaped}"'

        self._write_console_message(f'{result}\n', 'message')

    def cmd_clear(self, args):
        self.console.configure(state='normal')
        self.console.delete(1.0, END)
        self.console.configure(state='disabled')
        self._write_console_message('Console cleared.\n', 'success')

    def cmd_unknown(self, args):
        self._write_console_message("Unknown command. Type 'help' for a list of available commands.\n", 'error')

    def cmd_clearfilelog(self, args):
        self._write_console_message(level='info', text='Clearing file log...\n')
        file_log = self.master.file_operations_tab.file_converter_frame.files_log
        file_log.configure(state='normal')
        file_log.delete(1.0, END)
        file_log.configure(state='disabled')
        self._write_console_message(level='success', text='File log cleared.\n')

    def cmd_clearbackuplog(self, args):
        self._write_console_message(level='info', text='Clearing backup log...\n')
        backup_log = self.master.file_operations_tab.backup_frame.backup_log
        backup_log.configure(state='normal')
        backup_log.delete(1.0, END)
        backup_log.configure(state='disabled')
        self._write_console_message(level='success', text='Backup log cleared.\n')
