from pages.base_page import BaseTkPage


class DashboardPage(BaseTkPage):

    window_title = "Dashboard"

    def __init__(self):
        super().__init__()
        self._attach_window(self.window_title)

    def _activate(self, title):
        # Le texte affiché peut varier (ex: "Create Customer" vs "Add Customer").
        # On tente plusieurs variantes pour éviter les erreurs flakies.
        candidates = [title, title.replace("Customer", "Client"), title.replace("Create", "Add")]
        button = None
        last_exc = None
        for cand in candidates:
            try:
                button = self._button_by_text(cand)
                break
            except Exception as e:
                last_exc = e
        if button is None:
            raise last_exc if last_exc else RuntimeError(f"Button '{title}' not found")
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
