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

        # Wait until the fields and the Save button are detectable.
        deadline = time.time() + 10
        entry_controls = []
        while time.time() < deadline:
            entry_controls = self._entry_controls()
            try:
                save_button = self._button_by_text("Save Customer")
                if len(entry_controls) >= 3 and save_button is not None:
                    break
            except Exception:
                pass
            time.sleep(0.2)

        if len(entry_controls) < 3:
            raise RuntimeError("Customer input fields not found")

        self.name_field = entry_controls[0]
        self.cin_field = entry_controls[1]
        self.email_field = entry_controls[2]
        self.save_button = self._button_by_text("Save Customer")

        # Optional checkbox in extended UI
        self.insurance_checkbox = None
        try:
            self.insurance_checkbox = self._button_by_text("Add insurance")
        except Exception:
            self.insurance_checkbox = None

    def add_customer(self, name, cin, email, *, add_insurance=False, insurance_type="hospital", account_amount=1000):
        self._click_and_type(self.name_field, name)

        # Recompute fields to avoid stale/hidden Tk controls after the window redraw.
        # This also helps when Tk widgets are re-created on focus/update.
        time.sleep(0.2)
        entry_controls = self._entry_controls()
        if len(entry_controls) >= 3:
            self.name_field = entry_controls[0]
            self.cin_field = entry_controls[1]
            self.email_field = entry_controls[2]

        # Best-effort: retry click/type for CIN/Email in case controls refresh.
        self._click_and_type(self.cin_field, cin)
        time.sleep(0.1)
        self._click_and_type(self.email_field, email)




        # Insurance selection: UI was migrated from checkbox to radio buttons + account amount field.
        if add_insurance:
            try:
                # Select “Compte avec assurance”
                radio_ins = self._button_by_text("Compte avec assurance")
                radio_ins.click_input()
            except Exception:
                pass

            # Fill account amount if present (Entry has no direct label mapping; fallback to best-effort by entries)
            try:
                # Re-scan entry controls; the balance entry should appear after the 3 main fields.
                entry_controls = self._entry_controls()
                # Heuristic: balance is typically the 4th entry.
                if len(entry_controls) >= 4:
                    balance_entry = entry_controls[3]
                    self._click_and_type(balance_entry, str(account_amount))
            except Exception:
                pass

            # insurance type radio in insurance step 2 window is not selected here; it defaults to hospital.
            # test will later choose/keep default.

        self.save_button.click_input()


