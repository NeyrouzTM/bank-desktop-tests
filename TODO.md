# TODO - Page Assurance (Insurance)

## Objectif
Ajouter une page Assurance complète dans l'application bancaire avec formulaire de souscription.

## Étapes

### Étape 1 - Database
- [x] app/database.py : Ajouter `init_insurance_db()`, `add_insurance_subscription()`, `list_insurance_subscriptions()`

### Étape 2 - Page UI (shell_app.py)
- [x] app/shell_app.py : Ajouter "Insurance" dans `NAV_ITEMS`
- [x] app/shell_app.py : Créer `_view_insurance()` avec formulaire complet (solde, type assurance, packs, payer)

### Étape 3 - Page Object (tests)
- [x] pages/insurance_page.py : Créer la Page Object pour les tests UI

### Étape 4 - Tests
- [x] tests/test_insurance.py : Tests automatisés (succès, échec solde insuffisant, validation CIN)
  - 12 scénarios avec les vrais clients (neyrouz t, user 10, etc.)

### Étape 5 - Validation
- [ ] Lancer `pytest tests/test_insurance.py -v` et corriger les éventuels soucis

