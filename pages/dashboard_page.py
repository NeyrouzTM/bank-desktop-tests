from pages.base_page import BaseTkPage


class DashboardPage(BaseTkPage):

    window_title = "Dashboard"

    def __init__(self):
        super().__init__()
        self._attach_window(self.window_title)

    def _activate(self, title):
        button = self._button_by_text(title)
        try:
            self.window.set_focus()
        except Exception:
            pass

        try:
            button.click_input()
        except Exception:
            button.invoke()
        return button

    def open_customer_window(self):
        self._activate("Create Customer")

    def open_search_window(self):
        self._activate("Search Customer")

    def open_transfer_window(self):
        self._activate("Transfer Money")
