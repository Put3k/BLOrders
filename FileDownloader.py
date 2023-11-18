import csv
import time

from datetime import timedelta

from Google import create_service, get_credentials
from DriveAPI import list_folders, download_file_by_id, find_files_id_from_list
from utils import list_file_data_from_csv


def list_files_and_folders(drive_service, drive_folder_id):
    files = (
        drive_service.files()
        .list(q=f"mimeType contains 'image/'")
        .execute()
        .get("files", [])
    )
    folders = (
        drive_service.files()
        .list(q=f"mimeType='application/vnd.google-apps.folder'")
        .execute()
        .get("files", [])
    )

    return files, folders


def download_all_drive_traverse(
    drive_service,
    drive_folder_id,
    destination_folder,
):
    files, folders = list_files_and_folders(drive_service, drive_folder_id)

    if files:
        for file in files:
            download_file_by_id(
                drive_service,
                file_id=file["id"],
                file_name=file["name"].replace(" ", "_"),
                destination_folder=destination_folder,
            )

    if folders:
        for folder in folders:
            download_all_drive_traverse(drive_service, folder["id"], destination_folder)


def download_all_files():
    drive_service = create_service(
        get_credentials(), "drive", "v3", ["https://www.googleapis.com/auth/drive"]
    )

    start_time = time.time()
    download_all_drive_traverse(
        drive_service,
        drive_folder_id="1KHn6jTOiGxO5DRekWnLRM_SyxCNiQ-_3",
        destination_folder=r"E:\WinLuk\GRAFIKI_WL",
    )
    end_time = time.time()
    process_time = str(timedelta(seconds=(end_time - start_time))).split(":")
    print(
        "Download finished in ",
        process_time[0],
        "Hours",
        process_time[1],
        "Minutes",
        process_time[2],
        "Seconds",
    )


def recursive_download_listed_files(
    drive_service, drive_folder_id: str, file_data_list, found_files_list
) -> list:
    find_files_id_from_list(
        drive_service, drive_folder_id, file_data_list, found_files_list
    )

    folders = list_folders(drive_service, drive_folder_id)

    if folders:
        for folder in folders:
            recursive_download_listed_files(
                drive_service=drive_service,
                drive_folder_id=folder["id"],
                file_data_list=file_data_list,
                found_files_list=found_files_list,
            )


def download_listed_files(csv_file_path: str, drive_folder_id: str):
    drive_service = create_service(
        get_credentials(), "drive", "v3", ["https://www.googleapis.com/auth/drive"]
    )

    file_data_list = list_file_data_from_csv(csv_file_path)
    found_files_list = []
    recursive_download_listed_files(
        drive_service, drive_folder_id, file_data_list, found_files_list
    )

    print(file_data_list)
    print(found_files_list)


if __name__ == "__main__":
    download_listed_files(
        csv_file_path=r"E:\\WinShirt\\BLOrders\\lista_brakujacych_grafik — kopia.csv",
        drive_folder_id="1KHn6jTOiGxO5DRekWnLRM_SyxCNiQ-_3",
    )
