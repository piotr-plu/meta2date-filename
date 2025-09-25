"""Tkinter user interface for the meta2date filename application."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from .constants import DATE_HELP_TEXT, DEFAULT_EXTENSION, DEFAULT_FILE_NAME, DEFAULT_PATH_DIR
from .renamer import FileRenamer, RenameSettings, parse_extensions


class DataFileChangerApp(tk.Tk):
    """Tkinter top-level window orchestrating user input and rename execution."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Change Name To Modify Date")
        self.resizable(False, False)

        self.dir_path_var = tk.StringVar(value=DEFAULT_PATH_DIR)
        self.extension_var = tk.StringVar(value=DEFAULT_EXTENSION)
        self.date_origin_var = tk.StringVar(value="Modify date")
        self.name_structure_var = tk.StringVar()
        self.template_var = tk.StringVar(value=DEFAULT_FILE_NAME)
        self.current_settings: RenameSettings | None = None

        self.renamer = FileRenamer(self.append_log)

        self._build_menu()
        self._build_layout()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        menubar.add_command(label="Help", command=self.open_help)
        self.config(menu=menubar)

    def _build_layout(self) -> None:
        settings_frame = tk.LabelFrame(self, text="Settings", padx=10, pady=10)
        settings_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nwe")

        date_get_frame = tk.LabelFrame(self, text="Get date from:", padx=10, pady=10)
        date_get_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nwe")

        name_template_frame = tk.LabelFrame(self, text="Name Template", padx=10, pady=10)
        name_template_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nwe")

        log_window_frame = tk.LabelFrame(self, text="Logs", padx=10, pady=10)
        log_window_frame.grid(row=0, column=1, padx=15, pady=15, rowspan=3)

        tk.Label(settings_frame, text="Location:").grid(row=0, column=0, sticky="w")
        tk.Entry(settings_frame, textvariable=self.dir_path_var, width=40, border=2).grid(
            row=0, column=1, sticky="we"
        )
        tk.Button(settings_frame, text="...", command=self.browse_directory).grid(row=0, column=2)

        tk.Label(settings_frame, text="Files extensions:").grid(row=1, column=0, sticky="w")
        tk.Entry(settings_frame, textvariable=self.extension_var, width=40, border=2).grid(
            row=1, column=1, sticky="we"
        )

        tk.Radiobutton(
            date_get_frame,
            text="Properties: Modify Date",
            variable=self.date_origin_var,
            value="Modify date",
            justify="left",
            command=self._toggle_name_structure_state,
        ).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(
            date_get_frame,
            text="Properties: Create Date",
            variable=self.date_origin_var,
            value="Create date",
            justify="left",
            command=self._toggle_name_structure_state,
        ).grid(row=1, column=0, sticky="w")
        tk.Radiobutton(
            date_get_frame,
            text="File Name",
            variable=self.date_origin_var,
            value="File name",
            justify="left",
            command=self._toggle_name_structure_state,
        ).grid(row=2, column=0, sticky="w")

        tk.Label(date_get_frame, text="Point the date:").grid(row=2, column=1, padx=(10, 0))
        self.name_structure_entry = tk.Entry(
            date_get_frame, textvariable=self.name_structure_var, width=30, border=2
        )
        self.name_structure_entry.grid(row=2, column=2)
        self.name_structure_entry.config(state=tk.DISABLED)

        tk.Label(name_template_frame, text="Build name template for files:").grid(
            row=0, column=0, sticky="w"
        )
        tk.Entry(name_template_frame, textvariable=self.template_var, width=40, border=2).grid(
            row=0, column=1, sticky="we"
        )

        log_scrollbar = tk.Scrollbar(log_window_frame, orient=tk.VERTICAL)
        self.log_text = tk.Text(
            log_window_frame,
            height=20,
            width=60,
            yscrollcommand=log_scrollbar.set,
            state=tk.DISABLED,
        )
        self.log_text.grid(row=0, column=0)
        log_scrollbar.config(command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")

        tk.Button(self, text="Apply", width=20, command=self.apply_settings).grid(
            row=3, column=0, padx=5, pady=5, columnspan=2
        )
        tk.Button(self, text="Run", width=20, height=2, command=self.run_renamer).grid(
            row=4, column=0, padx=10, pady=10, columnspan=2
        )

    def browse_directory(self) -> None:
        """Prompt the user for a directory and update the bound entry field."""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path_var.set(directory)

    def _toggle_name_structure_state(self) -> None:
        if self.date_origin_var.get() == "File name":
            self.name_structure_entry.config(state=tk.NORMAL)
        else:
            self.name_structure_entry.config(state=tk.DISABLED)

    def open_help(self) -> None:
        """Show a modal window with available strftime placeholders."""
        help_window = tk.Toplevel(self)
        help_window.title("Help")

        tk.Label(help_window, text="Help for Name Template tags:", padx=10, pady=10).pack(
            padx=10, pady=10
        )

        help_scrollbar = tk.Scrollbar(help_window, orient=tk.VERTICAL)
        help_text = tk.Text(
            help_window,
            height=20,
            width=90,
            padx=15,
            pady=15,
            yscrollcommand=help_scrollbar.set,
        )
        help_scrollbar.config(command=help_text.yview)
        help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text.pack(padx=30, pady=20)
        help_text.insert(tk.END, DATE_HELP_TEXT)
        help_text.config(state=tk.DISABLED)

    def apply_settings(self) -> None:
        """Validate the current form values and store them for later execution."""
        directory_value = self.dir_path_var.get().strip()
        if not directory_value:
            self.append_log("----- Error -----\n")
            self.append_log("Specify a directory before applying settings.\n\n")
            return

        directory = Path(directory_value).expanduser()
        if not directory.exists() or not directory.is_dir():
            self.append_log("----- Error -----\n")
            self.append_log("Selected location is not a valid directory.\n\n")
            return

        extensions, display_extensions = parse_extensions(self.extension_var.get())
        date_origin = self.date_origin_var.get()
        name_structure = self.name_structure_var.get()
        template = self.template_var.get().strip() or DEFAULT_FILE_NAME

        if date_origin == "File name" and not name_structure:
            self.append_log("----- Error -----\n")
            self.append_log("Provide the name structure when using 'File Name'.\n\n")
            return

        self.current_settings = RenameSettings(
            directory=directory,
            extensions=extensions,
            display_extensions=display_extensions,
            date_origin=date_origin,
            name_structure=name_structure,
            template=template,
        )

        extensions_display = ", ".join(display_extensions)
        self.append_log("----- Set Settings -----\n")
        self.append_log(f"Location: {directory}\n")
        self.append_log(f"File extensions: {extensions_display}\n")
        self.append_log(f"Date origin: {date_origin}\n")
        self.append_log(f"Name Template: {template}\n\n")

    def run_renamer(self) -> None:
        """Execute the rename operation using the previously applied settings."""
        if not self.current_settings:
            self.append_log("----- Error -----\n")
            self.append_log("First click Apply button\n\n")
            return

        self.append_log("----- Start Program -----\n")
        renamed = self.renamer.rename_files(self.current_settings)
        self.append_log("----- Done -----\n")
        self.append_log(f"Changed {renamed} files name\n\n")
        self.current_settings = None

    def append_log(self, message: str) -> None:
        """Append text to the log widget while temporarily enabling it."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


__all__ = ["DataFileChangerApp"]
