"""View Item Screen"""

import os

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText

from screens.new_item_screen import NewItemScreen
from utils import (
    change_screen,
    open_yaml_file,
    save_to_yaml,
    list_items_to_dict,
)


class ViewItemScreen(NewItemScreen):
    """Item View screen."""

    def on_enter(self, *args):
        """Loads the yaml file fields into UI."""
        self.ids.added_items.clear_widgets()
        self.ids.display_title.text = os.path.basename(self.ids.item_title.text)

        yaml_file_path = f"{self.ids.item_title.text}.yaml"
        item_dict = open_yaml_file(yaml_file_path)

        for key, value in item_dict.items():
            if key == "checked":
                add_field = MDCheckbox(active=value, disabled=True)
            else:
                add_field = MDTextField(
                    MDTextFieldHelperText(text=key, mode="persistent"),
                    mode="outlined",
                )
                add_field.text = value
            self.ids.added_items.add_widget(add_field)

    def on_save(self):
        """Saves the changes in the field values to the same yaml."""
        if os.path.exists(f"{self.ids.item_title.text}.yaml"):
            all_items = self.ids.added_items.children
            mapped_values = list_items_to_dict(all_items)

            # Save as yaml
            save_to_yaml(f"{self.ids.item_title.text}.yaml", mapped_values)
        change_screen("items_screen")
