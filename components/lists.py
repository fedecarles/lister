"""Custom Lists for Lists and Items"""

import os
import shutil

from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from utils import (
    LIST_PATH,
    TEMPLATE_PATH,
    ARCHIVES_PATH,
    change_screen,
    get_screen_element,
)


# pylint: disable=R0901
class RoundCard(MDCard):
    """Round car for list items view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = [
            30,
        ]


# pylint: disable=R0901
class ListOfLists(TwoLineAvatarIconListItem, RoundCard):
    """List of the user created Lists."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._txt_left_pad = 10
        self.font_style = "H5"
        self.divider = None
        self.dialog = None
        self.height = "60dp"

    def on_release(self):
        """Sets the screen title to the item title."""
        title = get_screen_element("items_screen", "topbar")
        title.title = self.text
        change_screen("items_screen")

    def delete_list_dialog(self):
        """Displays delete list confirmation dialog."""
        self.dialog = MDDialog(
            text="This will remove all items under this lists.",
            buttons=[
                MDRaisedButton(
                    text="Delete", md_bg_color="red", on_release=self.delete_folder
                ),
                MDRaisedButton(text="Cancel", on_release=self.close_dialog),
            ],
        )
        self.dialog.open()

    def delete_folder(self, _):
        """Deletes the list folder and all files."""
        list_name = get_screen_element("items_screen", "topbar")
        list_name.text = self.text
        template_file = os.path.join(TEMPLATE_PATH, f"{self.text}.yaml")
        list_dir = os.path.join(LIST_PATH, f"{self.text}/")
        try:
            shutil.rmtree(list_dir)
            os.remove(template_file)
            self.parent.remove_widget(self)
            self.dialog.dismiss()
        except OSError as e:
            MDDialog(text=f"Deletion failed: {e}").open()

    def close_dialog(self, _):
        """Closes the delete list confirmation dialog."""
        self.dialog.dismiss()


# pylint: disable=R0901
class ListOfItems(TwoLineAvatarIconListItem):
    """List of user created items."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._txt_left_pad = 0
        self.font_style = "H6"

    def on_release(self):
        """Update screen title."""
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = self.secondary_text.replace(".yaml", "")
        change_screen("view_item_screen")

    def delete_item(self, list_of_items):
        """Deletes the item yaml file."""
        os.remove(f"{self.secondary_text}")
        self.parent.remove_widget(list_of_items)

    def archive_item(self, list_of_items):
        """Moves item to archives."""

        list_name = get_screen_element("items_screen", "topbar").title
        source_file = os.path.join(self.secondary_text)
        destination_path = ""

        file = os.path.basename(source_file)
        if os.path.exists(os.path.join(ARCHIVES_PATH, list_name, file)):
            destination_path = os.path.join(LIST_PATH, list_name)
        elif os.path.exists(os.path.join(LIST_PATH, list_name, file)):
            destination_path = os.path.join(ARCHIVES_PATH, list_name)

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        shutil.move(source_file, destination_path)
        self.parent.remove_widget(list_of_items)
