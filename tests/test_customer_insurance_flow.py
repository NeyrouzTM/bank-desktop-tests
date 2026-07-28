import time

from helpers import dismiss_messagebox, unique_customer
from pages.customer_page import CustomerPage



def test_create_customer_with_insurance_flow(customer_page):
    customer = unique_customer(101)

    account_amount = 600.0  # should be enough for hospital pack1 (200€) and maybe ambulatory pack2 etc.

    # Create customer with insurance
    customer_page.add_customer(
        customer["name"],
        customer["cin"],
        customer["email"],
        add_insurance=True,
        account_amount=account_amount,
    )

    # Dismiss "Success" messagebox from customer creation.
    try:
        dismiss_messagebox("Success")
    except Exception:
        try:
            dismiss_messagebox("Error")
        except Exception:
            pass

    insurance_title = "Insurance - Vermeg (simulation)"

    # Wait for insurance window
    last_err = None
    insurance_window = None
    for _ in range(20):
        try:
            insurance_window = customer_page._wait_for_window(insurance_title, timeout=2)
            break
        except Exception as e:
            last_err = e
            time.sleep(0.3)

    if insurance_window is None:
        raise RuntimeError(f"{insurance_title} window not found") from last_err

    insurance_window.set_focus()

    # Choose ambulance/hospital and a pack, then payer.
    original_window = customer_page.window
    customer_page.window = insurance_window
    try:
        # Choose hospitalière (default is hospital)
        try:
            rb_hosp = customer_page._button_by_text("Assurance hospitalière")
            rb_hosp.click_input()
        except Exception:
            pass

        # Select a pack from listbox default pack1
        payer_btn = customer_page._button_by_text("Payer")
        payer_btn.click_input()
    finally:
        customer_page.window = original_window

    # Payment should succeed (account_amount >= 200)
    dismiss_messagebox("Success")


def test_create_customer_with_insurance_insufficient_balance(customer_page):
    customer = unique_customer(102)

    account_amount = 50.0  # should NOT be enough for any pack (min hospital=200, ambulatory=100)

    customer_page.add_customer(
        customer["name"],
        customer["cin"],
        customer["email"],
        add_insurance=True,
        account_amount=account_amount,
    )

    try:
        dismiss_messagebox("Success")
    except Exception:
        try:
            dismiss_messagebox("Error")
        except Exception:
            pass

    insurance_title = "Insurance - Vermeg (simulation)"

    last_err = None
    insurance_window = None
    for _ in range(20):
        try:
            insurance_window = customer_page._wait_for_window(insurance_title, timeout=2)
            break
        except Exception as e:
            last_err = e
            time.sleep(0.3)

    if insurance_window is None:
        raise RuntimeError(f"{insurance_title} window not found") from last_err

    insurance_window.set_focus()

    original_window = customer_page.window
    customer_page.window = insurance_window
    try:
        try:
            rb_hosp = customer_page._button_by_text("Assurance hospitalière")
            rb_hosp.click_input()
        except Exception:
            pass

        payer_btn = customer_page._button_by_text("Payer")
        payer_btn.click_input()
    finally:
        customer_page.window = original_window

    dismiss_messagebox("Error")




