import time

from pages.base_page import BaseTkPage
from pages.dashboard_page import DashboardPage


class CustomerPage(BaseTkPage):

    window_title = "Dashboard"

    def __init__(self):
        super().__init__()
        dashboard = DashboardPage()
        dashboard.open_customer_window()
        self._attach_window(self.window_title)
        time.sleep(0.4)

        entry_controls = self._entry_controls()
        if len(entry_controls) < 3:
            raise RuntimeError("Customer input fields not found")

        self.name_field = entry_controls[0]
        self.cin_field = entry_controls[1]
        self.email_field = entry_controls[2]
        self.save_button = self._button_by_text("Save Customer")

    def add_customer(self, name, cin, email):
        self._click_and_type(self.name_field, name)
        self._click_and_type(self.cin_field, cin)
        self._click_and_type(self.email_field, email)
        self.save_button.click_input()
