"""Custom Lists for Lists and Items"""

import os
import shutil


from kivymd.uix.dialog import (
    MDDialog,
    MDDialogContentContainer,
    MDDialogSupportingText,
)
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from kivymd.uix.button import MDButton, MDButtonText

from utils import (
    ARCHIVES_PATH,
    LIST_PATH,
    TEMPLATE_PATH,
    change_screen,
    get_screen_element,
    open_yaml_file,
    save_to_yaml,
)


# pylint: disable=R0901
class ListOfLists(MDList):
    """List of the user created Lists."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = MDDialog()

    def on_release(self):
        """Sets the screen title to the item title."""
        title = get_screen_element("items_screen", "list_title")
        title.text = self.ids.headline.text
        change_screen("items_screen")

    def delete_list_dialog(self):
        """Displays delete list confirmation dialog."""
        self.dialog = MDDialog(
            MDDialogSupportingText(text="This will remove all items under this lists."),
            MDDialogContentContainer(
                MDButton(
                    MDButtonText(
                        text="Delete", theme_text_color="Custom", text_color="1f2335"
                    ),
                    theme_bg_color="Custom",
                    md_bg_color="ff757f",
                    on_release=self.delete_folder,
                ),
                MDButton(
                    MDButtonText(
                        text="Cancel", theme_text_color="Custom", text_color="1f2335"
                    ),
                    theme_bg_color="Custom",
                    md_bg_color="7aa2f7",
                    on_release=self.close_dialog,
                ),
            ),
        )
        self.dialog.open()

    def delete_folder(self, _):
        """Deletes the list folder and all files."""
        list_name = get_screen_element("items_screen", "topbar")
        list_name.text = self.ids.headline.text
        template_file = os.path.join(TEMPLATE_PATH, f"{self.ids.headline.text}.yaml")
        list_dir = os.path.join(LIST_PATH, f"{self.ids.headline.text}/")
        archive_dir = os.path.join(ARCHIVES_PATH, f"{self.ids.headline.text}/")
        try:
            if os.path.exists(archive_dir):
                shutil.rmtree(archive_dir)
            shutil.rmtree(list_dir)
            os.remove(template_file)
            self.parent.remove_widget(self)
            self.dialog.dismiss()
        except OSError as e:
            MDDialog(MDDialogSupportingText(text=f"Deletion failed: {e}")).open()

    def close_dialog(self, _):
        """Closes the delete list confirmation dialog."""
        self.dialog.dismiss()


# pylint: disable=R0901
class ListOfItems(MDCard):
    """List of user created items."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yaml_path = ""
        self.checked = False

    def mark(self, check):
        """Check/Uncheck item"""
        item = open_yaml_file(self.yaml_path)
        try:
            if item["checked"]:
                item["checked"] = False
                check.icon = "checkbox-blank-outline"
                self.ids.headline.text = self.ids.headline.text.replace("[s]", "")
            elif not item["checked"]:
                item["checked"] = True
                check.icon = "checkbox-marked-outline"
                self.ids.headline.text = f"[s]{self.ids.headline.text}[/s]"
        except KeyError:
            item["checked"] = False

        save_to_yaml(self.yaml_path, item)

    def on_press(self, *args):
        """Update screen title."""
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = self.yaml_path.replace(".yaml", "")
        change_screen("view_item_screen")

    def delete_item(self, list_of_items):
        """Deletes the item yaml file."""
        os.remove(f"{self.yaml_path}")
        self.parent.remove_widget(list_of_items)

    def archive_item(self):
        """Moves item to archives."""

        list_name = get_screen_element("items_screen", "list_title").text
        source_file = os.path.join(self.yaml_path)
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
            self.parent.remove_widget(self)
        except OSError as e:
            MDDialog(
                MDDialogSupportingText(text=f"File could not be moved: {e}")
            ).open()
