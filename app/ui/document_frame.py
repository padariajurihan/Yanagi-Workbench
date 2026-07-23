import customtkinter as ctk

from app.shared.shared import MSG_COLORS, configure_text_tags
from app.tools.document_converter import DocumentConverterLogic


class DocumentFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.input_format_var = ctk.StringVar(value='PDF')
        self.output_format_var = ctk.StringVar(value='DOCX')
        self.output_dir_var = ctk.StringVar(value='')
        self.logic = DocumentConverterLogic(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title = ctk.CTkLabel(self, text="Document Converter", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.file_log = ctk.CTkTextbox(self, corner_radius=0)
        configure_text_tags(self.file_log, MSG_COLORS)
        self.file_log.configure(state="disabled")
        self.file_log.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        self.format_frame = ctk.CTkFrame(self)
        self.format_frame.grid_columnconfigure(0, weight=1)
        self.format_frame.grid_columnconfigure(1, weight=1)
        self.format_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.input_format_label = ctk.CTkLabel(self.format_frame, text="Input type:")
        self.input_format_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_format_combo = ctk.CTkComboBox(
            self.format_frame,
            values=['PDF', 'DOCX'],
            variable=self.input_format_var,
            state='readonly',
        )
        self.input_format_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.output_format_label = ctk.CTkLabel(self.format_frame, text="Output type:")
        self.output_format_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_format_combo = ctk.CTkComboBox(
            self.format_frame,
            values=['DOCX', 'PDF'],
            variable=self.output_format_var,
            state='readonly',
        )
        self.output_format_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.output_dir_entry = ctk.CTkEntry(
            self,
            textvariable=self.output_dir_var,
            placeholder_text='Output directory',
            state='disabled',
        )
        self.output_dir_entry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.select_output_dir_button = ctk.CTkButton(
            self,
            text="Select Output Directory",
            command=self.logic.select_output_directory,
        )
        self.select_output_dir_button.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        self.select_files_button = ctk.CTkButton(
            self,
            text="Select Files",
            command=self.logic.select_input_files,
        )
        self.select_files_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.selection_clear_button = ctk.CTkButton(
            self,
            text="Clear Selection",
            command=self.logic.clear_selection,
        )
        self.selection_clear_button.grid(row=4, column=1, padx=10, pady=(0, 10), sticky="ew")

        self.convert_button = ctk.CTkButton(
            self,
            text="Convert",
            state='disabled',
            command=self.logic.convert_files,
        )
        self.convert_button.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")


