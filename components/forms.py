"""Custom field view forms."""

# pylint: disable=E0611
from kivy.properties import StringProperty

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
    MDDialogSupportingText,
)
from kivymd.uix.list import MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.button import MDButton, MDButtonText


# pylint: disable=too-many-ancestors
class NewFieldForm(MDList):
    """New field form."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = MDDialog()
        self.text_field = MDTextField()

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


# pylint: disable=too-many-ancestors
class NewItemForm(MDBoxLayout):
    """New item form."""


# pylint: disable=too-many-ancestors
class TableView(MDRecycleView):
    """Table view."""


# pylint: disable=too-many-ancestors
class TableCell(MDBoxLayout):
    """Table cell class for use in TableView"""

    text = StringProperty(None)
