"""View Item Screen"""

import os

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox

from screens.new_item_screen import NewItemScreen
from utils import change_screen, open_yaml_file, save_to_yaml, list_items_to_dict


class ViewItemScreen(NewItemScreen):
    """Item View screen."""

    def on_enter(self, *args):
        """Loads the yaml file fields into UI."""
        self.ids.added_items.clear_widgets()
        self.ids.display_title.text = os.path.basename(self.ids.item_title.text)

        yaml_file_path = f"{self.ids.item_title.text}.yaml"
        item_dict = open_yaml_file(yaml_file_path)

        placeholder = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
        )

        for key, value in item_dict.items():
            if key == "checked":
                add_field = MDCheckbox(active=value, disabled=True)
            else:
                add_field = MDTextField(helper_text=key, helper_text_mode="persistent")
                add_field.text = value
            placeholder.add_widget(add_field)

        self.ids.added_items.add_widget(placeholder)

    def on_save(self):
        """Saves the changes in the field values to the same yaml."""
        if os.path.exists(f"{self.ids.item_title.text}.yaml"):
            all_items = self.ids.added_items.children
            mapped_values = list_items_to_dict(all_items)

            # Save as yaml
            save_to_yaml(f"{self.ids.item_title.text}.yaml", mapped_values)
        change_screen("items_screen")
