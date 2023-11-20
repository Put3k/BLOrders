import datetime
import io
import os

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from error_handling import save_error_to_file
from utils import get_default_folder_path


def list_files(drive_service: Resource, drive_folder_id: str) -> list:
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
                print(f'Found file: {file.get("name")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files


def list_folders(drive_service: Resource, drive_folder_id: str) -> list:
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
                print(f'Found folder: {folder.get("name")}')
            folders.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    return folders


def find_folder_id_by_name(
    drive_service: Resource, name: str, root_folder_id: str = None
) -> str:
    """
    Find drive folder id by given name. If root folder id not provided, it will not specify it in query.
    """
    query_parts = {
        "parent": f"'{root_folder_id}' in parents",
        "folder_type": f"mimeType='application/vnd.google-apps.folder'",
        "name_contains": f"name contains '{name}'",
    }

    query = " and ".join([query_parts["name_contains"], query_parts["folder_type"]])
    if root_folder_id:
        query = " and ".join([query_parts["parent"], query])

    folders = []

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
                print(f'Found folder: {folder.get("name")}')
            folders.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    if folders:
        shortest_folder_name = min(folders, key=lambda x: len(x["name"]))
        return shortest_folder_name["id"]


def map_folder_id_to_design(
    drive_service: Resource, file_data_list: list, root_folder_id: str = None
):
    """
    Extend each item dictionary in list by design folder id.
    """
    print("\nMapping folders to designs.")
    previous_item = {}

    for item in file_data_list:
        if previous_item.get("design") == item["design"]:
            design_folder_id = previous_item["folder_id"]
        else:
            design_folder_id = find_folder_id_by_name(
                drive_service=drive_service,
                name=item["design"],
                root_folder_id=root_folder_id,
            )

        if design_folder_id:
            item["folder_id"] = design_folder_id


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


def find_file_in_folder(
    drive_service: Resource, design: str, endcode: str, root_folder_id: str = None
) -> dict:
    """
    Find file by design and endcode. If root folder id is provided it will narrow down search to specified folder.

    :return: dict, {"name": "file_name", "id": "file_id"}
    """
    # TODO: Make function accept list of design names to search for multiple keywords, e.g. KOT_KOLOR_RED_18C.
    #  Design list: ["KOT", "KOLOR", "RED"]

    query_parts = {
        "parent": f"'{root_folder_id}' in parents",
        "image_type": f"mimeType contains 'image/'",
        "design": f"name contains '{design}'",
        "endcode": f"name contains '{endcode}'",
    }

    query = " and ".join(
        [query_parts["design"], query_parts["endcode"], query_parts["image_type"]]
    )
    if root_folder_id:
        query = " and ".join([query_parts["parent"], query])

    found_files = []

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
                print(f'Found file: {folder.get("name")}')
            found_files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

    if found_files:
        shortest_file = min(found_files, key=lambda x: len(x["name"]))
        shortest_file["name"] = shortest_file["name"].replace(" ", "_")
        return shortest_file


def recursive_find_file_id_in_folder(
    drive_service: Resource, design: str, endcode: str, root_folder_id: str = None
):
    file_data = find_file_in_folder(drive_service, design, endcode, root_folder_id)
    if not file_data:
        folders = list_folders(drive_service, root_folder_id)
        for folder in folders:
            file_data = recursive_find_file_id_in_folder(
                drive_service, design, endcode, folder["id"]
            )
            if file_data:
                break

    return file_data
