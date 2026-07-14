"""Legacy dashboard entry — routes into the premium shell (already authenticated)."""

from shell_app import BankApp


def open_dashboard():
    app = BankApp()
    app._rebuild_shell("dashboard")
    app.run()
