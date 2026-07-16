TODO - banque desktop tests (Excel fixtures & runtime)

- [ ] app/database.py : rendre FILE_PATH configurable via env var (CUSTOMERS_DB_PATH)
- [ ] helpers.py :
  - [ ] ajouter reset_test_customer_database() qui copie data/customers.xlsx -> data/test_customers_runtime.xlsx
  - [ ] faire save_customers() écrire dans le runtime
  - [ ] faire unique_customer() lire depuis data/customers.xlsx (dataset manuel)
- [ ] conftest.py :
  - [ ] dans la fixture autouse clean_customer_database(), appeler reset_test_customer_database() (A = à chaque test)
  - [ ] définir os.environ['CUSTOMERS_DB_PATH'] = chemin runtime
- [ ] vérifier que transfer/customer/search UI lisent bien le runtime (via FILE_PATH env)
- [ ] exécuter tests et corriger les éventuels écarts

