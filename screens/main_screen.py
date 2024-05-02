from kivy.uix.screenmanager import Screen
from components.lists import ListOfLists
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from components.dialogs import SearchDialog
from kivymd.uix.menu import MDDropdownMenu
from utils import get_folder_list, save_to_yaml, LIST_PATH
from kivymd.app import MDApp

from screens.template_create_screen import TemplateCreateScreen


class MainScreen(Screen):
    """Main Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def main_menu_open(self, topbar):
        """Opens the field category dropdown menu."""
        menu_items = [
            {
                "text": "Light",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Light": self.change_theme(topbar, x),
            },
            {
                "text": "Dark",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Dark": self.change_theme(topbar, x),
            },
        ]
        menu = MDDropdownMenu(
            caller=topbar,
            items=menu_items,
            hor_growth="left",
        )
        menu.open()

    def change_theme(self, topbar, theme):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = theme
        app.theme_cls.primary_palette = "DeepPurple"
        app.theme_cls.primary_hue = "200"

        # save to config
        theme_config = {"theme": theme}
        save_to_yaml("config.yaml", theme_config)

    def open_search_dialog(self):
        def search_callback(instance):
            search_text = self.dialog.content_cls.ids.search_field.text

            item_list = self.ids.container
            search_results = []
            for item in item_list.children:
                if search_text in item.text:
                    search_results.append(item)

            if search_results:
                self.ids.container.clear_widgets()
                for item in search_results:
                    self.ids.container.add_widget(item)

            self.dismiss_dialog()

        self.dialog = MDDialog(
            type="custom",
            content_cls=SearchDialog(),
            buttons=[
                MDRaisedButton(
                    text="Cancel", md_bg_color="red", on_release=self.dismiss_dialog
                ),
                MDRaisedButton(text="Search", on_release=search_callback),
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self):
        self.dialog.dismiss()

    def reset_list(self):
        self.ids.container.clear_widgets()
        folder_list = get_folder_list(LIST_PATH)

        for list_item in folder_list:
            add_list = ListOfLists(text=list_item)
            self.ids.container.add_widget(add_list)
