import sys
import ctypes
import tkinter as tk
from gui import BO3SyncGUI


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":

    # 🔥 if not admin, relaunch as admin
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
        sys.exit()

    root = tk.Tk()
    app = BO3SyncGUI(root)
    root.mainloop()