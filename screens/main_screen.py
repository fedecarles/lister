"""Main Screen"""

from kivy.uix.screenmanager import Screen

from components.lists import ListOfLists
from components.dialogs import SearchDialog
from utils import (
    LIST_PATH,
    get_folder_list,
)


class MainScreen(Screen):
    """Main Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def search(self):
        """Opens search dialog."""
        dialog = SearchDialog()
        dialog.open_search_dialog(self.ids.list_container)

    def reset_list(self):
        """Resets to the full list view."""
        self.ids.list_container.clear_widgets()
        folder_list = get_folder_list(LIST_PATH)

        for list_item in folder_list:
            add_list = ListOfLists()
            add_list.ids.headline.text = list_item
            self.ids.list_container.add_widget(add_list)
