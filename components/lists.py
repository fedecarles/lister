from utils import get_screen_element, change_screen, LIST_PATH, TEMPLATE_PATH
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
import shutil
import os


class RoundCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = [
            30,
        ]


class ListOfLists(TwoLineAvatarIconListItem, RoundCard):
    """List of the user created Lists."""

    def __init__(self, pk=None, **kwargs):
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

    def delete_dialog(self, list_of_lists):
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

    def delete_folder(self, obj):
        """Deletes the list folder and all files."""
        list_name = get_screen_element("items_screen", "topbar")
        list_name.text = self.text
        template_file = f"{TEMPLATE_PATH}{list_name.text}.yaml"
        list_dir = f"{LIST_PATH}{list_name.text}/"
        shutil.rmtree(list_dir)
        os.remove(template_file)
        self.parent.remove_widget(self)
        self.dialog.dismiss()

    def close_dialog(self, obj):
        """Closes the delete list confirmation dialog."""
        self.dialog.dismiss()


class ListOfItems(TwoLineAvatarIconListItem):
    def __init__(self, pk=None, **kwargs):
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
