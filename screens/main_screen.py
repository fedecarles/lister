from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from utils import save_to_yaml
from kivymd.app import MDApp


class MainScreen(Screen):
    """Main Screen View"""

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
