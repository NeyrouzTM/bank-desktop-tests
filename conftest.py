

from __future__ import annotations

import base64
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from pywinauto import Desktop
from pytest_html import extras as html_extras

# Pendant les tests, l’app doit enregistrer les clients dans un fichier runtime séparé
# (sinon reset_customer_database() détruit data/customers.xlsx qui sert de dataset).
os.environ["CUSTOMERS_DB_PATH"] = str(
    Path(__file__).resolve().parent / "data" / "test_customers_runtime.xlsx"
)

from helpers import reset_customer_database


from pages.base_page import BaseTkPage
from pages.customer_page import CustomerPage
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.transfer_page import TransferPage


_APP_PROCESS = None
_KNOWN_TITLES = ["Login", "Dashboard"]
# Keep the app open after pytest so you can keep watching / reusing it.
_KEEP_APP_ALIVE = os.environ.get("KEEP_APP", "1") != "0"
# Live mode drives the already visible app and does not restart it by default.
_LIVE_APP_MODE = os.environ.get("LIVE_APP", "1") != "0"
_ALLOW_APP_RESTART = os.environ.get("ALLOW_APP_RESTART", "0") == "1"


def _desktop():
    return Desktop(backend="win32")


def _running_windows():
    desktop = _desktop()
    found = []
    for title in _KNOWN_TITLES:
        found.extend(desktop.windows(title=title))
    return found


def _start_app():
    global _APP_PROCESS

    project_root = Path(__file__).resolve().parent
    _APP_PROCESS = subprocess.Popen(
        [sys.executable, str(project_root / "app" / "main.py")],
        cwd=str(project_root),
    )
    return _APP_PROCESS


def _stop_app():
    global _APP_PROCESS

    if _APP_PROCESS is None:
        return
    try:
        _APP_PROCESS.terminate()
    except Exception:
        pass
    _APP_PROCESS = None


def _ensure_app_running(timeout=15):
    """Attach to an already open app, otherwise launch one visible instance."""
    existing = _running_windows()
    if existing:
        return existing[-1]

    _start_app()
    deadline = time.time() + timeout
    while time.time() < deadline:
        existing = _running_windows()
        if existing:
            return existing[-1]
        time.sleep(0.2)
    raise RuntimeError("Bank Desktop App did not start (Login/Dashboard window missing)")


def _goto_login_screen():
    """Ensure we are on the Login window for login tests."""
    desktop = _desktop()
    if desktop.windows(title="Login"):
        return

    # App already past login — restart once for a clean Login screen
    _stop_app()
    for window in _running_windows():
        try:
            window.close()
        except Exception:
            pass
    time.sleep(0.5)
    _ensure_app_running()
    BaseTkPage()._wait_for_window("Login", timeout=15)


@pytest.fixture(autouse=True)
def clean_customer_database():
    # Réinitialise le fichier de données utilisé par l'application.
    # Les tests doivent ensuite écrire leurs clients dans ce même fichier Excel.
    reset_customer_database()
    yield





@pytest.fixture(scope="session", autouse=True)
def app_session():
    """
    One shared live app for the whole pytest session.
    Prefer attaching to the app you already opened (temps réel).
    """
    window = _ensure_app_running()
    try:
        yield window
    finally:
        if not _KEEP_APP_ALIVE:
            _stop_app()
            for w in _running_windows():
                try:
                    w.close()
                except Exception:
                    pass


@pytest.fixture
def logged_in_dashboard(app_session):
    desktop = _desktop()

    if not desktop.windows(title="Dashboard"):
        _goto_login_screen()
        login_page = LoginPage()
        login_page.login("admin", "admin123")
        BaseTkPage()._wait_for_window("Dashboard", timeout=15)
        time.sleep(0.5)

    yield BaseTkPage()._wait_for_window("Dashboard", timeout=10)


@pytest.fixture
def login_page(app_session):
    _goto_login_screen()
    page = LoginPage()
    yield page
    # Do not close the live app window.


@pytest.fixture
def customer_page(logged_in_dashboard):
    page = CustomerPage()
    yield page


@pytest.fixture
def search_page(logged_in_dashboard):
    page = SearchPage()
    yield page


@pytest.fixture
def transfer_page(logged_in_dashboard):
    page = TransferPage()
    yield page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = next(
        (value for value in item.funcargs.values() if hasattr(value, "window")),
        None,
    )
    if page is None or getattr(page, "window", None) is None:
        return

    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_path = screenshots_dir / f"{item.nodeid.replace('::', '__').replace('/', '_')}.png"

    try:
        page.window.capture_as_image().save(screenshot_path)
    except Exception:
        pass

    try:
        screenshot_base64 = base64.b64encode(screenshot_path.read_bytes()).decode("utf-8")
        report.extras = getattr(report, "extras", [])
        report.extras.append(
            html_extras.image(
                screenshot_base64,
                name=f"Screenshot - {item.name}",
            )
        )
    except Exception:
        pass
