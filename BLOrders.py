from pathlib import Path

import PySimpleGUI as sg

from OrderHandler import main
from ImageEdit import merge
from PDFMerge import merge_pdf


def is_valid_path(filepath):
    if filepath and Path(filepath).exists():
        return True
    sg.popup_error("Ścieżka pliku jest niepoprawna")
    return False


# ------ GUI Definition ------ #

csv_label = sg.Text(
    "BaseLinker - Pobieranie grafik do zamówień", font=("Arial", 12, "bold")
)
image_edit_label = sg.Text("Łączenie Grafik", font=("Arial", 12, "bold"))
pdf_merge_label = sg.Text("Łączenie PDF", font=("Arial", 12, "bold"))


def custom_popup(message, data_to_copy, bg_color="red", text_color="white"):
    layout = [
        [sg.Text(message, background_color=bg_color, text_color=text_color)],
        [
            sg.Multiline(
                default_text=data_to_copy,
                size=(40, 10),
                key="-DATA-",
                disabled=True,
                autoscroll=False,
                background_color='white',
                text_color='black',
                border_width=1,
            )
        ],
        [sg.Button("OK", key="-OK-", button_color=(text_color, bg_color))],
    ]

    # Tworzenie okna z globalnym tłem
    window = sg.Window(
        "Popup", layout, modal=True, finalize=True, background_color=bg_color
    )

    # Ustawienie fokusu i zaznaczenia tekstu w multiline (opcjonalnie)
    window["-DATA-"].Widget.config(state="normal")  # Tymczasowe odblokowanie
    # Zaznaczenie całego tekstu
    window["-DATA-"].Widget.tag_add("sel", "1.0", "end")
    window["-DATA-"].Widget.config(state="disabled")  # Ponowne zablokowanie

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "-OK-"):
            break

    window.close()


layout = [
    [
        [csv_label],
        [
            sg.Text(
                'Wybierz plik CSV z listą zamówień BaseLinker a następnie wciśnij "Kontynuuj" aby pobrać grafiki powiązane z zamówieniami.'
            )
        ],
        [
            sg.Text("Plik CSV:"),
            sg.Input(key="-IN-"),
            sg.FileBrowse(file_types=(("Plik CSV", "*.csv*"),)),
            sg.Button("Pobierz Grafiki"),
            sg.Button("Sprawdź Grafiki"),
        ],
        [sg.Text("", size=(1, 1))],  # Spacing
        [image_edit_label],
        [
            sg.Text(
                "Wybierz folder z plikami PNG, które mają zostać złączone a nastepnie wybierz folder w którym mają zostać zapisane połączone pliki PNG."
            )
        ],
        [
            sg.Text("Folder Wejściowy:"),
            sg.Input(key="-ORIGIN_FOLDER_PNG-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Text("Folder Docelowy:"),
            sg.Input(key="-DESTINATION_FOLDER_PNG-"),
            sg.FolderBrowse(),
            sg.Button("Połącz Grafiki"),
        ],
        [sg.Text("", size=(1, 1))],
        [pdf_merge_label],
        [
            sg.Text(
                "Wybierz folder z plikami PDF, które mają zostać złączone a następnie wybierz folder w którym ma zostać zapisany plik PDF."
            )
        ],
        [
            sg.Text("Folder Wejściowy:"),
            sg.Input(key="-ORIGIN_FOLDER_PDF-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Text("Folder Docelowy:"),
            sg.Input(key="-DESTINATION_FOLDER_PDF-"),
            sg.FolderBrowse(),
            sg.Button("Połącz PDF"),
        ],
        [sg.Exit(button_color="tomato", size=(10, 2))],
    ]
]

window = sg.Window("BLOrders", layout)

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    if event == "Pobierz Grafiki" or event == "Sprawdź Grafiki":
        if is_valid_path(values["-IN-"]):
            if event == "Pobierz Grafiki":
                download_files = True
            elif event == "Sprawdź Grafiki":
                download_files = False
            (
                order_count,
                order_download_count,
                order_file_exists_count,
                missing_files_set,
            ) = main(values["-IN-"], download_files=download_files)
            if download_files:
                missing_files = order_count - order_download_count
            else:
                missing_files = order_count - order_file_exists_count

            missing_files_log = "\n".join(missing_files_set)

            if order_count:
                if order_download_count and download_files:
                    popup_msg = f"Ukończono pobieranie.\n\nLiczba zamówień: {order_count}\nPobranych plików: {order_download_count}\nBrakujących plików: {missing_files}"
                elif order_file_exists_count:
                    popup_msg = f"Ukończono sprawdzanie plików.\n\nLiczba zamówień: {order_count}\nZnalezionych plików: {order_file_exists_count}\nBrakujących plików: {missing_files}"
                else:
                    popup_msg = f"Znaleziono {order_count} zamówień ale nie znaleziono żadnego plików."

            else:
                popup_msg = "Nie znaleziono zamówień."
            custom_popup(popup_msg, missing_files_log)
            continue

    if event == "Połącz Grafiki":
        if is_valid_path(values["-ORIGIN_FOLDER_PNG-"]) and is_valid_path(
            values["-DESTINATION_FOLDER_PNG-"]
        ):
            designs_count = merge(
                values["-ORIGIN_FOLDER_PNG-"], values["-DESTINATION_FOLDER_PNG-"]
            )
            if designs_count:
                sg.popup_no_titlebar(f"""Połączono {designs_count} grafik.""")
                continue

    if event == "Połącz PDF":
        if is_valid_path(values["-ORIGIN_FOLDER_PDF-"]) and is_valid_path(
            values["-DESTINATION_FOLDER_PDF-"]
        ):
            result, designs_count = merge_pdf(
                values["-ORIGIN_FOLDER_PDF-"], values["-DESTINATION_FOLDER_PDF-"]
            )
        if result:
            sg.popup_no_titlebar(f"""Połączono {designs_count} plików PDF.""")

window.close()
