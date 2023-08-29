from pathlib import Path

import PySimpleGUI as sg

from DriveAPI import main
from ImageEdit import merge
from PDFMerge import merge_pdf


def is_valid_path(filepath):
    if filepath and Path(filepath).exists():
        return True
    sg.popup_error("Ścieżka pliku jest niepoprawna")
    return False


# ------ GUI Definition ------ #

csv_label = sg.Text("BaseLinker - Pobieranie grafik do zamówień", font=("Arial", 12, "bold"))
image_edit_label = sg.Text("Łączenie Grafik", font=("Arial", 12, "bold"))
pdf_merge_label = sg.Text("Łączenie PDF", font=("Arial", 12, "bold"))

layout = [[
    [csv_label],
    [sg.Text('Wybierz plik CSV z listą zamówień BaseLinker a następnie wciśnij "Kontynuuj" aby pobrać grafiki powiązane z zamówieniami.')],
    [sg.Text("Plik CSV:"), sg.Input(key="-IN-"), sg.FileBrowse(file_types=(("Plik CSV", "*.csv*"),)), sg.Button("Pobierz Grafiki")],
    [sg.Text("", size=(1, 1))],     #Spacing
    [image_edit_label],
    [sg.Text("Wybierz folder z plikami PNG, które mają zostać złączone a nastepnie wybierz folder w którym mają zostać zapisane połączone pliki PNG.")],
    [sg.Text("Folder Wejściowy:"), sg.Input(key="-ORIGIN_FOLDER_PNG-"), sg.FolderBrowse()],
    [sg.Text("Folder Docelowy:"), sg.Input(key="-DESTINATION_FOLDER_PNG-"), sg.FolderBrowse(), sg.Button("Połącz Grafiki")],
    [sg.Text("", size=(1, 1))],
    [pdf_merge_label],
    [sg.Text("Wybierz folder z plikami PDF, które mają zostać złączone a następnie wybierz folder w którym ma zostać zapisany plik PDF.")],
    [sg.Text("Folder Wejściowy:"), sg.Input(key="-ORIGIN_FOLDER_PDF-"), sg.FolderBrowse()],
    [sg.Text("Folder Docelowy:"), sg.Input(key="-DESTINATION_FOLDER_PDF-"), sg.FolderBrowse(), sg.Button("Połącz PDF")],
    [sg.Exit(button_color="tomato", size=(10, 2))],
]]

window = sg.Window("BLOrders", layout)

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "Pobierz Grafiki":
        if is_valid_path(values["-IN-"]):
            order_count, order_download_count = main(values["-IN-"])
            missing_files = order_count - order_download_count
            if order_count and order_download_count:
                sg.popup_no_titlebar(f"""Ukończono pobieranie.\n\nLiczba zamówień: {order_count}\nPobranych plików: {order_download_count}\nBrakujących plików: {missing_files}""")
                continue
    if event == "Połącz Grafiki":
        if is_valid_path(values["-ORIGIN_FOLDER_PNG-"]) and is_valid_path(values["-DESTINATION_FOLDER_PNG-"]):
            designs_count = merge(values["-ORIGIN_FOLDER_PNG-"], values["-DESTINATION_FOLDER_PNG-"])
            if designs_count:
                sg.popup_no_titlebar(f"""Połączono {designs_count} grafik.""")
                continue
    if event == "Połącz PDF":
        if is_valid_path(values["-ORIGIN_FOLDER_PDF-"]) and is_valid_path(values["-DESTINATION_FOLDER_PDF-"]):
            result, designs_count = merge_pdf(values["-ORIGIN_FOLDER_PDF-"], values["-DESTINATION_FOLDER_PDF-"])
        if result:
            sg.popup_no_titlebar(f"""Połączono {designs_count} plików PDF.""")
window.close()