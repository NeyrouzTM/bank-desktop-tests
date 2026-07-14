from pages.base_page import BaseTkPage


class LoginPage(BaseTkPage):

    def __init__(self):
        super().__init__()
        self._attach_window("Login")

        entry_controls = self._entry_controls()
        if len(entry_controls) < 2:
            raise RuntimeError("Login input fields not found")

        self.username_field = entry_controls[0]
        self.password_field = entry_controls[1]
        self.login_button = self._button_by_text("Login")

    def login(self, username, password):
        self._click_and_type(self.username_field, username)
        self._click_and_type(self.password_field, password)
        self.login_button.click_input()
