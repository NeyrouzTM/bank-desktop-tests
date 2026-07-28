import time
import re

from pages.base_page import BaseTkPage
from pages.dashboard_page import DashboardPage


class InsurancePage(BaseTkPage):
    """Page Object for the Insurance subscription form."""

    window_title = "Dashboard"

    def __init__(self):
        super().__init__()
        dashboard = DashboardPage()
        dashboard._activate("Insurance")
        self._attach_window(self.window_title)

        # Wait for insurance form controls to render
        deadline = time.time() + 10
        entry_controls = []
        while time.time() < deadline:
            entry_controls = self._entry_controls()
            try:
                payer_btn = self._button_by_text("Payer")
                search_btn = self._button_by_text("Search")
                if len(entry_controls) >= 2 and payer_btn is not None and search_btn is not None:
                    break
            except Exception:
                pass
            time.sleep(0.2)

        if len(entry_controls) < 2:
            raise RuntimeError("Insurance form input fields not found (need CIN + Balance)")

        self.cin_field = entry_controls[0]
        self.balance_field = entry_controls[1]
        self.search_button = self._button_by_text("Search")
        self.pay_button = self._button_by_text("Payer")

        # Customer info label (appears after search)
        self.customer_info_text = ""

        # Price label
        self.price_text = ""

        # History label
        self.history_text = ""

    def search_customer(self, cin: str):
        """Recherche un client par CIN."""
        self._click_and_type(self.cin_field, str(cin))
        self.search_button.click_input()
        time.sleep(0.3)

        # Read the customer info label via the unique controls
        try:
            # The customer info label is a styled_label; we read its text
            all_controls = self._unique_controls()
            for ctrl in all_controls:
                try:
                    txt = (ctrl.window_text() or "").strip()
                except Exception:
                    continue
                if txt.startswith("Client:") or txt.startswith("Client non trouvé"):
                    self.customer_info_text = txt
                    return txt
        except Exception:
            pass
        self.customer_info_text = ""
        return ""

    def set_balance(self, amount):
        """Définit le montant du solde."""
        self._click_and_type(self.balance_field, str(amount))
        time.sleep(0.1)

    def get_price(self) -> str:
        """Lit le prix affiché (ex: 'Prix: 200€')."""
        try:
            all_controls = self._unique_controls()
            for ctrl in all_controls:
                try:
                    txt = (ctrl.window_text() or "").strip()
                except Exception:
                    continue
                if txt.startswith("Prix:"):
                    self.price_text = txt
                    return txt
        except Exception:
            pass
        self.price_text = ""
        return ""

    def select_insurance_type(self, insurance_type: str):
        """Sélectionne le type d'assurance via radiobutton.
        insurance_type: 'hospital' (Assurance hospitalière) ou 'ambulatoire' (Assurance ambulatoire)
        """
        label_map = {
            "hospital": "Assurance hospitalière",
            "ambulatoire": "Assurance ambulatoire",
        }
        label = label_map.get(insurance_type, "Assurance hospitalière")
        try:
            rb = self._button_by_text(label)
            rb.click_input()
            time.sleep(0.3)  # Wait for pack listbox to refresh
        except Exception as e:
            raise RuntimeError(f"Could not select insurance type '{label}': {e}")

    def select_pack(self, pack_index: int = 0):
        """Sélectionne un pack dans la listbox par son index (0, 1, 2)."""
        all_controls = self._unique_controls()
        # Find the listbox control
        for ctrl in all_controls:
            try:
                class_name = ctrl.class_name()
            except Exception:
                continue
            if class_name == "ListBox":
                # Listbox items are child text elements
                try:
                    items = ctrl.children()
                    if items and pack_index < len(items):
                        items[pack_index].click_input()
                        time.sleep(0.2)
                        return
                except Exception:
                    pass
                break

        # Fallback: try clicking coordinates based on listbox
        for ctrl in all_controls:
            try:
                class_name = ctrl.class_name()
            except Exception:
                continue
            if class_name == "ListBox":
                try:
                    rect = ctrl.rectangle()
                    item_height = 20
                    y_click = rect.top + 10 + pack_index * item_height
                    ctrl.click_input(coords=(rect.left + 50, y_click))
                    time.sleep(0.2)
                except Exception:
                    pass
                return

    def payer(self):
        """Clique sur le bouton Payer."""
        self.pay_button.click_input()
        time.sleep(0.3)

    def get_customer_info(self) -> str:
        return self.customer_info_text

    def get_history_text(self) -> str:
        """Lit le texte d'historique (ex: 'Ce client a 1 souscription(s)')."""
        try:
            all_controls = self._unique_controls()
            for ctrl in all_controls:
                try:
                    txt = (ctrl.window_text() or "").strip()
                except Exception:
                    continue
                if "souscription" in txt.lower():
                    self.history_text = txt
                    return txt
        except Exception:
            pass
        self.history_text = ""
        return ""

