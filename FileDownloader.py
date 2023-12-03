import time

from datetime import datetime

from Google import get_service
from DriveAPI import (
    recursive_find_file_id_in_folder,
    map_folder_id_to_design,
    download_file_by_id,
)
from utils import list_file_data_from_csv, get_default_folder_path
from constants import DOWNLOAD_DESIGNS_FOLDER_ID
from error_handling import save_error_to_file, save_list_to_csv


def download_listed_files(csv_file_path: str, drive_folder_id: str):
    drive_service = get_service()
    file_data_list = list_file_data_from_csv(csv_file_path)
    map_folder_id_to_design(drive_service, file_data_list, drive_folder_id)

    folder_path = get_default_folder_path()
    missing_files = []

    print("\nDownload files")
    for item in file_data_list:
        item_name = f"{item['design']}_{item['endcode']}"
        print(f"Processing {item_name}")
        if not item.get("folder_id"):
            print(f"No folder found for {item_name}")
            continue
        file_data = recursive_find_file_id_in_folder(
            drive_service, item["design"], item["endcode"], item.get("folder_id")
        )
        if file_data:
            download_file_by_id(
                drive_service,
                file_data["id"],
                file_data["name"],
                folder_path,
            )
        else:
            message = f"Not found {item_name}"
            print(message)
            save_error_to_file(
                message,
                folder_path,
                datetime_string=datetime.now().strftime("%d-%m-%Y - %H%M%S"),
            )
            missing_files.append(item_name)

    save_list_to_csv(missing_files, get_default_folder_path(), "missing_files.csv")
