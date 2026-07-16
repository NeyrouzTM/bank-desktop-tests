# TODO - Stabiliser le framework + Excel dataset/runtime

## Objectif
Rendre stable l’exécution automatique (UI pywinauto) et garantir que :
- les données testées viennent d’un fichier Excel (dataset éditable)
- quand on ajoute un client via l’app, ça s’enregistre dans un autre fichier Excel (runtime)

## Étape 1 — Dataset & runtime Excel (déjà fait partiellement)
- [x] `conftest.py` fixe `CUSTOMERS_DB_PATH` vers `data/test_customers_runtime.xlsx`
- [ ] Vérifier/si besoin : s’assurer que `reset_customer_database()` ne supprime pas le dataset `data/customers.xlsx` mais seulement le runtime

## Étape 2 — Corriger l’automatisation UI (principal bug)
Les erreurs actuelles :
- `Customer input fields not found`
- `Button 'Save Customer' not found`
- `Transfer input fields not found`
- erreurs pywinauto `WinError 1400 / InvalidWindowHandle / ElementNotVisible`

Actions proposées (à implémenter) :
- [ ] Dans `pages/base_page.py` : fiabiliser `_attach_window()` et `_entry_controls()`
  - augmenter temps d’attente / remplacer par `wait_until` sur présence des champs
  - ne pas utiliser `time.sleep(0.4)` partout, mais attendre que les widgets soient visibles
- [ ] Dans `pages/customer_page.py` / `pages/transfer_page.py` / `pages/search_page.py` :
  - adapter l’ordre des champs trouvés (les méthodes actuelles prennent les 3 premiers `TkChild` rectangulaires)

## Étape 3 — Corriger la lecture Excel pendant le test
- [ ] `pages/search_page.py` : éviter la lecture d’un fichier runtime Excel corrompu/non prêt
  - ajouter retry sur `load_workbook(FILE_PATH)` si `BadZipFile`

## Étape 4 — Valider
- [ ] Lancer `python -m pytest -q`
- [ ] Vérifier que les tests utilisent bien :
  - dataset : `data/customers.xlsx`
  - runtime : `data/test_customers_runtime.xlsx`

