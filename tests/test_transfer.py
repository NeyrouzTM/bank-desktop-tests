from helpers import dismiss_messagebox, save_customers, unique_customer


def _field_text(field):
    return field.window_text().strip()


def test_transfer_success_clears_fields(transfer_page):
    sender = unique_customer(9)
    recipient = unique_customer(10)

    save_customers(
        [
            [sender["name"], sender["cin"], sender["email"]],
            [recipient["name"], recipient["cin"], recipient["email"]],
        ]
    )

    transfer_page.transfer_money(sender["cin"], recipient["cin"], "100")
    dismiss_messagebox("Success")

    assert _field_text(transfer_page.from_cin_field) == ""
    assert _field_text(transfer_page.to_cin_field) == ""
    assert _field_text(transfer_page.amount_field) == ""


def test_transfer_same_account_shows_error(transfer_page):
    customer = unique_customer(11)

    save_customers([[customer["name"], customer["cin"], customer["email"]]])

    transfer_page.transfer_money(customer["cin"], customer["cin"], "100")
    dismiss_messagebox("Error")


def test_transfer_invalid_amount_text_shows_error(transfer_page):
    sender = unique_customer(12)
    recipient = unique_customer(13)

    save_customers(
        [
            [sender["name"], sender["cin"], sender["email"]],
            [recipient["name"], recipient["cin"], recipient["email"]],
        ]
    )

    transfer_page.transfer_money(sender["cin"], recipient["cin"], "abc")
    dismiss_messagebox("Error")


def test_transfer_invalid_amount_negative_shows_error(transfer_page):
    sender = unique_customer(14)
    recipient = unique_customer(15)

    save_customers(
        [
            [sender["name"], sender["cin"], sender["email"]],
            [recipient["name"], recipient["cin"], recipient["email"]],
        ]
    )

    transfer_page.transfer_money(sender["cin"], recipient["cin"], "-5")
    dismiss_messagebox("Error")


def test_transfer_invalid_amount_zero_shows_error(transfer_page):
    sender = unique_customer(16)
    recipient = unique_customer(17)

    save_customers(
        [
            [sender["name"], sender["cin"], sender["email"]],
            [recipient["name"], recipient["cin"], recipient["email"]],
        ]
    )

    transfer_page.transfer_money(sender["cin"], recipient["cin"], "0")
    dismiss_messagebox("Error")


def test_transfer_invalid_account_shows_error(transfer_page):
    sender = unique_customer(18)

    save_customers([[sender["name"], sender["cin"], sender["email"]]])

    transfer_page.transfer_money(sender["cin"], "99999999", "25")
    dismiss_messagebox("Error")


def test_transfer_decimal_amount_clears_fields(transfer_page):
    sender = unique_customer(20)
    recipient = unique_customer(21)

    save_customers(
        [
            [sender["name"], sender["cin"], sender["email"]],
            [recipient["name"], recipient["cin"], recipient["email"]],
        ]
    )

    transfer_page.transfer_money(sender["cin"], recipient["cin"], "25.5")
    dismiss_messagebox("Success")

    assert _field_text(transfer_page.from_cin_field) == ""
    assert _field_text(transfer_page.to_cin_field) == ""
    assert _field_text(transfer_page.amount_field) == ""


def test_transfer_missing_fields_shows_error(transfer_page):
    transfer_page.transfer_money("", "", "")
    dismiss_messagebox("Error")
