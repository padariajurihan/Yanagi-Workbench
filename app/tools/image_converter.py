import threading
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.constants import END
from PIL import Image

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pass


class ImageConverterLogic:
    def __init__(self, master):
        self.master = master
        self.master.selected_files = []
        self.master.output_dir = None

    def open_file(self, event):
        files = fd.askopenfilenames(
            title='Select your images here',
            filetypes=[
                ('All files', '*.*'),
                ('JPEG', '*.jpg *.jpeg'),
                ('PNG', '*.png'),
                ('HEIF/HEIC', '*.heif *.heic'),
                ('WebP', '*.webp'),
            ],
        )

        self.master.selected_files = list(files)

        if not self.master.selected_files:
            return

        self.master.files_log.configure(state='normal')
        shown = 0

        for file_path in self.master.selected_files:
            if shown < 5:
                name = Path(file_path).name
                self.master.files_log.insert(END, f'File {name} has been added.\n')
            shown += 1

        remaining = max(0, len(self.master.selected_files) - 5)
        if remaining > 0:
            self.master.files_log.insert(END, f'... and more {remaining} file(s).\n')
        self.master.files_log.insert(END, f'Total files added: {len(self.master.selected_files)}\n')
        self.master.files_log.configure(state='disabled')

        self.master.desired_format_frame.grid(row=5, column=0, padx=10, pady=(0, 10), sticky='ew')
        self.master.output_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
        self._update_convert_button_state()

    def select_output_path(self):
        path = fd.askdirectory(title='Select output folder')
        if not path:
            return

        self.master.output_dir = path
        self.master.output_dir_var.set(path)
        self._update_convert_button_state()

    def _update_convert_button_state(self):
        if self.master.selected_files and self.master.output_dir:
            self.master.convert_btn.configure(state='normal')
        else:
            self.master.convert_btn.configure(state='disabled')

    def convert_files(self):
        self.master.convert_btn.configure(state='disabled')
        self.master.send_files_btn.configure(state='disabled')
        self.master.conversion_progress.set(0.0)
        self._log_message(f'Conversion started to {self.master.format_var.get()}.\n')

        thread = threading.Thread(target=self._convert_files_thread, daemon=True)
        thread.start()

    def _convert_files_thread(self):
        selected_format = self.master.format_var.get()
        total = len(self.master.selected_files)
        converted = 0

        for file_path in self.master.selected_files:
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
                self.master.after(0, self._update_progress, progress, message)
            except Exception as exc:
                message = f'Failed to convert {Path(file_path).name}: {exc}\n'
                self.master.after(0, self._log_message, message)

        self.master.after(0, self._finish_conversion)

    def _update_progress(self, progress, text):
        self.master.conversion_progress.set(progress)
        self._log_message(text)

    def _finish_conversion(self):
        self._log_message('Conversion finished.\n')
        self.master.convert_btn.configure(state='normal')
        self.master.send_files_btn.configure(state='normal')

    def _get_output_path(self, file_path, selected_format):
        path = Path(file_path)
        suffix = '.jpg' if selected_format == 'JPEG' else '.png'
        output_dir = Path(self.master.output_dir) if self.master.output_dir else path.parent
        return output_dir.joinpath(f'{path.stem}_converted{suffix}')

    def _log_message(self, text):
        self.master.files_log.configure(state='normal')
        self.master.files_log.insert(END, text)
        self.master.files_log.configure(state='disabled')

    def clear_log(self):
        self.master.files_log.configure(state='normal')
        self.master.files_log.delete(1.0, END)
        self.master.files_log.configure(state='disabled')
        self._log_message('File log cleared.\n')
