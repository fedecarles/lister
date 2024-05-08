"""Main Screen"""

import os

from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

from components.lists import ListOfLists
from components.dialogs import SearchDialog
from utils import (
    LIST_PATH,
    ASSETS_PATH,
    get_folder_list,
    save_to_yaml,
    create_dialog,
)


class MainScreen(Screen):
    """Main Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def main_menu_open(self, instance):
        """Opens the field category dropdown menu."""
        menu_items = [
            {
                "text": "Light",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Light": self.change_theme(instance, x),
            },
            {
                "text": "Dark",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Dark": self.change_theme(instance, x),
            },
        ]
        menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            hor_growth="left",
            position="bottom",
            width_mult=2,
        )
        menu.open()

    def change_theme(self, _, theme):
        """Sets the app theme."""
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = theme
        app.theme_cls.primary_palette = "DeepPurple"
        app.theme_cls.primary_hue = "200"

        # save to config
        theme_config = {"theme": theme}
        save_to_yaml(os.path.join(ASSETS_PATH, "config.yaml"), theme_config)

    # pylint: disable=R0801
    def open_search_dialog(self):
        """Opens the search dialog."""

        def search_callback(_):
            search_text = self.dialog.content_cls.ids.search_field.text
            search_results = [
                item for item in self.ids.container.children if search_text in item.text
            ]

            if search_results:
                self.ids.container.clear_widgets()
                for item in search_results:
                    self.ids.container.add_widget(item)

            self.dismiss_dialog(_)

        self.dialog = create_dialog(
            SearchDialog(), self.dismiss_dialog, search_callback
        )
        self.dialog.open()

    # pylint: disable=R0801
    def dismiss_dialog(self, _):
        """Closes dialog."""
        if self.dialog:
            self.dialog.dismiss()

    def reset_list(self):
        """Resets to the full list view."""
        self.ids.container.clear_widgets()
        folder_list = get_folder_list(LIST_PATH)

        for list_item in folder_list:
            add_list = ListOfLists(text=list_item)
            self.ids.container.add_widget(add_list)
