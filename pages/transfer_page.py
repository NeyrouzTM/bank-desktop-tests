import time

from pages.base_page import BaseTkPage
from pages.dashboard_page import DashboardPage


class TransferPage(BaseTkPage):

    window_title = "Dashboard"

    def __init__(self):
        super().__init__()
        dashboard = DashboardPage()
        dashboard.open_transfer_window()
        self._attach_window(self.window_title)
        time.sleep(0.4)

        entry_controls = self._entry_controls()
        if len(entry_controls) < 3:
            raise RuntimeError("Transfer input fields not found")

        self.from_cin_field = entry_controls[0]
        self.to_cin_field = entry_controls[1]
        self.amount_field = entry_controls[2]
        self.transfer_button = self._button_by_text("Transfer")

    def transfer_money(self, from_cin, to_cin, amount):
        self._click_and_type(self.from_cin_field, from_cin)
        self._click_and_type(self.to_cin_field, to_cin)
        self._click_and_type(self.amount_field, amount)
        self.transfer_button.click_input()
        time.sleep(0.5)
