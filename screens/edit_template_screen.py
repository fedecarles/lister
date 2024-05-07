"""Edit Template Screen"""

import os
import yaml

from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from utils import TEMPLATE_PATH, open_yaml_file, save_to_yaml


class EditTemplateScreen(Screen):
    """Template edit Screen View"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_path = ""

    def on_enter(self, *args):
        """Populates the yaml template data."""
        # self.template_path = f"{TEMPLATE_PATH}{self.ids.topbar.title}.yaml"
        self.template_path = os.path.join(
            TEMPLATE_PATH, f"{self.ids.topbar.title}.yaml"
        )
        template = open_yaml_file(self.template_path)
        self.ids.template_text.text = yaml.dump(template)

    def on_save(self):
        """Saves the data to the yaml template."""
        new_template = self.ids.template_text.text
        new_yaml = yaml.safe_load(new_template)
        save_to_yaml(self.template_path, new_yaml)
        MDDialog(text="Template saved.").open()
