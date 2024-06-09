"""Custom Dialogs classes"""

import os
import yaml

from kivymd.uix.dialog import MDDialog


# pylint: disable=R0901
class SearchDialog(MDDialog):
    """Search dialog box."""

    def open_search_dialog(self, container):
        """Opens the search dialog."""

        def search_callback(_):
            search_results = [
                item
                for item in container.children
                if self.ids.search_field.text.lower() in item.ids.headline.text.lower()
            ]

            if search_results:
                container.clear_widgets()
                for item in search_results:
                    container.add_widget(item)

            self.dismiss_dialog(_)

        self.ids.cancel_btn.bind(on_release=self.dismiss_dialog)
        self.ids.search_btn.bind(on_release=search_callback)
        self.open()

    # pylint: disable=R0801
    def dismiss_dialog(self, _):
        """Closes dialog."""
        self.dismiss()


class RenameDialog(MDDialog):
    """Rename List dialog box."""

    def open_rename_dialog(self, title, templates_path, lists_path, archives_path):
        """Opens the search dialog."""

        def rename_callback(_):
            old_name = title.text
            old_template = os.path.join(templates_path, f"{old_name}.yaml")
            old_list = os.path.join(lists_path, old_name)
            old_archive = os.path.join(archives_path, old_name)

            with open(old_template, encoding="utf-8") as file:
                template = yaml.safe_load(file)
            title.text = self.ids.rename_field.text
            template[title.text] = template.pop(old_name)

            new_template = os.path.join(templates_path, f"{title.text}.yaml")
            new_list = os.path.join(lists_path, title.text)
            new_archive = os.path.join(archives_path, title.text)

            with open(new_template, "w", encoding="utf-8") as file:
                yaml.dump(template, file, default_flow_style=False, sort_keys=False)

            os.remove(old_template)
            os.rename(old_list, new_list)
            os.rename(old_archive, new_archive)
            self.dismiss_dialog(_)

        self.ids.cancel_btn.bind(on_release=self.dismiss_dialog)
        self.ids.rename_btn.bind(on_release=rename_callback)
        self.open()

    # pylint: disable=R0801
    def dismiss_dialog(self, _):
        """Closes dialog."""
        self.dismiss()
