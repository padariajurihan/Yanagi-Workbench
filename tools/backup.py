import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.constants import END
import os
import shutil
import threading
from datetime import datetime
from tools.shared import MSG_COLORS, configure_text_tags

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
        # Input now supports selecting individual files and folders
        self.selected_input_files = []
        self.selected_input_folders = []
        self.files_input_path = ctk.CTkEntry(master=self, placeholder_text='Selected files (Add files or folders)', state='disabled')
        self.files_input_path.grid(row=2, column=0, padx=10, pady=(0, 10), sticky='ew')

        # Input selection buttons
        self.input_buttons_frame = ctk.CTkFrame(master=self)
        self.input_buttons_frame.grid(row=2, column=1, padx=10, pady=(0, 10), sticky='ew')
        self.input_buttons_frame.grid_columnconfigure(0, weight=1)
        self.input_buttons_frame.grid_columnconfigure(1, weight=1)

        self.select_input_mixed_btn = ctk.CTkButton(master=self.input_buttons_frame, text='Add Files/Folders', command=self.select_files_and_folders)
        self.select_input_mixed_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.clear_selection_btn = ctk.CTkButton(master=self.input_buttons_frame, text='Clear Selection', command=self.clear_selection, fg_color='#D90429', hover_color='#A3001C')
        self.clear_selection_btn.grid(row=0, column=1, sticky='ew', padx=(5, 0))

        self.files_output_path = ctk.CTkEntry(master=self, placeholder_text='Type the path of the output folder', state='disabled')
        self.files_output_path.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.select_output_path_btn = ctk.CTkButton(master=self, text='Select Output Path', command=self.select_output_path)
        self.select_output_path_btn.grid(row=3, column=1, padx=10, pady=(0, 10), sticky='ew')

        self.backup_btn = ctk.CTkButton(master=self, text='Backup', fg_color="#0CCA4A", hover_color="#008F39", command=self.backup_files, state='disabled')
        self.backup_btn.grid(row=4, column=1, padx=10, pady=(0, 10), sticky='ew')

    def _update_backup_button_state(self):
        output_path = self.files_output_path.get().strip()
        # Enable when at least one input file or folder is selected and an output folder is set
        has_input = bool(self.selected_input_files or self.selected_input_folders)
        state = 'normal' if has_input and output_path else 'disabled'
        self.backup_btn.configure(state=state)

    def _set_backup_controls_state(self, enabled: bool):
        self.select_input_mixed_btn.configure(state='normal' if enabled else 'disabled')
        self.clear_selection_btn.configure(state='normal' if enabled else 'disabled')
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
    def select_files_and_folders(self):
        """Open a simple dialog to browse and select files and folders."""
        top = tk.Toplevel(self)
        top.title('Add files and folders')
        top.geometry('700x450')
        current_path = tk.StringVar(value=os.path.expanduser('~'))

        def list_dir(path):
            try:
                entries = os.listdir(path)
            except Exception:
                entries = []
            entries.sort()
            lb.delete(0, tk.END)
            # show directories first
            for name in entries:
                full = os.path.join(path, name)
                display = name + '/' if os.path.isdir(full) else name
                lb.insert(tk.END, display)

        def go_up():
            p = os.path.dirname(current_path.get())
            if p:
                current_path.set(p)
                list_dir(p)

        def enter_dir(event=None):
            sel = lb.curselection()
            if not sel:
                return
            name = lb.get(sel[0])
            if name.endswith('/'):
                newp = os.path.join(current_path.get(), name[:-1])
                current_path.set(newp)
                list_dir(newp)

        def add_selected():
            sel = lb.curselection()
            to_add = []
            for i in sel:
                name = lb.get(i)
                if name.endswith('/'):
                    path = os.path.join(current_path.get(), name[:-1])
                else:
                    path = os.path.join(current_path.get(), name)
                to_add.append(path)
            self._add_paths(to_add)
            top.destroy()

        # top widgets
        path_entry = tk.Entry(top, textvariable=current_path)
        path_entry.pack(fill='x', padx=8, pady=6)

        btn_frame = tk.Frame(top)
        btn_frame.pack(fill='x', padx=8)
        tk.Button(btn_frame, text='Up', command=go_up).pack(side='left')
        tk.Button(btn_frame, text='Refresh', command=lambda: list_dir(current_path.get())).pack(side='left')

        frame = tk.Frame(top)
        frame.pack(fill='both', expand=True, padx=8, pady=6)
        sb = tk.Scrollbar(frame)
        sb.pack(side='right', fill='y')
        lb = tk.Listbox(frame, selectmode=tk.MULTIPLE, yscrollcommand=sb.set)
        lb.pack(fill='both', expand=True)
        sb.config(command=lb.yview)

        lb.bind('<Double-1>', enter_dir)

        control_frame = tk.Frame(top)
        control_frame.pack(fill='x', padx=8, pady=6)
        tk.Button(control_frame, text='Add Selected', command=add_selected).pack(side='right')
        tk.Button(control_frame, text='Cancel', command=top.destroy).pack(side='right')

        list_dir(current_path.get())

    def select_output_path(self):
        output_path = fd.askdirectory(title='Select output folder')
        if output_path:
            self.files_output_path.configure(state='normal')
            self.files_output_path.delete(0, END)
            self.files_output_path.insert(0, output_path)
            self.files_output_path.configure(state='disabled')
            self._update_backup_button_state()

    def _update_selection_entry(self):
        total = len(self.selected_input_files) + len(self.selected_input_folders)
        if total == 0:
            summary = 'No items selected'
        elif total == 1:
            if self.selected_input_files:
                summary = self.selected_input_files[0]
            else:
                summary = self.selected_input_folders[0]
        else:
            summary = f'{total} item(s) selected'

        self.files_input_path.configure(state='normal')
        self.files_input_path.delete(0, END)
        self.files_input_path.insert(0, summary)
        self.files_input_path.configure(state='disabled')
        self._update_backup_button_state()

    def _log_selection_details(self, prefix: str):
        self._write_log_message(f'{prefix}\n', 'info')
        if self.selected_input_files:
            self._write_log_message('Files:\n', 'message')
            for path in self.selected_input_files:
                self._write_log_message(f' - {path}\n', 'info')
        if self.selected_input_folders:
            self._write_log_message('Folders:\n', 'message')
            for path in self.selected_input_folders:
                self._write_log_message(f' - {path}\n', 'info')

    def _add_paths(self, paths):
        """Add a list of filesystem paths (files or folders) to the selection."""
        added = False
        for p in paths:
            if os.path.isdir(p):
                if p not in self.selected_input_folders:
                    self.selected_input_folders.append(p)
                    added = True
            elif os.path.isfile(p):
                if p not in self.selected_input_files:
                    self.selected_input_files.append(p)
                    added = True

        if added:
            self._update_selection_entry()
            self._log_selection_details('Selection updated')

    def clear_selection(self):
        if not (self.selected_input_files or self.selected_input_folders):
            self._write_log_message('No items selected to clear.\n', 'info')
            return

        self._write_log_message('Clearing current selection...\n', 'info')
        self._log_selection_details('Selection cleared')
        self.selected_input_files = []
        self.selected_input_folders = []
        self._update_selection_entry()

    def backup_files(self):
        output_path = self.files_output_path.get().strip()
        if not (self.selected_input_files or self.selected_input_folders) or not output_path:
            return

        self._set_backup_controls_state(False)
        total_inputs = len(self.selected_input_files) + len(self.selected_input_folders)
        self._write_log_message(f'Starting backup of {total_inputs} item(s) to {output_path}...\n')

        thread = threading.Thread(target=self._backup_files_thread, args=(self.selected_input_files, self.selected_input_folders, output_path), daemon=True)
        thread.start()

    def _backup_files_thread(self, input_files, input_folders, output_path):
        try:
            backup_folder_name = datetime.now().strftime('Backup_%Y-%m-%d_%H%M%S')
            output_with_backup_dir = os.path.join(output_path, backup_folder_name)
            os.makedirs(output_with_backup_dir, exist_ok=True)
            self.after(0, self._write_log_message, f'Created backup folder: {output_with_backup_dir}\n')

            copied_count = 0

            # First copy folders (preserve folder names)
            for folder in input_folders:
                try:
                    dest = os.path.join(output_with_backup_dir, os.path.basename(folder))
                    # Use copytree; dirs_exist_ok available on Python 3.8+
                    try:
                        shutil.copytree(folder, dest, dirs_exist_ok=True)
                    except TypeError:
                        # Fallback: if dest exists, walk and copy files
                        if not os.path.exists(dest):
                            os.makedirs(dest, exist_ok=True)
                        for root, dirs, files in os.walk(folder):
                            rel = os.path.relpath(root, folder)
                            target_root = os.path.join(dest, rel) if rel != '.' else dest
                            os.makedirs(target_root, exist_ok=True)
                            for fname in files:
                                src_file = os.path.join(root, fname)
                                dst_file = os.path.join(target_root, fname)
                                shutil.copy2(src_file, dst_file)
                                copied_count += 1

                    self.after(0, self._write_log_message, 'Copied folder ', 'default')
                    self.after(0, self._write_log_message, f'{folder}', 'info')
                    self.after(0, self._write_log_message, f' to {dest}\n', 'success')
                except Exception as e:
                    self.after(0, self._write_log_message, f'Failed to copy folder {folder}: {e}\n', 'error')

            # Then copy individual files into the backup root
            for src_file in input_files:
                try:
                    dst_file = os.path.join(output_with_backup_dir, os.path.basename(src_file))
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                    self.after(0, self._write_log_message, 'Copying ', 'default')
                    self.after(0, self._write_log_message, f'{src_file}', 'info')
                    self.after(0, self._write_log_message, ' to ', 'default')
                    self.after(0, self._write_log_message, f'{dst_file}\n', 'success')
                except Exception as inner_exc:
                    self.after(0, self._write_log_message, f'Failed to copy {src_file}: {inner_exc}\n', 'error')

            self.after(0, self._write_log_message, f'Backup completed. Total items copied: {copied_count}\n', 'success')
        except Exception as e:
            self.after(0, self._write_log_message, f'Error during backup: {e}\n')
        finally:
            self.after(0, self._set_backup_controls_state, True)