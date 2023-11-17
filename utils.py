import sys
import os
import csv

from datetime import datetime, timedelta


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_default_folder_path(
    new_folder_name=f"Drive Download - {datetime.now().strftime('%d-%m-%Y - %H%M%S')}",
) -> str:
    destination_path = os.path.join(os.getcwd(), new_folder_name)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    return destination_path


def list_file_data_from_csv(csv_file_path: str) -> list:
    with open(csv_file_path, encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=";")

        file_list = []

        for row in csv_reader:
            file_data = {}
            if len(row) > 0:
                file_components = row[0].split("_")
                file_data["design"] = file_components[0]
                file_data["endcode"] = file_components[1]

                file_list.append(file_data)

    return file_list
