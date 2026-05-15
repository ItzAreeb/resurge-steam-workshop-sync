import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

# =========================================================
# BO3 Workshop -> Resurge Sync Tool
# =========================================================

APP_TITLE = "BO3 Workshop Sync Tool"


class BO3SyncTool:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("850x550")

        # -------------------------------------------------
        # Variables
        # -------------------------------------------------
        self.game_path_var = tk.StringVar()
        self.workshop_path_var = tk.StringVar()

        # -------------------------------------------------
        # Auto Detect Paths
        # -------------------------------------------------
        self.auto_detect_paths()

        # -------------------------------------------------
        # UI
        # -------------------------------------------------
        self.build_ui()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):
        padding_x = 12
        padding_y = 8

        # -----------------------------
        # Game Folder
        # -----------------------------
        tk.Label(
            self.root,
            text="Black Ops III Game Folder"
        ).pack(anchor="w", padx=padding_x, pady=(15, 0))

        game_frame = tk.Frame(self.root)
        game_frame.pack(fill="x", padx=padding_x, pady=padding_y)

        tk.Entry(
            game_frame,
            textvariable=self.game_path_var
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            game_frame,
            text="Browse",
            command=self.browse_game_folder
        ).pack(side="left", padx=5)

        # -----------------------------
        # Workshop Folder
        # -----------------------------
        tk.Label(
            self.root,
            text="Steam Workshop Folder (311210)"
        ).pack(anchor="w", padx=padding_x)

        workshop_frame = tk.Frame(self.root)
        workshop_frame.pack(fill="x", padx=padding_x, pady=padding_y)

        tk.Entry(
            workshop_frame,
            textvariable=self.workshop_path_var
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            workshop_frame,
            text="Browse",
            command=self.browse_workshop_folder
        ).pack(side="left", padx=5)

        # -----------------------------
        # Sync Button
        # -----------------------------
        tk.Button(
            self.root,
            text="Sync Workshop Content",
            height=2,
            command=self.sync_workshop_content
        ).pack(pady=15)

        # -----------------------------
        # Log Output
        # -----------------------------
        tk.Label(
            self.root,
            text="Log Output"
        ).pack(anchor="w", padx=padding_x)

        self.log_box = scrolledtext.ScrolledText(
            self.root,
            height=18
        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=padding_x,
            pady=(0, 15)
        )

    # =====================================================
    # Logging
    # =====================================================

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        self.root.update()

    # =====================================================
    # Auto Detect
    # =====================================================

    def auto_detect_paths(self):
        possible_steam_locations = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Steam",
            r"D:\Steam",
            r"E:\Steam"
        ]

        detected_game_path = ""
        detected_workshop_path = ""

        for steam_root in possible_steam_locations:
            steamapps = Path(steam_root) / "steamapps"

            # -----------------------------
            # Detect BO3 Game Folder
            # -----------------------------
            possible_game = steamapps / "common" / "Call of Duty Black Ops III"

            if possible_game.exists():
                detected_game_path = str(possible_game)

            # -----------------------------
            # Detect Workshop Folder
            # -----------------------------
            possible_workshop = steamapps / "workshop" / "content" / "311210"

            if possible_workshop.exists():
                detected_workshop_path = str(possible_workshop)

        self.game_path_var.set(detected_game_path)
        self.workshop_path_var.set(detected_workshop_path)

    # =====================================================
    # Browse Functions
    # =====================================================

    # =====================================================
    # Browse Functions
    # =====================================================

    def browse_game_folder(self):
        current_path = self.game_path_var.get()

        folder = filedialog.askdirectory(
            initialdir=current_path if os.path.exists(current_path) else "/"
        )

        if folder:
            self.game_path_var.set(folder)

    def browse_workshop_folder(self):
        current_path = self.workshop_path_var.get()

        folder = filedialog.askdirectory(
            initialdir=current_path if os.path.exists(current_path) else "/"
        )

        if folder:
            self.workshop_path_var.set(folder)

    # =====================================================
    # Determine if item is a mod or map
    # =====================================================

    def determine_type(self, workshop_data):
        """
        Attempts to determine if content is a mod or a map.
        """

        title = str(workshop_data.get("Title", "")).lower()
        folder_name = str(workshop_data.get("FolderName", "")).lower()
        description = str(workshop_data.get("Description", "")).lower()

        combined = f"{title} {folder_name} {description}"

        mod_keywords = [
            "mod",
            "weapon pack",
            "hud",
            "gameplay",
            "menu",
            "custom weapons"
        ]

        for keyword in mod_keywords:
            if keyword in combined:
                return "mods"

        return "usermaps"

    # =====================================================
    # Main Sync
    # =====================================================

    def sync_workshop_content(self):
        game_path = Path(self.game_path_var.get())
        workshop_path = Path(self.workshop_path_var.get())

        # -----------------------------
        # Validation
        # -----------------------------
        if not game_path.exists():
            messagebox.showerror(
                "Error",
                "Game folder path is invalid."
            )
            return

        if not workshop_path.exists():
            messagebox.showerror(
                "Error",
                "Workshop folder path is invalid."
            )
            return

        self.log("===================================")
        self.log("Starting Sync...")
        self.log("===================================")

        # -----------------------------
        # Create mods/usermaps folders
        # -----------------------------
        mods_folder = game_path / "mods"
        usermaps_folder = game_path / "usermaps"

        mods_folder.mkdir(exist_ok=True)
        usermaps_folder.mkdir(exist_ok=True)

        self.log("Verified mods and usermaps folders.")

        # -----------------------------
        # Iterate Workshop Items
        # -----------------------------
        workshop_items = [
            item for item in workshop_path.iterdir()
            if item.is_dir()
        ]

        total_synced = 0

        for item_folder in workshop_items:
            try:
                workshop_json = item_folder / "workshop.json"

                if not workshop_json.exists():
                    self.log(f"[SKIPPED] No workshop.json in {item_folder.name}")
                    continue

                # -----------------------------
                # Read workshop.json
                # -----------------------------
                with open(workshop_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                folder_name = data.get("FolderName")

                if not folder_name:
                    self.log(f"[SKIPPED] No FolderName in {item_folder.name}")
                    continue

                content_type = self.determine_type(data)

                # -----------------------------
                # Destination
                # -----------------------------
                if content_type == "mods":
                    destination_root = mods_folder
                else:
                    destination_root = usermaps_folder

                final_folder = destination_root / folder_name
                zone_folder = final_folder / "zone"

                # -----------------------------
                # Create folders
                # -----------------------------
                zone_folder.mkdir(parents=True, exist_ok=True)

                # -----------------------------
                # Copy ALL contents
                # -----------------------------
                for content in item_folder.iterdir():
                    src = content
                    dst = zone_folder / content.name

                    # Remove old content first
                    if dst.exists():
                        if dst.is_dir():
                            shutil.rmtree(dst)
                        else:
                            dst.unlink()

                    # Copy
                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)

                self.log(
                    f"[SYNCED] {folder_name} -> {content_type}"
                )

                total_synced += 1

            except Exception as e:
                self.log(
                    f"[ERROR] {item_folder.name}: {str(e)}"
                )

        self.log("===================================")
        self.log(f"Sync Complete. {total_synced} items synced.")
        self.log("===================================")

        messagebox.showinfo(
            "Done",
            f"Sync Complete.\n\n{total_synced} items synced."
        )


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = BO3SyncTool(root)
    root.mainloop()