"""Item List View Screen"""

import csv
import os

from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.datatables import MDDataTable

from components.lists import ListOfItems
from components.dialogs import SearchDialog
from utils import (
    EXPORTS_PATH,
    LIST_PATH,
    change_screen,
    dicts_to_table,
    get_screen_element,
    open_yaml_file,
    sort_files_by_datetime,
)


class ItemsScreen(Screen):
    """Items Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = None
        self.view = "list"
        self.sort_by = None
        self.columns = []
        self.md_list = None
        self.dialog = None

    def on_enter(self):
        """Populates the list Items."""
        self.title = self.ids.topbar.title
        self.refresh_view()

    def refresh_view(self):
        """Refreshes the view based on the selected mode."""
        self.ids.item_list.clear_widgets()
        if self.view == "list":
            self.populate_list_view()
        elif self.view == "table":
            self.populate_table_view()

    def sort_dropdown(self, instance):
        """Creats the sort button dropdown values."""
        menu_items = [
            {
                "text": f"{col}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=index, y=f"{col}": self.update_sort_btn_text(
                    instance, x, y
                ),
            }
            for index, col in enumerate(self.columns)
        ]
        menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            hor_growth="left",
            position="bottom",
            width_mult=2,
        )
        menu.open()

    def update_sort_btn_text(self, caller_btn, index, col):
        """Updates the sort button dropdown value."""
        caller_btn.text = col
        self.sort_by = index
        self.refresh_view()

    def populate_list_view(self):
        """Populates the list view."""
        self.md_list = MDList()

        sorted_files = sort_files_by_datetime(
            os.listdir(os.path.join(LIST_PATH, self.title))
        )
        for file_path in sorted_files:
            yaml_file_path = os.path.join(LIST_PATH, self.title, file_path)
            fl = open_yaml_file(yaml_file_path)
            first_field = next(iter(fl))
            item_row = ListOfItems(
                text=fl[first_field],
                secondary_text=yaml_file_path,
                secondary_font_style="Icon",
            )
            self.md_list.add_widget(item_row, index=0)
            if not self.columns:
                self.columns = fl.keys()
        self.ids.item_list.add_widget(self.md_list, index=0)

    def populate_table_view(self):
        """Populates the table view."""
        all_dicts = []

        sort_btn = MDFillRoundFlatIconButton(
            text="Sort",
            pos_hint={"center_x": 0.5, "center_y": 0.9},
            icon="sort",
            on_release=lambda x: self.sort_dropdown(x),
        )

        self.add_widget(sort_btn)

        for file_path in os.listdir(os.path.join(LIST_PATH, self.title)):
            yaml_file_path = os.path.join(LIST_PATH, self.title, file_path)
            fl = open_yaml_file(yaml_file_path)
            fl["File"] = yaml_file_path
            all_dicts.append(fl)

        try:
            header_data, row_data = dicts_to_table(all_dicts, self.sort_by)
            data_table = MDDataTable(
                column_data=header_data,
                row_data=row_data,
                use_pagination=True,
                size_hint=(1, 0.8),
            )
            data_table.bind(on_row_press=self.on_row_press)
            self.ids.item_list.add_widget(data_table)
        except IndexError as e:
            MDDialog(text=f"Table could not be generated: {e}").open()

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
                "on_release": lambda _="export": self.export_data(self.title),
            },
            {
                "text": "Edit Template",
                "viewclass": "OneLineListItem",
                "on_release": lambda _="edit": self.go_to_edit_template(),
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
        for file_path in os.listdir(os.path.join(LIST_PATH, self.title)):
            yaml_file_path = os.path.join(LIST_PATH, self.title, file_path)
            fl = open_yaml_file(yaml_file_path)
            fl["File"] = yaml_file_path
            data.append(fl)

        # find the dict item with most amount of fields.
        # this is in case the users manually adds a new field to the template.
        dict_most_keys = max(data, key=lambda x: len(x))
        fieldnames = dict_most_keys.keys()

        try:
            with open(
                os.path.join(EXPORTS_PATH, list_name), "w", newline="", encoding="utf-8"
            ) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            MDDialog(text="Data has been saved in the exports folder.").open()
        except OSError as e:
            MDDialog(text=f"Export failed: {e}").open()

    def on_row_press(self, _, row):
        """Update screen title."""
        _, end_index = row.table.recycle_data[row.index]["range"]
        file_path = row.table.recycle_data[end_index]["text"]
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = file_path.replace(".yaml", "")
        change_screen("view_item_screen")

    def new_item(self, item):
        """Moves to the New Template screen"""
        get_screen_element("new_item_screen", "added_items").clear_widgets()
        get_screen_element("new_item_screen", "item_title").text = item
        change_screen("new_item_screen")

    def open_search_dialog(self):
        """Opens the search dialog."""

        if self.view == "table":
            MDDialog(text="Search only works on list view.").open()
            return

        def search_callback(_):
            search_text = self.dialog.content_cls.ids.search_field.text
            search_results = [
                item for item in self.md_list.children if search_text in item.text
            ]

            if search_results:
                self.md_list.clear_widgets()
                for item in search_results:
                    self.md_list.add_widget(item)

            self.dialog.dismiss()

        def dismiss_dialog(_):
            self.dialog.dismiss()

        self.dialog = MDDialog(
            type="custom",
            content_cls=SearchDialog(),
            buttons=[
                MDRaisedButton(
                    text="Cancel", md_bg_color="red", on_release=dismiss_dialog
                ),
                MDRaisedButton(text="Search", on_release=search_callback),
            ],
        )
        self.dialog.open()

    def reset_list(self):
        """Resets the items view."""

        # for table view, ignore reset
        if self.view == "table":
            return

        self.ids.item_list.remove_widget(self.md_list)
        self.populate_list_view()

    def go_to_edit_template(self):
        """Displays the edit template view."""
        topbar = get_screen_element("edit_template_screen", "topbar")
        topbar.title = self.ids.topbar.title
        self.manager.current = "edit_template_screen"
