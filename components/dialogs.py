"""Custom Dialogs classes"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog


# pylint: disable=R0901
class SearchDialog(MDDialog):
    """Search dialog box."""

    def open_search_dialog(self, container):
        """Opens the search dialog."""
        self.container = container

        def search_callback(_):
            search_results = [
                item
                for item in self.container.children
                if self.ids.search_field.text in item.ids.headline.text
            ]

            if search_results:
                self.container.clear_widgets()
                for item in search_results:
                    self.container.add_widget(item)

            self.dismiss_dialog(_)

        self.ids.cancel_btn.bind(on_release=lambda x: self.dismiss_dialog(x))
        self.ids.search_btn.bind(on_release=search_callback)
        self.open()

    # pylint: disable=R0801
    def dismiss_dialog(self, _):
        """Closes dialog."""
        self.dismiss()
