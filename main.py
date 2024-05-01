from screens.template_create_screen import TemplateCreateScreen
from screens.view_item_screen import ViewItemScreen
from screens.new_item_screen import NewItemScreen
from kivy.uix.screenmanager import ScreenManager
from screens.items_screen import ItemsScreen
from screens.main_screen import MainScreen
from components.lists import ListOfLists
from kivy.utils import platform
from kivymd.app import MDApp

from utils import (
    open_yaml_file,
    get_folder_list,
    LIST_PATH,
    TEMPLATE_PATH,
    EXPORTS_PATH,
)
import os

CONFIG = open_yaml_file("config.yaml")


class MainApp(MDApp):
    def on_start(self):
        """Populate the List of Lists."""
        self.folder_list = get_folder_list(LIST_PATH)
        all_lists = os.listdir(LIST_PATH)
        main_screen = self.root.get_screen("main_screen")

        for list_item in all_lists:
            add_list = ListOfLists(text=list_item)
            main_screen.ids.container.add_widget(add_list)

    def refresh_folder_view(self):
        """Updates the display to show the current list of folders."""

        screen = self.root.get_screen("main_screen")
        new_folder_list = get_folder_list(LIST_PATH)

        # Add widgets for each folder
        for list_item in new_folder_list:
            if list_item not in self.folder_list:
                add_list = ListOfLists(text=list_item)
                screen.ids.container.add_widget(add_list)
                self.folder_list.append(list_item)
            else:
                print(f"Item: {list_item} is already on self.folder_list")
        self.folder_list = new_folder_list

    def create_dirs(self):
        """Creates the initial lists and templates folders."""
        if platform == "android":
            from android.permissions import Permission, request_permissions
            from android.storage import primary_external_storage_path

            request_permissions(
                [
                    Permission.INTERNET,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ],
            )

            # Get the app's internal storage directory
            # app_dir = self.user_data_dir
            app_dir = primary_external_storage_path()

            # Create the 'Lister' directory if it doesn't exist
            lister_dir = os.path.join(app_dir, "Documents/Lister")
            if not os.path.exists(lister_dir):
                os.makedirs(lister_dir)

            # Create 'lists', 'templates', and 'exports' directories inside 'Lister'
            folders = ["lists", "templates", "exports"]
            for folder in folders:
                folder_path = os.path.join(lister_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
        else:
            os.makedirs(LIST_PATH, exist_ok=True)
            os.makedirs(TEMPLATE_PATH, exist_ok=True)
            os.makedirs(EXPORTS_PATH, exist_ok=True)

    def build(self):
        self.theme_cls.theme_style = CONFIG["theme"]
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.primary_hue = "200"
        self.create_dirs()

        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(TemplateCreateScreen(name="template_create_screen"))
        sm.add_widget(ItemsScreen(name="items_screen"))
        sm.add_widget(NewItemScreen(name="new_item_screen"))
        sm.add_widget(ViewItemScreen(name="view_item_screen"))


if __name__ == "__main__":
    app = MainApp()
    app.run()
