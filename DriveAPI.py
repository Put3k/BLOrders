import io
import os

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload



def list_files(drive_service, drive_folder_id: str):

    files = []

    query = f"'{drive_folder_id}' in parents and mimeType='image/jpeg'"

    try:
        files = []
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


def list_folders(drive_service, drive_folder_id: str):
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
            for file in response.get("files", []):
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            folders.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    return folders


def download_file(drive_service,
                  file_id: str,
                  file_name: str,
                  destination_folder: str):
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
            print(F'Download {int(status.progress() * 100)}% - {file_name}')
    except Exception as e:
        save_error_to_file(f"Download Error occurred for file: {file_name}.\nError message: {e}\n")

    file.seek(0)

    with open(file_path, 'wb') as f:
        f.write(file.read())