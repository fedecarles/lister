"""Template Creation Screen"""

import os

from kivy.uix.screenmanager import Screen

from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.textfield import MDTextField

from components.dialogs import CategoryInputDialog
from utils import (
    LIST_PATH,
    TEMPLATE_PATH,
    change_screen,
    get_folder_list,
    save_to_yaml,
)


class TemplateCreateScreen(Screen):
    """Template creation screen view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self, *args):
        """Housekeeping on enter"""
        self.ids.added_fields.clear_widgets()

    def add_field(self):
        """Adds a field to the template on user request."""

        field_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            adaptive_height=True,
            padding=10,
        )
        field_name = MDTextField(
            hint_text="Field name...",
            id="name",
            mode="round",
            input_type="text",
        )
        field_type_btn = MDDropDownItem()
        field_type_btn.text = "Text"
        field_type_btn.bind(
            on_release=lambda _, btn=field_type_btn: self.menu_open(btn)
        )
        field_row.add_widget(field_name)
        field_row.add_widget(field_type_btn)
        self.ids.added_fields.add_widget(field_row)

    def menu_open(self, caller_btn):
        """Opens the field category dropdown menu."""
        options = ["Text", "Number", "Date", "Category"]
        menu_items = [
            {
                "text": f"{o}",
                "viewclass": "OneLineListItem",
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
        caller_btn.text = text
        if text == "Category":
            self.dialog = MDDialog(
                type="custom",
                content_cls=CategoryInputDialog(),
                buttons=[
                    MDRaisedButton(
                        text="Cancel", md_bg_color="red", on_release=self.dismiss_dialog
                    ),
                    MDRaisedButton(
                        text="Save",
                        on_release=lambda _: self.set_categories(caller_btn),
                    ),
                ],
            )
            self.dialog.open()

    def dismiss_dialog(self, _):
        """Closes the dialog."""
        if self.dialog:
            self.dialog.dismiss()

    def set_categories(self, caller_btn):
        """Sets the categories as the button value."""
        categories = self.dialog.content_cls.ids.categories.text
        caller_btn.text = f"[{categories}]"
        self.dismiss_dialog(caller_btn)

    def on_save(self):
        """Saves the template to a yaml file."""
        md_boxlayouts = self.ids.added_fields
        fields = []
        template = {}

        folder_list = get_folder_list(LIST_PATH)

        # Handle some commor errors.
        if not md_boxlayouts.children:
            MDDialog(text="Please add at least one field before saving.").open()
            return

        template_name = str(self.ids.list_name.text)
        if not template_name:
            MDDialog(text="Please enter a template name.").open()
            return

        if template_name in folder_list:
            MDDialog(text="A Template already exists with that name.").open()
            return

        for widget in md_boxlayouts.children:
            name = widget.children[1].text
            typ = widget.children[0].text
            if typ not in ["Text", "Number", "Date"]:
                categories = typ.strip("[]")
                categories = categories.split(",")
                field = {
                    "field_name": name,
                    "type": "Category",
                    "categories": categories,
                }
            else:
                field = {"field_name": name, "type": typ}

            fields.append(field)

        template_name = str(self.ids.list_name.text)
        template[template_name] = fields[::-1]  # reverse list

        # Save template as yaml
        yaml_file_path = f"{TEMPLATE_PATH}{template_name}.yaml"
        try:
            save_to_yaml(yaml_file_path, template)
            print(f"YAML file '{yaml_file_path}' has been created successfully.")
            os.makedirs(LIST_PATH + self.ids.list_name.text, exist_ok=True)
            change_screen("main_screen")
        except OSError as e:
            MDDialog(text=f"Error saving Template: {str(e)}").open()
