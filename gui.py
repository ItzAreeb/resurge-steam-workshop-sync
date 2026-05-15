import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from sync_engine import BO3SyncEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class BO3SyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Workshop to Resurge Sync Tool")
        self.root.geometry("900x600")

        self.engine = BO3SyncEngine(logger=self.log)

        self.game_var = ctk.StringVar()
        self.workshop_var = ctk.StringVar()

        self.build_ui()
        self.auto_detect()

    # -----------------------------
    # UI
    # -----------------------------
    def build_ui(self):
        self.root.configure(bg="#0d1117")

        title = ctk.CTkLabel(
            self.root,
            text="BO3 WORKSHOP SYNC",
            font=("Segoe UI", 26, "bold")
        )
        title.pack(pady=20)

        container = ctk.CTkFrame(self.root)
        container.pack(padx=20, pady=10, fill="both", expand=True)

        # GAME
        self.game_entry = ctk.CTkEntry(
            container,
            textvariable=self.game_var,
            placeholder_text="Black Ops III folder path"
        )
        self.game_entry.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkButton(
            container,
            text="Browse Game Folder",
            command=self.browse_game
        ).pack(pady=(0, 10))

        # WORKSHOP
        self.workshop_entry = ctk.CTkEntry(
            container,
            textvariable=self.workshop_var,
            placeholder_text="Workshop 311210 folder"
        )
        self.workshop_entry.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkButton(
            container,
            text="Browse Workshop Folder",
            command=self.browse_workshop
        ).pack(pady=(0, 20))

        # SYNC BUTTON (big modern style)
        ctk.CTkButton(
            container,
            text="SYNC WORKSHOP",
            height=45,
            fg_color="#ff6b00",
            hover_color="#cc5500",
            font=("Segoe UI", 16, "bold"),
            command=self.sync
        ).pack(pady=10)

        # LOG BOX
        self.log_box = ctk.CTkTextbox(
            container,
            height=220
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=15)

    # -----------------------------
    # LOGGING
    # -----------------------------
    def log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.root.update()

    # -----------------------------
    # AUTO DETECT
    # -----------------------------
    def auto_detect(self):
        base = r"C:\Program Files (x86)\Steam\steamapps"

        game = Path(base) / "common" / "Call of Duty Black Ops III"
        workshop = Path(base) / "workshop" / "content" / "311210"

        if game.exists():
            self.game_var.set(str(game))

        if workshop.exists():
            self.workshop_var.set(str(workshop))

    # -----------------------------
    # BROWSE
    # -----------------------------
    def browse_game(self):
        folder = filedialog.askdirectory()
        if folder:
            self.game_var.set(folder)

    def browse_workshop(self):
        folder = filedialog.askdirectory()
        if folder:
            self.workshop_var.set(folder)

    # -----------------------------
    # SYNC
    # -----------------------------
    def sync(self):
        try:
            game_path = Path(self.game_var.get())
            workshop_path = Path(self.workshop_var.get())

            total = self.engine.sync(game_path, workshop_path)

            messagebox.showinfo("Done", f"Synced {total} items")

        except Exception as e:
            messagebox.showerror("Error", str(e))
