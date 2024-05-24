"""Custom Lists for Lists and Items"""

import os
import shutil

from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogSupportingText, MDDialogContentContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingIcon,
)
from kivymd.uix.selectioncontrol import MDCheckbox
from utils import (
    LIST_PATH,
    TEMPLATE_PATH,
    ARCHIVES_PATH,
    change_screen,
    get_screen_element,
    open_yaml_file,
    save_to_yaml,
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
class ListOfLists(MDListItem):
    """List of the user created Lists."""

    def __init__(self, headline, **kwargs):
        super().__init__(**kwargs)
        self.headline = MDListItemHeadlineText(text=headline)
        self._txt_left_pad = 10
        self.font_style = "H5"
        self.dialog = None
        self.height = "60dp"

    def on_release(self):
        """Sets the screen title to the item title."""
        title = get_screen_element("items_screen", "topbar")
        title.title = self.headline.text
        change_screen("items_screen")

    def delete_list_dialog(self):
        """Displays delete list confirmation dialog."""
        self.dialog = MDDialog(
            MDDialogSupportingText(text="This will remove all items under this lists."),
            MDDialogContentContainer(
                MDButton(
                    MDButtonText(text="Delete"),
                    md_bg_color="red",
                    on_release=self.delete_folder,
                ),
                MDButton(MDButtonText(text="Cancel"), on_release=self.close_dialog),
            ),
        )
        self.dialog.open()

    def delete_folder(self, _):
        """Deletes the list folder and all files."""
        list_name = get_screen_element("items_screen", "topbar")
        list_name.text = self.headline.text
        template_file = os.path.join(TEMPLATE_PATH, f"{self.headline.text}.yaml")
        list_dir = os.path.join(LIST_PATH, f"{self.headline.text}/")
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
class ListOfItems(MDListItem):
    """List of user created items."""

    def __init__(self, headline, secondary, **kwargs):
        super().__init__(**kwargs)
        self.row = MDListItem(
            MDListItemHeadlineText(text=headline),
            MDListItemSupportingText(text=secondary),
        )

    def mark(self, check, list_of_items):
        """Check/Uncheck item"""
        item = open_yaml_file(self.secondary_text)
        try:
            if item["checked"]:
                item["checked"] = False
                check.icon = "checkbox-blank-outline"
                self.text = self.text.replace("[s]", "")
            elif not item["checked"]:
                item["checked"] = True
                check.icon = "checkbox-marked-outline"
                self.text = f"[s]{self.text}[/s]"
        except KeyError:
            item["checked"] = False

        save_to_yaml(self.secondary_text, item)

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

        try:
            shutil.move(source_file, destination_path)
            self.parent.remove_widget(list_of_items)
        except OSError as e:
            MDDialog(text=f"File could not be moved: {e}")


class LeftCheckbox(MDCheckbox):
    pass
