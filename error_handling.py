import os
import csv


def save_error_to_file(message, folder_path, datetime_string):
    current_folder = os.getcwd()
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(
        os.path.join(error_path, f"error_log - {datetime_string}.txt"),
        "a",
        encoding="utf-8",
    ) as e:
        e.write(message)


def save_search_log_to_file(message, folder_path, datetime_string):
    current_folder = os.getcwd()
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(
        os.path.join(error_path, f"search_log - {datetime_string}.txt"), "a"
    ) as e:
        e.write(message)


def save_list_to_csv(items_list: list, destination_folder: str, file_name: str) -> None:
    """
    Saves list of dictionaries to csv file.
    """

    with open(
        os.path.join(destination_folder, file_name), "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.writer(f, delimiter=";")

        writer.writerow(["Design Code"])
        for item in items_list:
            writer.writerow([item])
