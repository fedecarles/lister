"""Template Creation Screen"""

import os

from kivy.uix.screenmanager import Screen

from kivymd.uix.dialog import MDDialog, MDDialogSupportingText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.textfield import MDTextField

from components.lists import NewFieldForm
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
        new_field = NewFieldForm()
        self.ids.added_fields.add_widget(new_field)

    def on_save(self):
        """Saves the template to a yaml file."""
        md_boxlayouts = self.ids.added_fields
        fields = []
        template = {}

        folder_list = get_folder_list(LIST_PATH)

        # Handle some commor errors.
        if not md_boxlayouts.children:
            MDDialog(
                MDDialogSupportingText(
                    text="Please add at least one filed before saving."
                )
            ).open()
            return

        template_name = str(self.ids.list_name.text)
        if not template_name:
            MDDialog(
                MDDialogSupportingText(text="Please enter a template name.")
            ).open()

            return

        if template_name in folder_list:
            MDDialog(
                MDDialogSupportingText(text="A Template already exists with than name.")
            ).open()
            return

        for widget in md_boxlayouts.children:
            name = widget.ids.name.text
            typ = widget.ids.category_text.text
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
            MDDialog(
                MDDialogSupportingText(text=f"Error saving Template: {str(e)}.")
            ).open()
