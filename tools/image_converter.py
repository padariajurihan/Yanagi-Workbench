import customtkinter as ctk
import threading
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.constants import END
from PIL import Image
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    # If registration fails, PIL may still handle formats if system libs are present.
    pass

# -- IMAGE CONVERTER FRAME --
class ImageConverterFrame(ctk.CTkFrame):
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
