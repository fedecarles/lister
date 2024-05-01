from kivy.utils import platform
from kivymd.app import MDApp
from kivy.metrics import dp
import yaml
import os


def get_screen_element(screen, element_id):
    app = MDApp.get_running_app()
    screen = app.root.get_screen(screen)
    return screen.ids[element_id]


def change_screen(screen):
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


# yaml operations
def open_yaml_file(path):
    with open(path) as file:
        return yaml.safe_load(file)


def save_to_yaml(path, my_dict):
    with open(path, "w") as file:
        yaml.dump(my_dict, file, default_flow_style=False, sort_keys=False)
        print(f"YAML item '{path}' has been created successfully.")


# File operations
def get_folder_list(folder):
    """Returns a list of folders in the 'lists' directory."""
    return [f for f in os.listdir(folder)]


def dicts_to_table(list_of_dicts: list, sort_by: int = 0) -> (list, list):
    """Converts the list of dicts from yaml files into row and column data
    for MDDataTable"""
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
        for k, v in d.items():
            if k not in all_dicts:
                all_dicts[k] = [v]
            else:
                all_dicts[k].append(v)

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
