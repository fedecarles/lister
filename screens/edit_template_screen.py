"""Edit Template Screen"""

import os
import yaml
from yaml.scanner import ScannerError

from kivymd.uix.dialog import MDDialog, MDDialogSupportingText
from kivy.uix.screenmanager import Screen
from utils import TEMPLATE_PATH, open_yaml_file, save_to_yaml


class EditTemplateScreen(Screen):
    """Template edit Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_path = ""

    def on_enter(self, *args):
        """Populates the yaml template data."""

        self.template_path = os.path.join(
            TEMPLATE_PATH, f"{self.ids.list_title.text}.yaml"
        )
        template = open_yaml_file(self.template_path)
        self.ids.template_text.text = yaml.dump(template)

    def on_save(self):
        """Saves the data to the yaml template."""
        new_template = self.ids.template_text.text
        try:
            new_yaml = yaml.safe_load(new_template)
            save_to_yaml(self.template_path, new_yaml)
            MDDialog(MDDialogSupportingText(text="Template saved.")).open()
        except ScannerError as e:
            MDDialog(MDDialogSupportingText(text=f"Invalid yaml format:{e}")).open()
