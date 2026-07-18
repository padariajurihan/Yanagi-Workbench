import customtkinter as ctk

from app.tools.image_converter import ImageConverterLogic


class ImageConverterFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.output_dir_var = ctk.StringVar(value='')
        self.format_var = ctk.StringVar(value='JPEG')
        self.logic = ImageConverterLogic(self)

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
        self.button_frame.grid_columnconfigure(2, weight=1)

        self.send_files_btn = ctk.CTkButton(master=self.button_frame, text='Select your files here')
        self.send_files_btn.grid(row=0, column=0, sticky='ew')
        self.send_files_btn.bind('<Button-1>', self.logic.open_file)

        self.convert_btn = ctk.CTkButton(master=self.button_frame, text='Convert', state='disabled', command=self.logic.convert_files)
        self.convert_btn.grid(row=0, column=1, padx=(10, 0), sticky='ew')

        self.clear_log_btn = ctk.CTkButton(master=self.button_frame, text='Clear Log', fg_color='#D90429', hover_color='#A3001C', command=self.logic.clear_log)
        self.clear_log_btn.grid(row=0, column=2, padx=(10, 0), sticky='ew')

        self.output_frame = ctk.CTkFrame(master=self)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(1, weight=0)

        self.output_dir_entry = ctk.CTkEntry(
            master=self.output_frame,
            textvariable=self.output_dir_var,
            placeholder_text='Output directory',
            state='disabled',
        )
        self.output_dir_entry.grid(row=0, column=0, sticky='ew')

        self.select_output_dir_btn = ctk.CTkButton(master=self.output_frame, text='Select Path', command=self.logic.select_output_path)
        self.select_output_dir_btn.grid(row=0, column=1, padx=(10, 0), sticky='ew')

        self.output_frame.grid_remove()

        self.conversion_progress = ctk.CTkProgressBar(master=self)
        self.conversion_progress.set(0.0)
        self.conversion_progress.grid(row=4, column=0, padx=10, pady=(0, 10), sticky='ew')

        self.desired_format_frame = ctk.CTkFrame(master=self)
        self.desired_format_frame.grid_columnconfigure(0, weight=1)
        self.desired_format_frame.grid_columnconfigure(1, weight=1)

        self.format_label = ctk.CTkLabel(master=self.desired_format_frame, text='Desired format:')
        self.format_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.jpeg_radio = ctk.CTkRadioButton(master=self.desired_format_frame, variable=self.format_var, value='JPEG', text='JPEG')
        self.jpeg_radio.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.png_radio = ctk.CTkRadioButton(master=self.desired_format_frame, variable=self.format_var, value='PNG', text='PNG')
        self.png_radio.grid(row=1, column=1, padx=10, pady=(0, 10), sticky='w')
