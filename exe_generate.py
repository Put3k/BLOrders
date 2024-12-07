import subprocess
import os
from pathlib import Path


BINARY_MARK = ";."
BASE_PATH = os.getcwd()
MAIN_FILE = "../BLOrders.py"
CREDENTIALS_PATH = "../credentials.json;."
DRIVE_DESTINATION_PATH = "../drive_folders_destination.json;."

output_path = Path(BASE_PATH) / "output"
output_path.mkdir(parents=True, exist_ok=True)

os.makedirs("exe", exist_ok=True)

CONTRACTORS = ["FAKTORIA", "NICE"]

for contractor in CONTRACTORS:
    # Override credentials for different contractors
    with open("constants.py", "r") as file:
        lines = file.readlines()

    with open("constants.py", "w") as file:
        for line in lines:
            if line.startswith("CONTRACTOR ="):
                file.write(f"CONTRACTOR = '{contractor}'\n")
            else:
                file.write(line)

    FILE_NAME = f"BLOrders-{contractor}" if contractor else "BLOrders"

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
        ],
        cwd="exe/",
    )
