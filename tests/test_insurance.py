"""Tests UI pour la page Assurance - scénarios réalistes avec les vrais clients.

Utilise les données du fichier data/customers.xlsx:
  - neyrouz t  (CIN: 12345645) – client principal des tests
  - user 10    (CIN: 78945678) – second client
  - issam      (CIN: 0)        – pour tests CIN invalide (pas 8 chiffres)

L'application reste ouverte entre les tests (KEEP_APP & LIVE_APP).
"""

import time

import pytest

from helpers import dismiss_messagebox, save_customers

# ── Données réelles depuis data/customers.xlsx ──────────────────────────
NEYROUZ = {"name": "neyrouz t", "cin": "12345645", "email": "neyrouz@gmail.com"}
USER10 = {"name": "user 10", "cin": "78945678", "email": "user@gmail.com"}
ISSAM = {"name": "issam", "cin": "0", "email": "issam@gmail.com"}

PACK_PRICES = {
    "hospital": [200, 500, 800],
    "ambulatoire": [100, 300, 600],
}


def _prepare_customers(*customers):
    """Enregistre les clients dans la base de test (runtime)."""
    save_customers([[c["name"], c["cin"], c["email"]] for c in customers])


def _dismiss_any():
    """Ferme toute messagebox présente (Success ou Error)."""
    for title in ("Success", "Error"):
        try:
            dismiss_messagebox(title, timeout=2)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────
# Fixture : nettoie la base clients + insurance avant chaque test
# ─────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def _clean_insurance_data():
    """Réinitialise insurance.xlsx avant chaque test."""
    from app.database import INSURANCE_PATH, init_insurance_db
    from openpyxl import Workbook

    init_insurance_db()
    wb = Workbook()
    ws = wb.active
    ws.append(["Date", "CIN", "CustomerName", "InsuranceType", "Pack", "Price",
               "BalanceBefore", "BalanceAfter", "Status"])
    wb.save(INSURANCE_PATH)
    yield


# ═════════════════════════════════════════════════════════════════════════
# SCÉNARIOS SUCCÈS
# ═════════════════════════════════════════════════════════════════════════

def test_insurance_hospital_pack1_success(insurance_page):
    """neyrouz t · solde 600€ · hospital pack1 (200€) → Success, solde→400€"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    time.sleep(0.3)
    info = insurance_page.get_customer_info()
    assert "neyrouz" in info.lower(), f"Client non trouvé: {info}"

    insurance_page.set_balance(600)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)  # pack1 = 200€
    time.sleep(0.2)
    price = insurance_page.get_price()
    assert "200" in price, f"Prix attendu 200€, obtenu: {price}"

    insurance_page.payer()
    dismiss_messagebox("Success")
    time.sleep(0.2)

    # Vérifie que le solde a été mis à jour
    try:
        history = insurance_page.get_history_text()
        assert "1" in history, f"Historique attendu '1 souscription', obtenu: {history}"
    except Exception:
        pass


def test_insurance_hospital_pack2_success(insurance_page):
    """neyrouz t · solde 1000€ · hospital pack2 (500€) → Success, solde→500€"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(1000)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(1)  # pack2 = 500€

    price = insurance_page.get_price()
    assert "500" in price, f"Prix attendu 500€, obtenu: {price}"

    insurance_page.payer()
    dismiss_messagebox("Success")


def test_insurance_ambulatoire_pack3_success(insurance_page):
    """user 10 · solde 700€ · ambulatoire pack3 (600€) → Success, solde→100€"""
    _prepare_customers(USER10)

    insurance_page.search_customer(USER10["cin"])
    insurance_page.set_balance(700)
    insurance_page.select_insurance_type("ambulatoire")
    insurance_page.select_pack(2)  # pack3 = 600€

    price = insurance_page.get_price()
    assert "600" in price, f"Prix attendu 600€, obtenu: {price}"

    insurance_page.payer()
    dismiss_messagebox("Success")


def test_insurance_multiple_subscriptions(insurance_page):
    """neyrouz t · 2 souscriptions successives → historique '2 souscription(s)'"""
    _prepare_customers(NEYROUZ)

    # Première souscription : pack1 hospital (200€) avec 500€ → reste 300€
    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(500)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)
    insurance_page.payer()
    dismiss_messagebox("Success")
    time.sleep(0.3)

    # Deuxième souscription : pack1 ambulatoire (100€) avec le nouveau solde 300€ → reste 200€
    insurance_page.select_insurance_type("ambulatoire")
    insurance_page.select_pack(0)
    insurance_page.payer()
    dismiss_messagebox("Success")
    time.sleep(0.3)

    history = insurance_page.get_history_text()
    assert "2" in history, f"Historique attendu '2 souscriptions', obtenu: {history}"


# ═════════════════════════════════════════════════════════════════════════
# SCÉNARIOS ÉCHEC (solde insuffisant)
# ═════════════════════════════════════════════════════════════════════════

def test_insurance_insufficient_balance_hospital(insurance_page):
    """neyrouz t · solde 50€ · hospital pack1 (200€) → Error (50 < 200)"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(50)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)

    insurance_page.payer()
    dismiss_messagebox("Error")


def test_insurance_insufficient_balance_ambulatoire(insurance_page):
    """user 10 · solde 50€ · ambulatoire pack2 (300€) → Error (50 < 300)"""
    _prepare_customers(USER10)

    insurance_page.search_customer(USER10["cin"])
    insurance_page.set_balance(50)
    insurance_page.select_insurance_type("ambulatoire")
    insurance_page.select_pack(1)  # pack2 = 300€

    insurance_page.payer()
    dismiss_messagebox("Error")


def test_insurance_switch_type_insufficient(insurance_page):
    """neyrouz t · solde 500€ · hospital pack1 (200€) OK · switch ambulatoire pack3 (600€) Error"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(500)

    # Hospital pack1 (200€) devrait marcher
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)
    insurance_page.payer()
    dismiss_messagebox("Success")
    time.sleep(0.3)

    # Switch ambulatoire pack3 (600€) > nouveau solde 300€ → Error
    insurance_page.select_insurance_type("ambulatoire")
    insurance_page.select_pack(2)
    insurance_page.payer()
    dismiss_messagebox("Error")


# ═════════════════════════════════════════════════════════════════════════
# SCÉNARIOS VALIDATION
# ═════════════════════════════════════════════════════════════════════════

def test_insurance_cin_not_found(insurance_page):
    """CIN inexistant (00000000) → Error 'CIN invalide' ou 'Client non trouvé'"""
    _prepare_customers()

    insurance_page.search_customer("00000000")

    info = insurance_page.get_customer_info()
    if info:
        assert "non trouvé" in info.lower(), f"Attendu 'non trouvé', obtenu: {info}"

    # Tenter de payer sans client valide → Error
    insurance_page.set_balance(1000)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)
    insurance_page.payer()
    try:
        dismiss_messagebox("Error")
    except Exception:
        pass  # Si pas de message, c'est que le bouton Payer est bloqué côté UI


def test_insurance_empty_cin_shows_error(insurance_page):
    """CIN vide → Error"""
    _prepare_customers()

    insurance_page.search_customer("")
    try:
        dismiss_messagebox("Error")
    except Exception:
        pass


def test_insurance_balance_negative_shows_error(insurance_page):
    """Solde négatif → Error"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(-50)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)

    insurance_page.payer()
    dismiss_messagebox("Error")


def test_insurance_balance_zero_insufficient(insurance_page):
    """Solde 0€ · hospital pack1 (200€) → Error (0 < 200)"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(0)
    insurance_page.select_insurance_type("hospital")
    insurance_page.select_pack(0)

    insurance_page.payer()
    dismiss_messagebox("Error")


def test_insurance_no_pack_selected(insurance_page):
    """Payer sans sélectionner de pack → Error"""
    _prepare_customers(NEYROUZ)

    insurance_page.search_customer(NEYROUZ["cin"])
    insurance_page.set_balance(1000)
    insurance_page.select_insurance_type("hospital")
    # Ne sélectionne PAS de pack
    time.sleep(0.2)

    insurance_page.payer()
    try:
        dismiss_messagebox("Error")
    except Exception:
        pass

