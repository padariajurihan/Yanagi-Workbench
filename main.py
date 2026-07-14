import customtkinter as ctk
from tools.backup import BackupFrame
from tools.console import ConsoleFrame
from tools.image_converter import ImageConverterFrame
from tools.config import APP_TITLE, APP_MIN_SIZE
from tools.shared import ICONS

class ToolsColumn(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        self.console_widget_btn = ctk.CTkButton(self, image=ICONS["console"], text="Console", compound="left", command=lambda: self._show_widget(ConsoleFrame))
        self.console_widget_btn.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.backup_widget_btn = ctk.CTkButton(self, image=ICONS["backup"], text="Backup", compound="left", command=lambda: self._show_widget(BackupFrame))
        self.backup_widget_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.image_converter_widget_btn = ctk.CTkButton(self, image=ICONS["image_converter"], text="Image Converter", compound="left", command=lambda: self._show_widget(ImageConverterFrame))
        self.image_converter_widget_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

    def _show_widget(self, widget_class):
        for widget in self.master.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self:
                widget.destroy()

        widget = widget_class(self.master)
        widget.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        self.tools_column = ToolsColumn(self)
        self.tools_column.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


if __name__ == '__main__':
    root = App()
    root.title(APP_TITLE)
    root.minsize(*APP_MIN_SIZE)
    root.mainloop()
