import subprocess
import os
from pathlib import Path

from constants import CONTRACTOR


BINARY_MARK = ";."

FILE_NAME = f"BLOrders-{CONTRACTOR}" if CONTRACTOR else "BLOrders"
BASE_PATH = os.getcwd()
MAIN_FILE = "../BLOrders.py"
CREDENTIALS_PATH = "../credentials.json;."
DRIVE_DESTINATION_PATH = "../drive_folders_destination.json;."


output_path = Path(BASE_PATH) / "output"
output_path.mkdir(parents=True, exist_ok=True)
os.chdir("output/")

subprocess.run(
    [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name",
        FILE_NAME,
        "--add-data",
        CREDENTIALS_PATH,
        "--add-data",
        DRIVE_DESTINATION_PATH,
        MAIN_FILE,
    ]
)
