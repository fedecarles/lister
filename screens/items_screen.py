"""Item List View Screen"""

from concurrent.futures import ThreadPoolExecutor
import logging
import csv
import os

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemHeadlineText,
)
from kivymd.uix.dialog import MDDialog, MDDialogSupportingText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.recycleview import MDRecycleView

# from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDIconButton


from components.lists import ListOfItems, TableView
from components.dialogs import SearchDialog
from utils import (
    EXPORTS_PATH,
    LIST_PATH,
    ARCHIVES_PATH,
    change_screen,
    dicts_to_table,
    get_screen_element,
    open_yaml_file,
    sort_files_by_datetime,
    create_dialog,
    log_runtime,
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
        self.dialog = None
        self.counts = 0
        self.md_list = MDList()

    @log_runtime
    def on_enter(self, *args):
        """Populates the list Items."""
        if self.title != self.ids.topbar.title:
            self.ids.scroll_area.clear_widgets()  # on changing lists, clear widgets
            self.title = self.ids.topbar.title
        self.refresh_view()

    @log_runtime
    def refresh_view(self):
        """Refreshes the view based on the selected mode."""
        app = MDApp.get_running_app()
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

    @log_runtime
    def update_sort_btn_text(self, caller_btn, index, col):
        """Updates the sort button dropdown value."""
        caller_btn.text = col
        self.sort_by = index
        self.refresh_view()

    @log_runtime
    def populate_list_view(self, source: str):
        """Populates the list view."""
        self.ids.sort_layout.clear_widgets()
        self.ids.scroll_area.clear_widgets()

        try:
            # Get the directory path and list all files
            directory_path = os.path.join(source, self.title)
            # files = os.listdir(directory_path)
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

            # Use ThreadPoolExecutor to process files in parallel
            if self.counts != len(sorted_files):
                self.md_list.clear_widgets()
                with ThreadPoolExecutor() as executor:
                    items_data = sorted(
                        list(executor.map(process_file, sorted_files)),
                        key=lambda x: x["checked"],
                    )

                # Schedule the update of UI elements on the main thread
                Clock.schedule_once(lambda _: self.update_ui(items_data))
            else:
                self.ids.scroll_area.add_widget(self.md_list)

        except OSError:
            MDDialog(MDDialogSupportingText(text="No items to show.")).open()

    @log_runtime
    def update_ui(self, items_data):
        """Updates the UI with processed items data."""

        self.ids.scroll_area.clear_widgets()
        for item_data in items_data:
            item_row = ListOfItems()
            item_row.ids.headline.text = item_data["text"][:20]
            item_row.yaml_path = item_data["secondary_text"]

            # Ensure backward compatibility by adding 'checked' field if missing
            if item_data["checked"]:
                item_row.ids.check.icon = "checkbox-marked-outline"
                item_row.text = f"[s]{item_row.ids.headline.text}[/s]"
            else:
                item_row.ids.check.icon = "checkbox-blank-outline"

            ## Change inbox/archive icons
            if item_data["source"] == ARCHIVES_PATH:
                item_row.ids.archive_btn.icon = "inbox-outline"
                item_row.ids.archive_btn.text_color = [0, 1, 0, 1]
            else:
                item_row.ids.archive_btn.icon = "archive-outline"
                item_row.ids.archive_btn.text_color = [50, 50, 0, 1]

            self.md_list.add_widget(item_row)
        self.counts = len(self.md_list.children)
        self.ids.scroll_area.add_widget(self.md_list)

    @log_runtime
    def populate_table_view(self):
        """Populates the table view."""
        all_dicts = []
        fl = {}

        if not self.ids.sort_layout.children:
            sort_btn = MDIconButton(
                text="Sort",
                icon="sort",
                on_release=self.sort_dropdown,
            )
            self.ids.sort_layout.add_widget(sort_btn)

        for file_path in os.listdir(os.path.join(LIST_PATH, self.title)):
            yaml_file_path = os.path.join(LIST_PATH, self.title, file_path)
            fl = open_yaml_file(yaml_file_path)
            # fl["File"] = yaml_file_path
            all_dicts.append(fl)

        table_header = [{"text": str(field)} for field in fl.keys()]
        table_rows = [
            {"text": str(item[field])} for item in all_dicts for field in item.keys()
        ]
        table_data = table_header + table_rows

        try:
            table_view = TableView()
            table_view.data = table_data
            table_view.ids.recycle_grid.cols = len(fl.keys())
            self.ids.scroll_area.clear_widgets()
            self.ids.scroll_area.add_widget(table_view)

        except IndexError as e:
            MDDialog(
                MDDialogSupportingText(text=f"Table could not be generated: {e}")
            ).open()

    @log_runtime
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
                "text": "Export Data",
                "on_release": lambda _="export": self.export_data(self.title),
            },
            {
                "text": "Edit Template",
                "on_release": lambda _="edit": self.go_to_edit_template(),
            },
            {
                "text": "Archive",
                "on_release": lambda x="archive": self.update_view(topbar, x),
            },
        ]
        menu = MDDropdownMenu(
            caller=topbar,
            items=menu_items,
            hor_growth="left",
        )
        menu.open()

    @log_runtime
    def update_view(self, _, text):
        """Updates the view based on user selection."""
        self.view = text
        self.refresh_view()

    @log_runtime
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

    def on_row_press(self, _, row):
        """Update screen title."""
        _, end_index = row.table.recycle_data[row.index]["range"]
        file_path = row.table.recycle_data[end_index]["text"]
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = file_path.replace(".yaml", "")
        change_screen("view_item_screen")

    @log_runtime
    def new_item(self, item):
        """Moves to the New Template screen"""
        get_screen_element("new_item_screen", "added_items").clear_widgets()
        get_screen_element("new_item_screen", "item_title").text = item
        change_screen("new_item_screen")

    @log_runtime
    def search(self):
        """Opens the search dialog."""
        dialog = SearchDialog()
        dialog.open_search_dialog(self.md_list)

    @log_runtime
    def reset_list(self):
        """Resets the items view."""

        # for table view, ignore reset
        if self.view == "table":
            return

        self.ids.scroll_area.clear_widgets()
        if self.view == "list":
            self.populate_list_view(LIST_PATH)
        elif self.view == "archive":
            self.populate_list_view(ARCHIVES_PATH)

    @log_runtime
    def go_to_edit_template(self):
        """Displays the edit template view."""
        topbar = get_screen_element("edit_template_screen", "topbar")
        topbar.title = self.ids.topbar.title
        self.manager.current = "edit_template_screen"
