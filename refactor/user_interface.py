import PySimpleGUI as sg

from utils.file_handling import is_valid_path


# Labels
baselinker_download_label = sg.Text("BaseLinker - Pobieranie grafik do zamówień", font=("Arial", 12, "bold"))
image_merge_label = sg.Text("Łączenie Grafik", font=("Arial", 12, "bold"))
pdf_merge_label = sg.Text("Łączenie PDF", font=("Arial", 12, "bold"))

# PySimpleGUI spacing definition
sg_space = sg.Text("", size=(1, 1))

# GUI Definiton
layout = [[
    [baselinker_download_label],
    [sg.Text('Wybierz plik CSV z listą zamówień BaseLinker a następnie wciśnij "Kontynuuj" aby pobrać grafiki'
             ' powiązane z zamówieniami.')],
    [
        sg.Text("Plik CSV:"), sg.Input(key="-IN-"),
        sg.FileBrowse(file_types=(("Plik CSV", "*.csv*"),)),
        sg.Button("Pobierz Grafiki"),
        sg.Button("Sprawdź Grafiki")
    ],
    [sg_space],
    [image_merge_label],
    [sg.Text("Wybierz folder z plikami PNG, które mają zostać złączone a nastepnie wybierz folder w którym mają zostać"
             " zapisane połączone pliki PNG.")],
    [sg.Text("Folder Wejściowy:"), sg.Input(key="-ORIGIN_FOLDER_PNG-"), sg.FolderBrowse()],
    [sg.Text("Folder Docelowy:"), sg.Input(key="-DESTINATION_FOLDER_PNG-"), sg.FolderBrowse(), sg.Button("Połącz Grafiki")],
    [sg_space],
    [pdf_merge_label],
    [sg.Text("Wybierz folder z plikami PDF, które mają zostać złączone a następnie wybierz folder w którym ma zostać"
             " zapisany plik PDF.")],
    [sg.Text("Folder Wejściowy:"), sg.Input(key="-ORIGIN_FOLDER_PDF-"), sg.FolderBrowse()],
    [sg.Text("Folder Docelowy:"), sg.Input(key="-DESTINATION_FOLDER_PDF-"), sg.FolderBrowse(), sg.Button("Połącz PDF")],
    [sg.Exit(button_color="tomato", size=(10, 2))],
]]

window = sg.Window("BLOrders", layout)
while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "Exit"):
        break



window.close()
