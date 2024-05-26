"""Custom Lists for Lists and Items"""

import os
import shutil

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText
from kivymd.uix.list import (
    MDList,
    MDListItem,
)
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.label import MDLabel
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
class ListOfLists(MDList):
    """List of the user created Lists."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_release(self):
        """Sets the screen title to the item title."""
        title = get_screen_element("items_screen", "topbar")
        title.title = self.ids.list_name.text
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
        list_name.text = self.ids.list_name.text
        template_file = os.path.join(TEMPLATE_PATH, f"{self.ids.list_name.text}.yaml")
        list_dir = os.path.join(LIST_PATH, f"{self.ids.list_name.text}/")
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
class ListOfItems(MDCardSwipe):
    """List of user created items."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yaml_path = ""

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

    def on_press(self):
        """Update screen title."""
        title_element = get_screen_element("view_item_screen", "item_title")
        title_element.text = self.yaml_path.replace(".yaml", "")
        change_screen("view_item_screen")

    def delete_item(self, list_of_items):
        """Deletes the item yaml file."""
        os.remove(f"{self.yaml_path}")
        self.parent.remove_widget(list_of_items)

    def archive_item(self, list_of_items):
        """Moves item to archives."""

        list_name = get_screen_element("items_screen", "topbar").title
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
            self.parent.remove_widget(list_of_items)
        except OSError as e:
            MDDialog(text=f"File could not be moved: {e}")


class LeftCheckbox(MDCheckbox):
    pass


class NewFieldForm(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def menu_open(self, caller_btn):
        """Opens the field category dropdown menu."""
        options = ["Text", "Number", "Date", "Category"]
        menu_items = [
            {
                "text": f"{o}",
                "on_release": lambda x=f"{o}": self.update_button_text(caller_btn, x),
            }
            for o in options
        ]
        menu = MDDropdownMenu(
            caller=caller_btn,
            items=menu_items,
            position="bottom",
            adaptive_width=True,
            hor_growth="left",
        )
        menu.open()

    def update_button_text(self, caller_btn, text):
        """Updates the buton with category values."""
        self.text_field = MDTextField(hint_text="Category A, Category B...")
        if text == "Category":
            self.dialog = MDDialog(
                MDDialogSupportingText(text="Enter Categories"),
                MDDialogContentContainer(self.text_field),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Cancel"),
                        md_bg_color="red",
                        on_release=self.dismiss_dialog,
                    ),
                    MDButton(
                        MDButtonText(text="Save"),
                        on_release=lambda _: self.set_categories(caller_btn),
                    ),
                ),
            )
            self.dialog.open()
        else:
            self.ids.category_text.text = text

    def dismiss_dialog(self, _):
        """Closes the dialog."""
        if self.dialog:
            self.dialog.dismiss()

    def set_categories(self, caller_btn):
        """Sets the categories as the button value."""
        categories = self.text_field.text
        self.ids.category_text.text = f"[{categories}]"
        self.dismiss_dialog(caller_btn)


class NewItemForm(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
