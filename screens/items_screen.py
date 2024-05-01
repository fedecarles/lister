"""Screen for the List Items View."""

from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import Screen
from components.lists import ListOfItems
from kivymd.uix.list import MDList

from utils import (
    dicts_to_table,
    change_screen,
    get_screen_element,
    open_yaml_file,
    LIST_PATH,
    EXPORTS_PATH,
)
import os
import csv


class ItemsScreen(Screen):
    """Items Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view = "list"
        self.sort_by = None
        self.columns = []

    def on_enter(self):
        """Populates the list Items."""
        self.title = self.ids.topbar.title
        self.refresh_view()

    def refresh_view(self):
        """Refreshes the view based on the selected mode."""
        self.ids.item_list.clear_widgets()
        self.all_items = [f for f in os.listdir(f"{LIST_PATH}{self.title}")]
        if self.view == "list":
            self.populate_list_view()
        elif self.view == "table":
            self.populate_table_view()

    def sort_dropdown(self, caller_btn):
        menu_items = [
            {
                "text": f"{col}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=index, y=f"{col}": self.update_sort_btn_text(
                    caller_btn, x, y
                ),
            }
            for index, col in enumerate(self.columns)
        ]
        menu = MDDropdownMenu(
            caller=caller_btn,
            items=menu_items,
            hor_growth="left",
        )
        menu.open()

    def update_sort_btn_text(self, caller_btn, index, col):
        caller_btn.text = col
        self.sort_by = index
        self.refresh_view()

    def populate_list_view(self):
        """Populates the list view."""
        self.md_list = MDList()

        for file_path in self.all_items:
            yaml_file_path = f"{LIST_PATH}{self.title}/{file_path}"
            fl = open_yaml_file(yaml_file_path)
            first_field = next(iter(fl))
            item_row = ListOfItems(
                text=fl[first_field],
                secondary_text=yaml_file_path,
                secondary_font_style="Icon",
            )
            self.md_list.add_widget(item_row)
            if self.columns is not None:
                self.columns = fl.keys()
        self.ids.item_list.add_widget(self.md_list)

    def populate_table_view(self):
        self.all_dicts = []
        for file_path in self.all_items:
            yaml_file_path = f"{LIST_PATH}{self.title}/{file_path}"
            fl = open_yaml_file(yaml_file_path)
            fl["File"] = yaml_file_path
            self.all_dicts.append(fl)

        header_data, row_data = dicts_to_table(self.all_dicts, self.sort_by)

        self.data_table = MDDataTable(
            column_data=header_data,
            row_data=row_data,
            use_pagination=True,
            elevation=2,
            size_hint=(1, 0.9),
        )
        self.data_table.bind(on_row_press=self.on_row_press)
        self.ids.item_list.add_widget(self.data_table)

    def menu_open(self, topbar):
        """Opens the field category dropdown menu."""
        menu_items = [
            {
                "text": "List View",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="list": self.update_view(topbar, x),
            },
            {
                "text": "Table View",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="table": self.update_view(topbar, x),
            },
            {
                "text": "Export",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Export": self.export_data(self.title),
            },
        ]
        menu = MDDropdownMenu(
            caller=topbar,
            items=menu_items,
            hor_growth="left",
        )
        menu.open()

    def update_view(self, topbar, text):
        """Updates the view based on user selection."""
        self.view = text
        self.refresh_view()

    def export_data(self, list_name):
        """Exports list data to csv."""
        data = []
        for file_path in self.all_items:
            yaml_file_path = f"{LIST_PATH}{list_name}/{file_path}"
            fl = open_yaml_file(yaml_file_path)
            fl["File"] = yaml_file_path
            data.append(fl)

        fieldnames = data[0].keys()
        with open(f"{EXPORTS_PATH}{list_name}", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def on_row_press(self, table, row):
        """Update screen title."""
        start_index, end_index = row.table.recycle_data[row.index]["range"]
        file_path = row.table.recycle_data[end_index]["text"]
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = file_path.replace(".yaml", "")
        change_screen("view_item_screen")

    def new_item(self, item):
        """Moves to the New Template screen"""
        get_screen_element("new_item_screen", "added_items").clear_widgets()
        get_screen_element("new_item_screen", "item_title").text = item
        change_screen("new_item_screen")
