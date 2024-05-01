from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from utils import change_screen, open_yaml_file, save_to_yaml, TEMPLATE_PATH, LIST_PATH


class NewItemScreen(Screen):
    """New Item creation view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_fields = []
        self.options = {}

    def open_date_picker(self, text_field, *args):
        """Displays the date picker for date fields."""
        date_picker = MDDatePicker()

        def on_save(instance, value, date_range):
            text_field.text = str(value)

        date_picker.bind(on_save=on_save)
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
            added_items_layout.add_widget(placeholder)

    def add_widget_by_field_type(self, placeholder, field):
        """Builds widgets from template."""
        field_name = field["field_name"]
        field_type = field["type"]
        field_categories = field.get("categories", [])
        self.options[field_name] = field_categories

        self.add_field = MDTextField(multiline=True)
        self.add_field.helper_text = field_name
        self.add_field.helper_text_mode = "persistent"
        self.add_field.icon_right = "note-text-outline"

        self.add_field.input_type = "number" if field_type == "Number" else "text"
        self.add_field.icon_right = (
            "format-list-numbered" if field_type == "Number" else "text"
        )

        if field_type == "Date":
            self.add_field.icon_right = "calendar-outline"
            self.add_field.bind(focus=self.open_date_picker)
        elif field_type == "Category":
            self.add_field.icon_right = "clipboard-list-outline"
            self.category_fields.append(field_name)
            self.add_field.bind(
                focus=lambda instance, value: self.show_dropdown(instance)
            )

        placeholder.add_widget(self.add_field)

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
        all_items = self.ids.added_items

        for w in all_items.children:
            vals = [val.text for val in w.children if isinstance(val, MDTextField)]
            labels = [
                val.helper_text for val in w.children if isinstance(val, MDTextField)
            ]

        mapped_values = dict(zip(labels, vals))
        mapped_values = {k: v for k, v in reversed(mapped_values.items())}

        # Save as yaml. Use timestamp as suffix for the filenames.
        new_date = datetime.now().strftime("%Y-%m-%d %H%M%S")
        yaml_file_path = f"{LIST_PATH}{self.ids.item_title.text}/{self.ids.item_title.text}_{new_date}.yaml"
        save_to_yaml(yaml_file_path, mapped_values)
        change_screen("items_screen")
