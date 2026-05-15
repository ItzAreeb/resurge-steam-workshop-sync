import os
import json
import shutil
from pathlib import Path


class BO3SyncEngine:
    def __init__(self, logger=print):
        self.log = logger

    # -----------------------------
    # Determine mod or map
    # -----------------------------
    def determine_type(self, workshop_data):
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

    # -----------------------------
    # Core sync function
    # -----------------------------
    def sync(self, game_path: Path, workshop_path: Path):
        if not game_path.exists():
            raise ValueError("Game path invalid")

        if not workshop_path.exists():
            raise ValueError("Workshop path invalid")

        self.log("Starting sync...")

        mods_folder = game_path / "mods"
        usermaps_folder = game_path / "usermaps"

        mods_folder.mkdir(exist_ok=True)
        usermaps_folder.mkdir(exist_ok=True)

        workshop_items = [i for i in workshop_path.iterdir() if i.is_dir()]

        total = 0

        for item_folder in workshop_items:
            try:
                json_path = item_folder / "workshop.json"

                if not json_path.exists():
                    self.log(f"Skip {item_folder.name} (no workshop.json)")
                    continue

                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                folder_name = data.get("FolderName")
                if not folder_name:
                    self.log(f"Skip {item_folder.name} (no FolderName)")
                    continue

                content_type = self.determine_type(data)

                base = mods_folder if content_type == "mods" else usermaps_folder

                final_folder = base / folder_name
                zone_folder = final_folder / "zone"

                zone_folder.mkdir(parents=True, exist_ok=True)

                # copy everything into zone
                for content in item_folder.iterdir():
                    dst = zone_folder / content.name

                    if dst.exists():
                        if dst.is_dir():
                            shutil.rmtree(dst)
                        else:
                            dst.unlink()

                    if content.is_dir():
                        shutil.copytree(content, dst)
                    else:
                        shutil.copy2(content, dst)

                self.log(f"Synced {folder_name} -> {content_type}")
                total += 1

            except Exception as e:
                self.log(f"Error {item_folder.name}: {e}")

        self.log(f"Done. {total} items synced.")
        return total