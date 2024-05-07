"""New Item Screen"""

from datetime import datetime

from kivy.uix.screenmanager import Screen

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField

from utils import LIST_PATH, TEMPLATE_PATH, change_screen, open_yaml_file, save_to_yaml


class NewItemScreen(Screen):
    """New Item creation view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_fields = []
        self.options = {}

    def open_date_picker(self, text_field, instance):
        """Displays the date picker for date fields."""
        date_picker = MDDatePicker()

        def on_save(_instance, value, _date_range):
            text_field.text = str(value)

        date_picker.bind(on_save=on_save)
        if instance:
            date_picker.open()

    def on_enter(self, *args):
        """Displays all the items inside the list."""
        template = open_yaml_file(f"{TEMPLATE_PATH}{self.ids.item_title.text}.yaml")
        added_items_layout = self.ids.added_items
        placeholder = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
        )

        for fields in template.values():
            for field in fields:
                self.add_widget_by_field_type(placeholder, field)
            added_items_layout.add_widget(placeholder, index=0)

    def add_widget_by_field_type(self, placeholder, field):
        """Builds widgets from template."""
        field_name = field["field_name"]
        field_type = field["type"]
        field_categories = field.get("categories", [])
        self.options[field_name] = field_categories

        add_field = MDTextField(
            multiline=True,
            helper_text=field_name,
            helper_text_mode="persistent",
            icon_right="note-text-outline",
        )

        # for numeric fields, setl input type for numeric keyboard.
        add_field.input_type = "number" if field_type == "Number" else "text"
        add_field.icon_right = (
            "format-list-numbered" if field_type == "Number" else "text"
        )

        if field_type == "Date":
            add_field.icon_right = "calendar-outline"
            add_field.bind(focus=self.open_date_picker)
        elif field_type == "Category":
            add_field.icon_right = "clipboard-list-outline"
            self.category_fields.append(field_name)
            add_field.bind(focus=lambda instance, _: self.show_dropdown(instance))

        placeholder.add_widget(add_field)

    def show_dropdown(self, text_field):
        """Displays the Category field dropdown."""
        options = self.options[text_field.helper_text]
        menu_items = [
            {
                "text": option,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=option: self.set_text_value(text_field, x),
            }
            for option in options
        ]
        text_field.dropdown = MDDropdownMenu(
            caller=text_field, items=menu_items, width_mult=4, position="center"
        )
        text_field.dropdown.open()

    def set_text_value(self, text_field, value):
        """Fills the value picked from the dropdown for Category fields."""
        text_field.text = value
        text_field.dropdown.dismiss()

    def on_save(self):
        """Saves the item as a yaml file"""
        mapped_values = {}
        all_items = self.ids.added_items.children

        for item in all_items:
            for child in item.children:
                if isinstance(child, MDTextField):
                    mapped_values[child.helper_text] = child.text
        mapped_values = dict(reversed(mapped_values.items()))

        # some error handling
        if not list(mapped_values.values())[0]:
            MDDialog(text="Primary field is empty").open()
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
