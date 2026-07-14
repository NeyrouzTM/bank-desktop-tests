from helpers import dismiss_messagebox, save_customers, unique_customer


def test_search_existing_customer_returns_details(search_page):
    customer = unique_customer(7)

    save_customers([[customer["name"], customer["cin"], customer["email"]]])

    search_page.search_customer(customer["cin"])

    assert customer["name"] in search_page.result_text
    assert customer["cin"] in search_page.result_text
    assert customer["email"] in search_page.result_text


def test_search_existing_customer_with_spaces(search_page):
    customer = unique_customer(8)

    save_customers([[customer["name"], customer["cin"], customer["email"]]])

    search_page.search_customer(f"  {customer['cin']}  ")

    assert customer["name"] in search_page.result_text


def test_search_missing_customer_returns_not_found(search_page):
    search_page.search_customer("99999999")

    assert search_page.result_text == "Customer not found"


def test_search_missing_cin_shows_error(search_page):
    search_page.search_customer("")
    dismiss_messagebox("Error")
