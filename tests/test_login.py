from helpers import wait_for_window


def test_valid_login_opens_dashboard(login_page):

    login_page.login("admin", "admin123")

    dashboard = wait_for_window("Dashboard")
    assert dashboard.window_text() == "Dashboard"
