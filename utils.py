"""Helper and utility functions."""

import os
import yaml
from datetime import datetime

from kivy.metrics import dp
from kivy.utils import platform
from kivymd.app import MDApp


def get_screen_element(screen: str, element_id: str):
    """
    Summary:
    Gets an element by id from a specified screen.

    Parameters:
    - screen (str): A kivy Screen name.
    - element (str): A kivy element id.

    Returns:
    Kivy Element: A Kivy element.
    """
    app = MDApp.get_running_app()
    screen = app.root.get_screen(screen)
    return screen.ids[element_id]


def change_screen(screen: str) -> None:
    """
    Summary:
    Switches to a specified Kivy Screen.

    Parameters:
    - screen (str): A kivy Screen name.

    Returns:
    None
    """

    app = MDApp.get_running_app()
    app.root.current = screen


# File storage paths
if platform == "android":
    from android.storage import primary_external_storage_path

    STORAGE_PATH = primary_external_storage_path()
else:
    STORAGE_PATH = "."
DOCUMENTS_PATH = os.path.join(STORAGE_PATH, "Documents/Lister")
LIST_PATH = os.path.join(DOCUMENTS_PATH, "lists/")
TEMPLATE_PATH = os.path.join(DOCUMENTS_PATH, "templates/")
EXPORTS_PATH = os.path.join(DOCUMENTS_PATH, "exports/")
ASSETS_PATH = os.path.join("assets/")


def sort_files_by_datetime(file_paths):
    def extract_datetime(file_path):
        filename = os.path.basename(file_path)
        date_string = filename.split("_")[-1].split(".")[0]
        return datetime.strptime(date_string, "%Y-%m-%d %H%M%S")

    sorted_file_paths = sorted(file_paths, key=extract_datetime, reverse=True)
    return sorted_file_paths


# yaml operations
def open_yaml_file(path: str) -> dict:
    """
    Summary:
    Reads a yaml filed ans stores it as a dict.

    Parameters:
    - path (str): A file path.

    Returns:
    A python dict.
    """
    with open(path) as file:
        return yaml.safe_load(file)


def save_to_yaml(path, my_dict) -> None:
    """
    Summary:
    Writes a yaml file from a python dict.

    Parameters:
    - path (str): A file path.
    - my_dict (dict): A python dict.

    Returns:
    None
    """
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(my_dict, file, default_flow_style=False, sort_keys=False)
        print(f"YAML item '{path}' has been created successfully.")


# File operations
def get_folder_list(folder: str) -> list:
    """
    Summary:
    Returns a list of folders in the 'lists' directory.

    Parameters:
    - folder (str): A folder path.

    Returns:
    A list a folder names.
    """
    return list(os.listdir(folder))


def dicts_to_table(list_of_dicts: list, sort_by: int = 0) -> tuple[list, list]:
    """
    Summary:
    Converts the list of dicts from yaml files into row and column data
    for MDDataTable

    Parameters:
    - list_of_dicts (list[dict]): A list of dictionaries.
    - sort_by (int): An integer.

    Returns:
    A tuple with the header and row data for the MDDataTable.
    """

    all_dicts = {}
    dps_all = []
    header_data = []
    row_data = []
    for d in list_of_dicts:
        # calculate dp size
        dps_row = [max(20, len(col * 2)) for col in d.values()]
        dps_all.append(dps_row)

        # For sorting purposes, convert the list of dicts to a
        # single dict where the data columns are a key.
        for key, value in d.items():
            if key not in all_dicts:
                all_dicts[key] = [value]
            else:
                all_dicts[key].append(value)

    # Convert the dictionary to MDDataTable header/row formats.
    list_length = len(next(iter(all_dicts.values())))
    for i in range(list_length):
        tuple_data = tuple(all_dicts[key][i] for key in all_dicts)
        row_data.append(tuple_data)

    dps = [max(dps) for dps in zip(*dps_all)]

    for index, d in enumerate(all_dicts.keys()):
        header_data.append((d, dp(dps[index])))

    # Sort the dictionary
    if sort_by is not None:
        row_data = sorted(
            zip(*[all_dicts[col] for col in all_dicts.keys()]),
            key=lambda x: x[sort_by],
        )

    return header_data, row_data
