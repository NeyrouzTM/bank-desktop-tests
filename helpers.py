from pathlib import Path
from tempfile import NamedTemporaryFile
import time

from openpyxl import Workbook, load_workbook
from pywinauto import Desktop

from app.database import FILE_PATH, init_db


def reset_customer_database():
    init_db()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["CustomerName", "CIN", "Email"])

    target_path = Path(FILE_PATH)
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_path = Path(temp_file.name)

    workbook.save(temp_path)
    temp_path.replace(target_path)


def customer_rows():
    workbook = load_workbook(FILE_PATH)
    worksheet = workbook.active
    return list(worksheet.iter_rows(values_only=True))


def save_customers(rows):
    workbook = load_workbook(FILE_PATH)
    worksheet = workbook.active

    if worksheet.max_row > 1:
        worksheet.delete_rows(2, worksheet.max_row - 1)

    for row in rows:
        worksheet.append(row)

    workbook.save(FILE_PATH)


def wait_for_window(title, timeout=10):
    desktop = Desktop(backend="win32")
    deadline = time.time() + timeout

    while time.time() < deadline:
        windows = desktop.windows(title=title)
        if windows:
            return windows[-1]
        time.sleep(0.2)

    raise RuntimeError(f"{title} window not found")


def dismiss_messagebox(title, timeout=5):
    dialog = wait_for_window(title, timeout=timeout)
    try:
        dialog.child_window(title="OK", class_name="Button").click_input()
    except Exception:
        dialog.close()
    return dialog


def unique_customer(index):
    return {
        "name": f"Test Customer {index}",
        "cin": f"91{index:06d}",
        "email": f"customer{index}@example.com",
    }
