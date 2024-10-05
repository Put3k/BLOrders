import json

from utils import resource_path

CONTRACTOR = None

SMALL_SIZES = ["3-4", "5-6", "7-8"]
PRODUCTS = ["LEZA", "KOSZ", "POD", "KB_ZW", "KB_MAG", "KB_FUN", "KB_GOLD"]

DRIVES_PATH = resource_path("drive_folders_destination.json")
with open(DRIVES_PATH) as f:
    drive_dest = json.load(f)

    WHITE_SHIRT_FOLDER_ID = drive_dest.get("WHITE_SHIRT_FOLDER_ID")
    WHITE_CUP_FOLDER_ID = drive_dest.get("WHITE_CUP_FOLDER_ID")
    BLACK_SHIRT_FOLDER_ID = drive_dest.get("BLACK_SHIRT_FOLDER_ID")
    BLACK_CUP_FOLDER_ID = drive_dest.get("BLACK_CUP_FOLDER_ID")
    BLACK_HALFTONE_SHIRT_FOLDER_ID = drive_dest.get("BLACK_HALFTONE_SHIRT_FOLDER_ID")
    GOLD_CUP_FOLDER_ID = drive_dest.get("GOLD_CUP_FOLDER_ID")
    DOWNLOAD_DESIGNS_FOLDER_ID = drive_dest.get("DOWNLOAD_DESIGNS_FOLDER_ID")

    API_NAME = drive_dest.get("API_NAME")
    API_VERSION = drive_dest.get("API_VERSION")
    SCOPES = drive_dest.get("SCOPES")
