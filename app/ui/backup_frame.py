import customtkinter as ctk

from app.tools.backup import BackupLogic
from app.shared.shared import MSG_COLORS, configure_text_tags


class BackupFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.logic = BackupLogic(self)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.label = ctk.CTkLabel(master=self, text='Backup')
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.backup_log = ctk.CTkTextbox(master=self, corner_radius=0)
        configure_text_tags(self.backup_log, MSG_COLORS)
        self.backup_log.configure(state='disabled')
        self.backup_log.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='nsew')

        self.selected_input_files = []
        self.selected_input_folders = []

        self.files_input_path = ctk.CTkEntry(master=self, placeholder_text='Selected files (Add files or folders)', state='disabled')
        self.files_input_path.grid(row=2, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.input_buttons_frame = ctk.CTkFrame(master=self)
        self.input_buttons_frame.grid(row=2, column=1, padx=10, pady=(0, 10), sticky='ew')
        self.input_buttons_frame.grid_columnconfigure(0, weight=1)
        self.input_buttons_frame.grid_columnconfigure(1, weight=1)

        self.select_input_mixed_btn = ctk.CTkButton(
            master=self.input_buttons_frame,
            text='Add Files/Folders',
            command=self.logic.select_files_and_folders,
        )
        self.select_input_mixed_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.clear_selection_btn = ctk.CTkButton(
            master=self.input_buttons_frame,
            text='Clear Selection',
            command=self.logic.clear_selection,
            fg_color='#D90429',
            hover_color='#A3001C',
        )
        self.clear_selection_btn.grid(row=0, column=1, sticky='ew', padx=(5, 0))

        self.files_output_path = ctk.CTkEntry(master=self, placeholder_text='Type the path of the output folder', state='disabled')
        self.files_output_path.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.select_output_path_btn = ctk.CTkButton(master=self, text='Select Output Path', command=self.logic.select_output_path)
        self.select_output_path_btn.grid(row=3, column=1, padx=10, pady=(0, 10), sticky='ew')

        self.backup_btn = ctk.CTkButton(
            master=self,
            text='Backup',
            fg_color='#0CCA4A',
            hover_color='#008F39',
            command=self.logic.backup_files,
            state='disabled',
        )
        self.backup_btn.grid(row=4, column=1, padx=10, pady=(0, 10), sticky='ew')

        self.clear_log_btn = ctk.CTkButton(
            master=self,
            text='Clear Log',
            fg_color='#D90429',
            hover_color='#A3001C',
            command=self.logic.clear_log,
        )
        self.clear_log_btn.grid(row=4, column=0, padx=10, pady=(0, 10), sticky='ew')
