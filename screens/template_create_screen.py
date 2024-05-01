from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog

from components.dialogs import CategoryInputDialog

from utils import (
    get_folder_list,
    change_screen,
    save_to_yaml,
    LIST_PATH,
    TEMPLATE_PATH,
)
import os


class TemplateCreateScreen(Screen):
    """Template creation screen view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_dialog = None

    def on_enter(self):
        """Housekeeping on enter"""
        self.ids.added_fields.clear_widgets()

    def add_field(self, *args):
        """Adds a field to the template on user request."""

        field_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            adaptive_height=True,
        )
        field_name = MDTextField(hint_text="Field name...", id="name")
        field_type_btn = MDRaisedButton(text="Text", id="type_btn")
        field_type_btn.bind(
            on_release=lambda x, btn=field_type_btn: self.menu_open(btn)
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
                        on_release=lambda x="": self.save_categories(caller_btn, x),
                    ),
                ],
            )
            self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    def save_categories(self, caller_btn, *args):
        print(self.dialog.content_cls.ids)
        categories = self.dialog.content_cls.ids.categories.text
        caller_btn.text = f"[{categories}]"
        self.dismiss_dialog()

    def on_save(self):
        """Saves the template to a yaml file."""
        md_boxlayouts = self.ids.added_fields
        fields = []
        template = {}

        folder_list = get_folder_list(LIST_PATH)

        for w in md_boxlayouts.children:
            name = w.children[1].text
            typ = w.children[0].text
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
        if template_name in folder_list:
            MDDialog(text="A Template already exists  with than name.").open()
        else:
            yaml_file_path = f"{TEMPLATE_PATH}{template_name}.yaml"
            save_to_yaml(yaml_file_path, template)
            print(f"YAML file '{yaml_file_path}' has been created successfully.")

            # Create the folder for the list items.
            os.makedirs(LIST_PATH + self.ids.list_name.text, exist_ok=True)
            change_screen("main_screen")
