import asyncio
import datetime
import io
import os

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from error_handling import save_error_to_file
from utils import get_default_folder_path


def list_files(drive_service, drive_folder_id: str) -> list:
    """
    List all files inside given drive folder.
    :param drive_service: Google Drive API service
    :param drive_folder_id: Google Drive folder ID
    :return: list
    """

    files = []

    query = f"'{drive_folder_id}' in parents and mimeType contains 'image/'"

    try:
        page_token = None
        while True:
            response = (
                drive_service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files


def find_file_by_design_and_code(
    drive_service, drive_folder_id: str, design: str, endcode: str
) -> dict:
    """
    Return dict that contains file data.
    :param drive_service: Google Drive API service
    :param drive_folder_id: ID of Google Drive folder e.g '52z70URqeIgQ32wq4Ns5lIHaoDsLcFwkT'
    :param design: e.g. CFATH
    :param endcode: e.g. 02C
    :return: {"id": "16z70URqeIgQ32wq4Ns5lIHaoDsLcFwkT", name": "CFATH 02C.png"}
    """
    query = f"'{drive_folder_id}' in parents and name contains '{design}' and name contains '{endcode}'"

    files = []

    try:
        page_token = None
        while True:
            response = (
                drive_service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    return min(files, key=lambda x: len(x["name"]))


def list_folders(drive_service, drive_folder_id: str) -> list:
    """
    List all folders inside given drive folder.
    :param drive_service: Google Drive API service
    :param drive_folder_id: Google Drive folder ID
    :return: list
    """

    folders = []

    query = f"'{drive_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"

    try:
        page_token = None
        while True:
            response = (
                drive_service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for folder in response.get("files", []):
                print(f'Found folder: {folder.get("name")}, {folder.get("id")}')
            folders.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    return folders


def download_file_by_id(
    drive_service, file_id: str, file_name: str, destination_folder: str
) -> None:
    """
    Downloads a file from Google Drive to given destination folder with given file name.
    :param drive_service: Google Drive API service
    :param file_id: Google Drive file ID
    :param file_name: local file name
    :param destination_folder: absolute path to destination folder e.g. E:\\SomeFolderName\\SomeFolderName
    """
    request = drive_service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=file, request=request)
    file_path = os.path.join(destination_folder, file_name)

    done = False

    try:
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% - {file_name}")
    except Exception as e:
        save_error_to_file(
            f"Download Error occurred for file: {file_name}.\nError message: {e}\n",
            get_default_folder_path("Download_errors"),
            datetime.datetime.now().strftime("%d-%m-%Y - %H%M%S"),
        )

    file.seek(0)

    with open(file_path, "wb") as f:
        f.write(file.read())


def find_files_id_from_list(
    drive_service, drive_folder_id, file_data_list, found_files_list
):
    for i, file_data in enumerate(file_data_list):
        query = f"'{drive_folder_id}' in parents and name contains '{file_data['design']}' and name contains '{file_data['endcode']}'"

        results = drive_service.files().list(q=query).execute().get("files", [])

        if results:
            shortest_result = min(results, key=lambda x: len(x["name"]))
            result_data = {
                "id": shortest_result["id"],
                "name": shortest_result["name"].replace(" ", "_"),
            }
            print(f"Found file: {result_data['name']}, {result_data['id']}")
            found_files_list.append(result_data)
            file_data_list.pop(i)
        else:
            pass
            print(f"Not Found: {file_data['design']}_{file_data['endcode']}")
