import os


def save_error_to_file(message, folder_path, datetime_string):
    current_folder = os.getcwd()
    download_path = os.path.join(current_folder, f"BaseLinker - {datetime_string}")
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(os.path.join(error_path, f"error_log - {datetime_string}.txt"), "a") as e:
        e.write(message)


def save_search_log_to_file(message, folder_path, datetime_string):
    current_folder = os.getcwd()
    download_path = os.path.join(current_folder, f"BaseLinker - {datetime_string}")
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(
        os.path.join(error_path, f"search_log - {datetime_string}.txt"), "a"
    ) as e:
        e.write(message)
