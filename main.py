import customtkinter as ctk
from tools.backup import BackupFrame
from tools.console import ConsoleFrame
from tools.image_converter import ImageConverterFrame
from tools.config import APP_TITLE, APP_MIN_SIZE

class FileOperationsTab(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.add('File Converter')
        self.add('Backup')

        # Configure the 'File Converter' tab to expand
        image_converter_tab = self.tab('File Converter')
        image_converter_tab.grid_rowconfigure(0, weight=1)
        image_converter_tab.grid_columnconfigure(0, weight=1)

        self.image_converter_frame = ImageConverterFrame(image_converter_tab)
        self.image_converter_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # Configure the 'Backup' tab to expand
        backup_tab = self.tab('Backup')
        backup_tab.grid_rowconfigure(0, weight=1)
        backup_tab.grid_columnconfigure(0, weight=1)

        self.backup_frame = BackupFrame(backup_tab)
        self.backup_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.console_frame = ConsoleFrame(self)
        self.console_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.file_operations_tab = FileOperationsTab(self)
        self.file_operations_tab.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

if __name__ == '__main__':
    root = App()
    root.title(APP_TITLE)
    root.minsize(*APP_MIN_SIZE)
    root.mainloop()
