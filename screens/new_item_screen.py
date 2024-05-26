"""New Item Screen"""

from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldMaxLengthText,
)
from components.lists import NewItemForm

from utils import (
    LIST_PATH,
    TEMPLATE_PATH,
    change_screen,
    open_yaml_file,
    save_to_yaml,
    list_items_to_dict,
)


class NewItemScreen(Screen):
    """New Item creation view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_fields = []
        self.options = {}

    def open_date_picker(self, text_field, instance):
        """Displays the date picker for date fields."""
        date_picker = MDModalDatePicker()

        def on_cancel(instance_date_picker):
            instance_date_picker.dismiss()

        def on_ok(instance_date_picker):
            text_field.text = str(instance_date_picker.get_date()[0])

        date_picker.bind(on_ok=on_ok, on_cancel=on_cancel)
        if instance:
            date_picker.open()

    def show_dropdown(self, text_field, instance):
        """Displays the Category field dropdown."""
        options = self.options[text_field.children[0].text]
        menu_items = [
            {
                "text": option,
                "on_release": lambda x=option: self.set_text_value(text_field, x),
            }
            for option in options
        ]
        self.dropdown = MDDropdownMenu(
            caller=text_field, items=menu_items, width_mult=4, position="center"
        )
        self.dropdown.open()

    def set_text_value(self, text_field, value):
        """Fills the value picked from the dropdown for Category fields."""
        text_field.text = value
        self.dropdown.dismiss()

    def on_enter(self, *args):
        """Displays all the items inside the list."""
        template = open_yaml_file(f"{TEMPLATE_PATH}{self.ids.item_title.text}.yaml")

        for fields in template.values():
            for field in fields:
                self.add_widget_by_field_type(self.ids.added_items, field)
            # self.ids.added_items.add_widget(placeholder, index=0)

    def add_widget_by_field_type(self, placeholder, field):
        """Builds widgets from template."""
        field_name = field["field_name"]
        field_type = field["type"]
        field_categories = field.get("categories", [])
        self.options[field_name] = field_categories
        self.category_fields.append(field_name)

        add_field = NewItemForm()

        if field_type == "Text":
            icon = "note-text-outline"
        elif field_type == "Number":
            icon = "format-list-numbered"
        elif field_type == "Date":
            icon = "calendar-outline"
            add_field.ids.new_field_value.bind(focus=self.open_date_picker)
        elif field_type == "Category":
            icon = "clipboard-list-outline"
            add_field.ids.new_field_value.bind(focus=self.show_dropdown)

        add_field.ids.field_type_icon.icon = icon
        add_field.ids.helper_text.text = field_name

        placeholder.add_widget(add_field)

    def on_save(self):
        """Saves the item as a yaml file"""
        all_items = self.ids.added_items.children

        mapped_values = list_items_to_dict(all_items)
        mapped_values["checked"] = False

        # some error handling
        if not list(mapped_values.values())[0]:
            MDDialog(MDDialogSupportingText(text="Primary field is empty")).open()
            return

        # Save as yaml. Use timestamp as suffix for the filenames.
        try:
            title = self.ids.item_title.text
            new_date = datetime.now().strftime("%Y-%m-%d %H%M%S")
            yaml_file_path = f"{LIST_PATH}{title}/{title}_{new_date}.yaml"
            save_to_yaml(yaml_file_path, mapped_values)
            change_screen("items_screen")
        except OSError as e:
            MDDialog(text=f"Error saving note: {str(e)}.").open()
