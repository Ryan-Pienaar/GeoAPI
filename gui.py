import PySimpleGUI as sg
import os.path
from functions import *

# !---------------------------------------GUI--------------------------------------------------!

def startGUI():
    file_list_column = [
        [
            sg.Text("File"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            ),
            sg.Button("Parse Locations"),
            sg.Button("Score Data"),
        ],
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column),
        ]
    ]

    window = sg.Window("GeoAPI (Version 1.2)", layout)

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith(".xlsx")
            ]
            window["-FILE LIST-"].update(fnames)

        if event == "Parse Locations":
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                checkLocations(filename)
                sg.Popup("Done parsing locations. Select another file to be parsed", title="Finished")
            except:
                sg.Popup("Please select a file to be parsed", title="Error")

        if event == "Score Data":
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                score(filename)
                sg.Popup("Done scoring data. Select another file to be scored", title="Finished")
            except:
                sg.Popup("Please select a file with data to be scored", title="Error")

    window.close()