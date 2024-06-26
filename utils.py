"""Helper and utility functions."""

import os
import time
import logging
from datetime import datetime

import yaml

from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox

from components.dialogs import SearchDialog
from components.forms import NewItemForm

# File storage paths
if platform == "android":
    # pylint: disable=E0401
    # pylint: disable=C0415
    from android.storage import primary_external_storage_path

    STORAGE_PATH = primary_external_storage_path()
else:
    STORAGE_PATH = "."
DOCUMENTS_PATH = os.path.join(STORAGE_PATH, "Documents/Lister")
LIST_PATH = os.path.join(DOCUMENTS_PATH, "lists/")
TEMPLATE_PATH = os.path.join(DOCUMENTS_PATH, "templates/")
EXPORTS_PATH = os.path.join(DOCUMENTS_PATH, "exports/")
ASSETS_PATH = os.path.join("assets/")
ARCHIVES_PATH = os.path.join(DOCUMENTS_PATH, "archives/")


# logging
def log_runtime(func):
    """Prints our the function runtime."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        runtime = end_time - start_time
        logging.info("Function %s executed in %s seconds", func.__name__, runtime)
        return result

    return wrapper


# Screen operations
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


# yaml files operations
def sort_files_by_datetime(file_paths):
    """Sort the yaml files by date suffix."""

    def extract_datetime(file_path):
        filename = os.path.basename(file_path)
        date_string = filename.split("_")[-1].split(".")[0]
        return datetime.strptime(date_string, "%Y-%m-%d %H%M%S")

    sorted_file_paths = sorted(file_paths, key=extract_datetime, reverse=True)
    return sorted_file_paths


def open_yaml_file(path: str) -> dict:
    """
    Summary:
    Reads a yaml filed ans stores it as a dict.

    Parameters:
    - path (str): A file path.

    Returns:
    A python dict.
    """
    with open(path, encoding="utf-8") as file:
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


def list_items_to_dict(all_list_items: MDList) -> dict:
    """
    Summary:
    Returns a dict from an MDList object.

    Parameters:
    - all_list_items (MDList): An MDList.

    Returns:
    A dict of MDList items titles.
    """
    mapped_values = {}
    for item in all_list_items:
        if isinstance(item, NewItemForm):
            for child in item.children:
                if isinstance(child, MDTextField):
                    mapped_values[child.children[0].text] = child.text
                if isinstance(child, MDCheckbox):
                    mapped_values["checked"] = child.active
        else:
            if isinstance(item, MDTextField):
                mapped_values[item.children[0].text] = item.text
            if isinstance(item, MDCheckbox):
                mapped_values["checked"] = item.active

    mapped_values = dict(reversed(mapped_values.items()))
    return mapped_values


# Dialog operations
def create_dialog(_content, _cancel_fn, _callback_fn) -> MDDialog:
    """
    Summary:
    Returns an MDDialog.

    Parameters:
    - content (custom): A custom Dialog class.
    - cancel_fn (fn): A close dialog function.
    - callback_fn (fn): A callback function.

    Returns:
    An MDDialog
    """
    return SearchDialog
