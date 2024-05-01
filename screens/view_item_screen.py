from screens.new_item_screen import NewItemScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from utils import (
    save_to_yaml,
    change_screen,
    open_yaml_file,
)
import os


class ViewItemScreen(NewItemScreen):
    """Item View screen."""

    def on_enter(self):
        """Loads the yaml file fields into UI."""
        self.ids.added_items.clear_widgets()

        title_parts = self.ids.item_title.text.split("/")
        self.ids.display_title.text = title_parts[-1]

        yaml_file_path = f"{self.ids.item_title.text}.yaml"
        item_dict = open_yaml_file(yaml_file_path)

        placeholder = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
        )

        for key, val in item_dict.items():
            add_field = MDTextField(helper_text=key, helper_text_mode="persistent")
            add_field.text = val
            placeholder.add_widget(add_field)

        self.ids.added_items.add_widget(placeholder)

    def on_save(self):
        """Saves the changes in the field values to the same yaml."""
        if os.path.exists(f"{self.ids.item_title.text}.yaml"):
            all_items = self.ids.added_items

            for w in all_items.children:
                vals = [val.text for val in w.children if isinstance(val, MDTextField)]
                labels = [
                    val.helper_text
                    for val in w.children
                    if isinstance(val, MDTextField)
                ]

            mapped_values = dict(zip(labels, vals))
            mapped_values = {k: v for k, v in reversed(mapped_values.items())}

            # Save as yaml
            save_to_yaml(f"{self.ids.item_title.text}.yaml", mapped_values)
        change_screen("items_screen")
