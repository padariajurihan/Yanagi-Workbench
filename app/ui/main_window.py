import customtkinter as ctk

from app.config.config import APP_TITLE, APP_MIN_SIZE
from app.shared.shared import ICONS
from app.ui.backup_frame import BackupFrame
from app.ui.console_frame import ConsoleFrame
from app.ui.image_converter_frame import ImageConverterFrame
from app.ui.document_frame import DocumentFrame


class ToolsColumn(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)

        self.console_widget_btn = ctk.CTkButton(
            self,
            image=ICONS["console"],
            text="Console",
            compound="left",
            command=lambda: self._show_widget(ConsoleFrame),
        )
        self.console_widget_btn.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.backup_widget_btn = ctk.CTkButton(
            self,
            image=ICONS["backup"],
            text="Backup",
            compound="left",
            command=lambda: self._show_widget(BackupFrame),
        )
        self.backup_widget_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.image_converter_widget_btn = ctk.CTkButton(
            self,
            image=ICONS["image_converter"],
            text="Image Converter",
            compound="left",
            command=lambda: self._show_widget(ImageConverterFrame),
        )
        self.image_converter_widget_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.document_widget_btn = ctk.CTkButton(
            self,
            image=ICONS["document_converter"],
            text="Document Converter",
            compound="left",
            command=lambda: self._show_widget(DocumentFrame),
        )
        self.document_widget_btn.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")

    def _show_widget(self, widget_class):
        current_widget = getattr(self.master, "current_widget", None)
        if current_widget is not None:
            current_widget.destroy()

        widget = widget_class(self.master)
        widget.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.master.current_widget = widget


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.current_widget = None

        self.tools_column = ToolsColumn(self)
        self.tools_column.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tools_column._show_widget(ConsoleFrame)

        self.title(APP_TITLE)
        self.minsize(*APP_MIN_SIZE)
