import threading
import customtkinter as ctk
import pillow_heif
try:
    pillow_heif.register_heif_opener()
except Exception:
    # If registration fails, PIL may still handle formats if system libs are present.
    pass
from PIL import Image
import tkinter.filedialog as fd
from tkinter.constants import *
import ast
from pathlib import Path
from datetime import datetime
import shutil
import os

# Global color map for console and logs — reuse across the project
MSG_COLORS = {
    'info': '#2374AB',    # Rich Cerulean
    'error': '#D90429',   # Flag Red
    'success': '#0CCA4A', # Jade Green
    'message': '#9CFFD9', # Aquamarine
    'default': '#EDF2F4'  # Platinum
}


def configure_text_tags(text_widget, colors: dict):
    """Configure text tags (colors) on a Text/CTkTextbox widget.

    This allows reusing the same tag names/colors across multiple widgets.
    """
    for name, color in colors.items():
        # CTkTextbox uses tag_config
        try:
            text_widget.tag_config(name, foreground=color)
        except Exception:
            # Fallback: ignore if the widget doesn't support tags
            pass


def safe_echo_eval(expression: str):
    expression = expression.strip()
    if not expression:
        return ''

    # First try to evaluate quoted string literals like "Olá, isso é uma mensagem"
    try:
        value = ast.literal_eval(expression)
        return value
    except Exception:
        pass

    # Then allow safe arithmetic expressions only
    node = ast.parse(expression, mode='eval')
    for sub in ast.walk(node):
        if not isinstance(sub, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                ast.Pow, ast.FloorDiv, ast.USub, ast.UAdd,
                                ast.Tuple, ast.List, ast.Dict, ast.Set,
                                ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt,
                                ast.GtE, ast.Subscript, ast.Slice)):
            raise ValueError(f'Unsupported expression: {sub.__class__.__name__}')
        if isinstance(sub, ast.Name):
            raise ValueError('Name expressions are not allowed')
        if isinstance(sub, ast.Call):
            raise ValueError('Function calls are not allowed')

    return eval(compile(node, '<string>', 'eval'), {'__builtins__': None}, {})


class FileOperationsTab(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.add('File Converter')
        self.add('Backup')

        # Configure the 'File Converter' tab to expand
        file_converter_tab = self.tab('File Converter')
        file_converter_tab.grid_rowconfigure(0, weight=1)
        file_converter_tab.grid_columnconfigure(0, weight=1)

        self.file_converter_frame = FileManagementFrame(file_converter_tab)
        self.file_converter_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # Configure the 'Backup' tab to expand
        backup_tab = self.tab('Backup')
        backup_tab.grid_rowconfigure(0, weight=1)
        backup_tab.grid_columnconfigure(0, weight=1)

        self.backup_frame = BackupFrame(backup_tab)
        self.backup_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


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



# -- FILE MANAGEMENT FRAME --
class FileManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.selected_files = []
        self.output_dir = None
        self.output_dir_var = ctk.StringVar(value='')
        self.format_var = ctk.StringVar(value='JPEG')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(master=self, text='File log')
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.files_log = ctk.CTkTextbox(master=self, corner_radius=0)
        self.files_log.configure(state='disabled')
        self.files_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='nsew')

        self.button_frame = ctk.CTkFrame(master=self)
        self.button_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky='ew')
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.send_files_btn = ctk.CTkButton(master=self.button_frame, text='Select your files here')
        self.send_files_btn.grid(row=0, column=0, sticky='ew')
        self.send_files_btn.bind('<Button-1>', command=self.open_file)

        self.convert_btn = ctk.CTkButton(master=self.button_frame, text='Convert', state='disabled', command=self.convert_files)
        self.convert_btn.grid(row=0, column=1, padx=(10, 0), sticky='ew')

        self.output_frame = ctk.CTkFrame(master=self)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(1, weight=0)

        self.output_dir_entry = ctk.CTkEntry(master=self.output_frame, textvariable=self.output_dir_var, placeholder_text='Output directory', state='disabled')
        self.output_dir_entry.grid(row=0, column=0, sticky='ew')

        self.select_output_dir_btn = ctk.CTkButton(master=self.output_frame, text='Select Path', command=self.select_output_path)
        self.select_output_dir_btn.grid(row=0, column=1, padx=(10, 0), sticky='ew')
        self.output_frame.grid_remove()

        self.conversion_progress = ctk.CTkProgressBar(master=self)
        self.conversion_progress.set(0.0)
        self.conversion_progress.grid(row=4, column=0, padx=10, pady=(0, 10), sticky='ew')

        # File format frame
        self.desired_format_frame = ctk.CTkFrame(master=self)
        self.desired_format_frame.grid_columnconfigure(0, weight=1)
        self.desired_format_frame.grid_columnconfigure(1, weight=1)

        self.format_label = ctk.CTkLabel(master=self.desired_format_frame, text='Desired format:')
        self.format_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.jpeg_radio = ctk.CTkRadioButton(master=self.desired_format_frame, variable=self.format_var, value='JPEG', text='JPEG')
        self.jpeg_radio.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.png_radio = ctk.CTkRadioButton(master=self.desired_format_frame, variable=self.format_var, value='PNG', text='PNG')
        self.png_radio.grid(row=1, column=1, padx=10, pady=(0, 10), sticky='w')

    def open_file(self, event):
        files = fd.askopenfilenames(title='Select your images here', 
                                    filetypes=[('All files', '*.*'),
                                               ('JPEG', '*.jpg *.jpeg'),
                                               ('PNG', '*.png'),
                                               ('HEIF/HEIC', '*.heif *.heic'),
                                               ('WebP', '*.webp')])

        # Put all the files into a list
        self.selected_files = list(files)

        # If there is one file or more
        if len(self.selected_files) > 0:
            shown = 0

            for file in self.selected_files:
                if shown < 5:
                    name = Path(file).name
                    self.files_log.configure(state='normal')
                    self.files_log.insert(END, f'File {name} has been added.\n')
                    self.files_log.configure(state='disabled')

                shown += 1

            remaining = max(0, len(self.selected_files) - 5)
            self.files_log.configure(state='normal')
            if remaining > 0:
                self.files_log.insert(END, f'... and more {remaining} file(s).\n')
            self.files_log.insert(END, f'Total files added: {len(self.selected_files)}\n')
            self.files_log.configure(state='disabled')

            self.desired_format_frame.grid(row=5, column=0, padx=10, pady=(0, 10), sticky='ew')
            self.output_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
            self._update_convert_button_state()

    def select_output_path(self):
        path = fd.askdirectory(title='Select output folder')
        if path:
            self.output_dir = path
            self.output_dir_var.set(path)
            self._update_convert_button_state()

    def _update_convert_button_state(self):
        if self.selected_files and self.output_dir:
            self.convert_btn.configure(state='normal')
        else:
            self.convert_btn.configure(state='disabled')

    def convert_files(self):
        self.convert_btn.configure(state='disabled')
        self.send_files_btn.configure(state='disabled')
        self.conversion_progress.set(0.0)
        self._log_message(f'Conversion started to {self.format_var.get()}.\n')

        thread = threading.Thread(target=self._convert_files_thread, daemon=True)
        thread.start()

    def _convert_files_thread(self):
        selected_format = self.format_var.get()
        total = len(self.selected_files)
        converted = 0

        for file_path in self.selected_files:
            try:
                output_path = self._get_output_path(file_path, selected_format)
                with Image.open(file_path) as image:
                    if selected_format == 'JPEG':
                        if image.mode in ('RGBA', 'LA', 'P'):
                            image = image.convert('RGB')
                        image.save(output_path, format='JPEG', quality=95)
                    else:
                        image.save(output_path, format='PNG')

                converted += 1
                progress = converted / total
                message = f'Converted {Path(file_path).name} → {Path(output_path).name}\n'
                self.after(0, self._update_progress, progress, message)
            except Exception as exc:
                message = f'Failed to convert {Path(file_path).name}: {exc}\n'
                self.after(0, self._log_message, message)

        self.after(0, self._finish_conversion)

    def _update_progress(self, progress, text):
        self.conversion_progress.set(progress)
        self._log_message(text)

    def _finish_conversion(self):
        self._log_message('Conversion finished.\n')
        self.convert_btn.configure(state='normal')
        self.send_files_btn.configure(state='normal')

    def _get_output_path(self, file_path, selected_format):
        path = Path(file_path)
        suffix = '.jpg' if selected_format == 'JPEG' else '.png'
        output_dir = Path(self.output_dir) if self.output_dir else path.parent
        return output_dir.joinpath(f'{path.stem}_converted{suffix}')

    def _log_message(self, text):
        self.files_log.configure(state='normal')
        self.files_log.insert(END, text)
        self.files_log.configure(state='disabled')

# -- BACKUP FRAME --
class BackupFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.label = ctk.CTkLabel(master=self, text='Backup')
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.backup_log = ctk.CTkTextbox(master=self, corner_radius=0)
        configure_text_tags(self.backup_log, MSG_COLORS)
        self.backup_log.configure(state='disabled')
        self.backup_log.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='nsew')

        self.files_input_path = ctk.CTkEntry(master=self, placeholder_text='Type the path of the files you want to backup', state='disabled')
        self.files_input_path.grid(row=2, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.select_input_path_btn = ctk.CTkButton(master=self, text='Select Input Path', command=self.select_input_path)
        self.select_input_path_btn.grid(row=2, column=1, padx=10, pady=(0, 10), sticky='ew')

        self.files_output_path = ctk.CTkEntry(master=self, placeholder_text='Type the path of the output folder', state='disabled')
        self.files_output_path.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.select_output_path_btn = ctk.CTkButton(master=self, text='Select Output Path', command=self.select_output_path)
        self.select_output_path_btn.grid(row=3, column=1, padx=10, pady=(0, 10), sticky='ew')

        self.backup_btn = ctk.CTkButton(master=self, text='Backup', fg_color="#0CCA4A", hover_color="#008F39", command=self.backup_files, state='disabled')
        self.backup_btn.grid(row=4, column=1, padx=10, pady=(0, 10), sticky='ew')

    def _update_backup_button_state(self):
        input_path = self.files_input_path.get().strip()
        output_path = self.files_output_path.get().strip()
        state = 'normal' if input_path and output_path else 'disabled'
        self.backup_btn.configure(state=state)

    def _set_backup_controls_state(self, enabled: bool):
        self.select_input_path_btn.configure(state='normal' if enabled else 'disabled')
        self.select_output_path_btn.configure(state='normal' if enabled else 'disabled')
        if enabled:
            self._update_backup_button_state()
        else:
            self.backup_btn.configure(state='disabled')

    def _write_log_message(self, text, level='default'):
        self.backup_log.configure(state='normal')
        self.backup_log.insert(END, text, level)
        self.backup_log.configure(state='disabled')
        self.backup_log.see(END)

    # -- BACKUP METHODS --
    def select_input_path(self):
        input_path = fd.askdirectory(title='Select input folder')
        if input_path:
            self.files_input_path.configure(state='normal')
            self.files_input_path.delete(0, END)
            self.files_input_path.insert(0, input_path)
            self.files_input_path.configure(state='disabled')
            self._update_backup_button_state()

    def select_output_path(self):
        output_path = fd.askdirectory(title='Select output folder')
        if output_path:
            self.files_output_path.configure(state='normal')
            self.files_output_path.delete(0, END)
            self.files_output_path.insert(0, output_path)
            self.files_output_path.configure(state='disabled')
            self._update_backup_button_state()

    def backup_files(self):
        input_path = self.files_input_path.get().strip()
        output_path = self.files_output_path.get().strip()
        if not input_path or not output_path:
            return

        self._set_backup_controls_state(False)
        self._write_log_message(f'Starting backup from {input_path} to {output_path}...\n')

        thread = threading.Thread(target=self._backup_files_thread, args=(input_path, output_path), daemon=True)
        thread.start()

    def _backup_files_thread(self, input_path, output_path):
        try:
            backup_folder_name = datetime.now().strftime('Backup_%Y-%m-%d_%H%M%S')
            output_with_backup_dir = os.path.join(output_path, backup_folder_name)
            os.makedirs(output_with_backup_dir, exist_ok=True)
            self.after(0, self._write_log_message, f'Created backup folder: {output_with_backup_dir}\n')

            copied_count = 0
            for root, dirs, files in os.walk(input_path):
                rel_root = os.path.relpath(root, input_path)
                target_root = os.path.join(output_with_backup_dir, rel_root) if rel_root != '.' else output_with_backup_dir
                os.makedirs(target_root, exist_ok=True)

                for file_name in files:
                    src_file = os.path.join(root, file_name)
                    dst_file = os.path.join(target_root, file_name)
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                    self.after(0, self._write_log_message, 'Copying ', 'default')
                    self.after(0, self._write_log_message, f'{src_file}', 'info')
                    self.after(0, self._write_log_message, ' to ', 'default')
                    self.after(0, self._write_log_message, f'{dst_file}\n', 'success')

            self.after(0, self._write_log_message, f'Backup completed from {input_path} to {output_with_backup_dir}. Total files copied: {copied_count}\n', 'success')
        except Exception as e:
            self.after(0, self._write_log_message, f'Error during backup: {e}\n')
        finally:
            self.after(0, self._set_backup_controls_state, True)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.minsize(800, 600)
        
        self.console_frame = ConsoleFrame(self)
        self.console_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.file_operations_tab = FileOperationsTab(self)
        self.file_operations_tab.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

if __name__ == '__main__':
    root = App()
    root.title("Yanagi Workbench")
    root.mainloop()
