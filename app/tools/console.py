import ast
from tkinter.constants import END

from app.tools.shared import safe_echo_eval


class ConsoleLogic:
    def __init__(self, master):
        self.master = master
        self.commands = {
            'help': self.cmd_help,
            'echo': self.cmd_echo,
            'clear': self.cmd_clear,
        }

    def handle_command(self, user_cmd: str):
        if not user_cmd.strip():
            return

        self.master.console_entry.delete(0, END)
        self._write_console_message(f'>>> {user_cmd}\n', 'default')

        parts = user_cmd.split()
        cmd = parts[0].lower()
        args = parts[1:]

        handler = self.commands.get(cmd, self.cmd_unknown)
        handler(args=args)

    def _write_console_message(self, text, level='default'):
        self.master._write_console_message(text, level)

    def cmd_help(self, args):
        help_text = (
            'Available commands:\n'
            'help - Show this help message\n'
            'echo <text> - Echo the provided text\n'
            'clear - Clear the console\n'
        )
        self._write_console_message(help_text, 'info')

    def cmd_echo(self, args):
        echo_text = ' '.join(args)

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
        self.master.console.configure(state='normal')
        self.master.console.delete(1.0, END)
        self.master.console.configure(state='disabled')
        self._write_console_message('Console cleared.\n', 'success')

    def cmd_unknown(self, args):
        self._write_console_message("Unknown command. Type 'help' for a list of available commands.\n", 'error')

    def cmd_unknown(self, args):
        self._write_console_message("Unknown command. Type 'help' for a list of available commands.\n", 'error')
