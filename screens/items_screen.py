"""Item List View Screen"""

from concurrent.futures import ThreadPoolExecutor
import os
import csv
import logging

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from kivymd.uix.list import MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog, MDDialogSupportingText

from components.forms import TableView
from components.lists import ListOfItems
from components.dialogs import SearchDialog, RenameDialog
from utils import (
    EXPORTS_PATH,
    LIST_PATH,
    ARCHIVES_PATH,
    TEMPLATE_PATH,
    change_screen,
    get_screen_element,
    open_yaml_file,
    sort_files_by_datetime,
)


# Configure logging
logging.basicConfig(level=logging.DEBUG)


class ItemsScreen(Screen):
    """Items Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = None
        self.view = "list"
        self.sort_by = None
        self.columns = []
        self.md_list = MDList(spacing="12dp")
        self.reverse = False

    def on_enter(self, *args):
        """Populates the list Items."""
        self.ids.scroll_area.clear_widgets()  # on changing lists, clear widgets
        self.refresh_view()

    def refresh_view(self):
        """Refreshes the view based on the selected mode."""
        self.ids.scroll_area.clear_widgets()
        if self.view == "list":
            self.populate_list_view(LIST_PATH)
        elif self.view == "table":
            self.populate_table_view()
        elif self.view == "archive":
            self.populate_list_view(ARCHIVES_PATH)

    def sort_dropdown(self, instance):
        """Creates the sort button dropdown values."""
        menu_items = [
            {
                "text": f"{col}",
                "on_release": lambda x=index, y=f"{col}": self.update_sort_btn_text(
                    instance, x, y
                ),
            }
            for index, col in enumerate(self.columns)
        ]
        menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            hor_growth="right",
            position="bottom",
            width_mult=2,
        )
        menu.open()

    def update_sort_btn_text(self, _caller_btn, _index, col):
        """Updates the sort button dropdown value."""
        self.sort_by = col
        self.refresh_view()

    def populate_list_view(self, source: str):
        """Populates the list view."""

        try:
            # Get the directory path and list all files
            directory_path = os.path.join(source, self.ids.list_title.text)
            with os.scandir(directory_path) as entries:
                files = [entry.name for entry in entries if entry.is_file()]
            sorted_files = sort_files_by_datetime(files)

            def process_file(file_path):
                try:
                    yaml_file_path = os.path.join(directory_path, file_path)
                    fl = open_yaml_file(yaml_file_path)
                    first_field = next(iter(fl))

                    item_data = {
                        "text": fl[first_field],
                        "secondary_text": yaml_file_path,
                        "checked": fl.get("checked", False),
                        "source": source,
                    }

                    return item_data
                except IOError as e:
                    logging.error(f"Error processing file {file_path}: {e}")
                    return None

            cond_1 = len(self.md_list.children) != len(sorted_files)
            cond_2 = self.ids.list_title.text != self.title
            cond_3 = self.view == "archive" and source != "ARCHIVES_PATH"
            cond_4 = self.view == "list" and source != "LIST_PATH"

            # Use ThreadPoolExecutor to process files in parallel
            if (cond_1) or (cond_2) or (cond_3) or (cond_4):
                self.md_list.clear_widgets()
                with ThreadPoolExecutor() as executor:
                    items_data = sorted(
                        list(executor.map(process_file, sorted_files)),
                        key=lambda x: x["checked"],
                    )

                # Schedule the update of UI elements on the main thread
                Clock.schedule_once(lambda _: self.update_ui(items_data))
                self.title = self.ids.list_title.text
            else:
                self.ids.scroll_area.add_widget(self.md_list)

        except OSError:
            MDDialog(MDDialogSupportingText(text="No items to show.")).open()

    def update_ui(self, items_data):
        """Updates the UI with processed items data."""

        self.ids.scroll_area.clear_widgets()
        for item_data in items_data:
            item_row = ListOfItems()
            item_row.ids.headline.text = item_data["text"][:40]
            item_row.yaml_path = item_data["secondary_text"]

            if item_data["checked"]:
                item_row.ids.check.icon = "checkbox-marked-outline"
                item_row.ids.headline.text = f"[s]{item_row.ids.headline.text}[/s]"
            else:
                item_row.ids.check.icon = "checkbox-blank-outline"

            self.md_list.add_widget(item_row)
        self.ids.scroll_area.add_widget(self.md_list)

    def populate_table_view(self):
        """Populates the table view."""
        all_dicts = []
        fl = {}

        for file_path in os.listdir(os.path.join(LIST_PATH, self.ids.list_title.text)):
            yaml_file_path = os.path.join(
                LIST_PATH, self.ids.list_title.text, file_path
            )
            fl = open_yaml_file(yaml_file_path)
            all_dicts.append(fl)

        sort_cols = fl.copy()
        self.columns = sort_cols.keys()  # collect column names for dropdown

        if not self.reverse:
            self.reverse = True
        else:
            self.reverse = False

        if self.sort_by:
            all_dicts = sorted(
                all_dicts, key=lambda x: x[self.sort_by], reverse=self.reverse
            )

        table_header = [{"text": str(field)} for field in fl.keys()]
        table_rows = [
            {"text": str(item[field])} for item in all_dicts for field in item.keys()
        ]
        table_data = table_header + table_rows

        try:
            table_view = TableView()
            table_view.data = table_data
            table_view.ids.recycle_grid.cols = len(self.columns)
            self.ids.scroll_area.clear_widgets()
            self.ids.scroll_area.add_widget(table_view)

        except IndexError as e:
            MDDialog(
                MDDialogSupportingText(text=f"Table could not be generated: {e}")
            ).open()

    def menu_open(self, topbar):
        """Opens the field category dropdown menu."""
        menu_items = [
            {
                "text": "List View",
                "on_release": lambda x="list": self.update_view(topbar, x),
            },
            {
                "text": "Table View",
                "on_release": lambda x="table": self.update_view(topbar, x),
            },
            {
                "text": "Archive Archive",
                "on_release": lambda x="archive": self.update_view(topbar, x),
            },
            {
                "text": "Move to Archive/Inbox",
                "on_release": lambda x="archive": self.move_to_archive(),
            },
            {
                "text": "Export Data",
                "on_release": lambda _="export": self.export_data(
                    self.ids.list_title.text
                ),
            },
            {
                "text": "Edit Template",
                "on_release": lambda _="edit": self.go_to_edit_template(),
            },
            {
                "text": "Rename List",
                "on_release": lambda x="rename": self.rename_list(),
            },
        ]
        menu = MDDropdownMenu(
            caller=topbar,
            items=menu_items,
            hor_growth="left",
        )
        menu.open()

    def update_view(self, _, text):
        """Updates the view based on user selection."""
        self.view = text
        self.refresh_view()

    def export_data(self, list_name):
        """Exports list data to csv."""
        data = []
        for file_path in os.listdir(os.path.join(LIST_PATH, self.ids.list_title.text)):
            yaml_file_path = os.path.join(
                LIST_PATH, self.ids.list_title.text, file_path
            )
            fl = open_yaml_file(yaml_file_path)
            fl["File"] = yaml_file_path
            data.append(fl)

        # find the dict item with most amount of fields.
        # this is in case the users manually adds a new field to the template.
        dict_most_keys = max(data, key=len)
        fieldnames = dict_most_keys.keys()

        try:
            with open(
                os.path.join(EXPORTS_PATH, list_name), "w", newline="", encoding="utf-8"
            ) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            MDDialog(
                MDDialogSupportingText(
                    text="Data has been saved in the exports folder."
                )
            ).open()
        except OSError as e:
            MDDialog(MDDialogSupportingText(text=f"Export failed: {e}")).open()

    def new_item(self, item):
        """Moves to the New Template screen"""
        get_screen_element("new_item_screen", "added_items").clear_widgets()
        get_screen_element("new_item_screen", "item_title").text = item
        change_screen("new_item_screen")

    def search(self):
        """Opens the search dialog."""
        dialog = SearchDialog()
        dialog.open_search_dialog(self.md_list)

    def rename(self):
        """Opens the search dialog."""
        dialog = RenameDialog()
        dialog.open_rename_dialog()

    def reset_list(self):
        """Resets the items view."""
        # for table view, ignore reset
        if self.view == "table":
            return
        self.ids.scroll_area.clear_widgets()
        self.refresh_view()

    def go_to_edit_template(self):
        """Displays the edit template view."""
        topbar_title = get_screen_element("edit_template_screen", "list_title")
        topbar_title.text = self.ids.list_title.text
        self.manager.current = "edit_template_screen"

    def move_to_archive(self):
        """Moves item to the archive section."""
        items_to_remove = []
        if self.view == "list":
            items_to_remove = [
                item
                for item in self.md_list.children
                if item.ids.check.icon == "checkbox-marked-outline"
            ]
        elif self.view == "archive":
            items_to_remove = [
                item
                for item in self.md_list.children
                if item.ids.check.icon == "checkbox-blank-outline"
            ]
        for item in items_to_remove:
            item.archive_item()
        self.refresh_view()

    def rename_list(self):
        """Renames the list."""
        dialog = RenameDialog()
        dialog.open_rename_dialog(
            self.ids.list_title, TEMPLATE_PATH, LIST_PATH, ARCHIVES_PATH
        )
