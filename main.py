"""Main App Build"""

import os

from kivymd.app import MDApp

from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager

from components.lists import ListOfLists

from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from screens.main_screen import MainScreen
from screens.items_screen import ItemsScreen
from screens.new_item_screen import NewItemScreen
from screens.view_item_screen import ViewItemScreen
from screens.edit_template_screen import EditTemplateScreen
from screens.template_create_screen import TemplateCreateScreen
from utils import (
    DOCUMENTS_PATH,
    EXPORTS_PATH,
    LIST_PATH,
    TEMPLATE_PATH,
    ASSETS_PATH,
    ARCHIVES_PATH,
    get_folder_list,
    open_yaml_file,
)

CONFIG = open_yaml_file(os.path.join(ASSETS_PATH, "config.yaml"))


class MainApp(MDApp):
    """Main Lister App"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.folder_list = []

    def on_start(self):
        """Populate the List of Lists."""
        if os.path.exists(LIST_PATH):
            self.folder_list = get_folder_list(LIST_PATH)
            all_lists = os.listdir(LIST_PATH)
            main_screen = self.root.get_screen("main_screen")

            for list_item in all_lists:
                # add_list = ListOfLists(MDListItemHeadlineText(text=list_item))
                add_list = ListOfLists(list_item)
                # add_list = MDListItem(MDListItemHeadlineText(text=list_item))
                main_screen.ids.container.add_widget(add_list)

    def refresh_folder_view(self):
        """Updates the display to show the current list of folders."""

        screen = self.root.get_screen("main_screen")
        new_folder_list = get_folder_list(LIST_PATH)

        # Add widgets for each folder
        for list_item in new_folder_list:
            if list_item not in self.folder_list:
                add_list = ListOfLists(list_item)
                screen.ids.container.add_widget(add_list)
                self.folder_list.append(list_item)
            else:
                print(f"Item: {list_item} is already on self.folder_list")
        self.folder_list = new_folder_list

    def create_dirs(self):
        """Creates the initial lists and templates folders."""
        if platform == "android":
            # pylint: disable=E0401
            # pylint: disable=C0415
            from android.permissions import Permission, request_permissions

            request_permissions(
                [
                    Permission.INTERNET,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ],
                self.on_request_permissions_done,
            )
        else:
            os.makedirs(LIST_PATH, exist_ok=True)
            os.makedirs(TEMPLATE_PATH, exist_ok=True)
            os.makedirs(EXPORTS_PATH, exist_ok=True)
            os.makedirs(ARCHIVES_PATH, exist_ok=True)

    def on_request_permissions_done(self, _permissions, grant_results):
        """Create folders on permissions granted."""
        if all(grant_results):
            # pylint: disable=E0401
            # pylint: disable=C0415
            from android.storage import primary_external_storage_path

            # Get the app's internal storage directory
            # app_dir = self.user_data_dir
            app_dir = primary_external_storage_path()

            # Create the 'Lister' directory if it doesn't exist
            lister_dir = os.path.join(app_dir, DOCUMENTS_PATH)
            if not os.path.exists(lister_dir):
                os.makedirs(lister_dir)

            # Create 'lists', 'templates', and 'exports' directories inside 'Lister'
            folders = ["lists", "templates", "exports", "archives"]
            for folder in folders:
                folder_path = os.path.join(lister_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
        else:
            self.stop()

    def build(self):
        """Build app theme and screens"""
        self.create_dirs()
        self.theme_cls.theme_style = CONFIG["theme"]
        self.theme_cls.primary_palette = "Deepskyblue"
        self.theme_cls.primary_hue = "200"

        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(TemplateCreateScreen(name="template_create_screen"))
        sm.add_widget(ItemsScreen(name="items_screen"))
        sm.add_widget(NewItemScreen(name="new_item_screen"))
        sm.add_widget(ViewItemScreen(name="view_item_screen"))
        sm.add_widget(EditTemplateScreen(name="edit_template_screen"))


if __name__ == "__main__":
    app = MainApp()
    app.run()
