import threading
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.constants import END

from pdf2docx import Converter

try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None


class DocumentConverterLogic:
    def __init__(self, master):
        self.master = master
        self.master.selected_files = []
        self.master.output_dir = None

    def select_input_files(self):
        accepted_types = [
            ('PDF files', '*.pdf'),
            ('DOCX files', '*.docx'),
            ('All files', '*.*'),
        ]
        files = fd.askopenfilenames(title='Select files', filetypes=accepted_types)
        if not files:
            return

        self.master.selected_files = list(files)
        self._log_message(f'Selected {len(self.master.selected_files)} file(s) for conversion.\n', 'info')
        for path in self.master.selected_files:
            self._log_message(f' - {Path(path).name}\n', 'default')
        self._update_convert_button_state()

    def select_output_directory(self):
        directory = fd.askdirectory(title='Select output directory')
        if not directory:
            return

        self.master.output_dir = directory
        self.master.output_dir_var.set(directory)
        self._log_message(f'Output directory selected: {directory}\n', 'info')
        self._update_convert_button_state()

    def clear_selection(self):
        self.master.selected_files = []
        self.master.output_dir = None
        self.master.output_dir_var.set('')
        self._log_message('Selection cleared.\n', 'message')
        self._update_convert_button_state()

    def _update_convert_button_state(self):
        if self.master.selected_files and self.master.output_dir:
            self.master.convert_button.configure(state='normal')
        else:
            self.master.convert_button.configure(state='disabled')

    def convert_files(self):
        if not self.master.selected_files or not self.master.output_dir:
            return

        self.master.convert_button.configure(state='disabled')
        self._log_message('Conversion started.\n', 'message')

        thread = threading.Thread(target=self._convert_files_thread, daemon=True)
        thread.start()

    def _convert_files_thread(self):
        input_type = self.master.input_format_var.get()
        output_type = self.master.output_format_var.get()

        for file_path in self.master.selected_files:
            try:
                if input_type == 'PDF' and output_type == 'DOCX':
                    self._convert_pdf_to_docx(file_path)
                elif input_type == 'DOCX' and output_type == 'PDF':
                    self._convert_docx_to_pdf(file_path)
                else:
                    self._log_message(f'Skipping unsupported conversion: {input_type} → {output_type}\n', 'error')
            except Exception as exc:
                self._log_message(f'Failed to convert {Path(file_path).name}: {exc}\n', 'error')

        self.master.after(0, self._conversion_complete)

    def _convert_pdf_to_docx(self, file_path: str):
        output_path = Path(self.master.output_dir) / (Path(file_path).stem + '.docx')
        converter = Converter(file_path)
        converter.convert(str(output_path), start=0, end=None)
        converter.close()
        self._log_message(f'Converted {Path(file_path).name} → {output_path.name}\n', 'success')

    def _convert_docx_to_pdf(self, file_path: str):
        if docx2pdf_convert is None:
            self._log_message('DOCX to PDF conversion requires the optional package docx2pdf.\n', 'error')
            return

        output_path = Path(self.master.output_dir) / (Path(file_path).stem + '.pdf')
        docx2pdf_convert(file_path, str(output_path))
        self._log_message(f'Converted {Path(file_path).name} → {output_path.name}\n', 'success')

    def _conversion_complete(self):
        self._log_message('Conversion completed.\n', 'success')
        self._update_convert_button_state()

    def _log_message(self, message: str, tag: str = 'default'):
        self.master.file_log.configure(state='normal')
        try:
            self.master.file_log.insert(END, message, tag)
        except Exception:
            self.master.file_log.insert(END, message)
        self.master.file_log.configure(state='disabled')
        self.master.file_log.see('end')