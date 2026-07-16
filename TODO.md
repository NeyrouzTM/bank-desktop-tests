# TODO - Amélioration rapport pytest-html

- [ ] Modifier `conftest.py` pour afficher le CIN dans le rapport pour les cas **succès** (best-effort, sinon “CIN: N/A”).
- [ ] Modifier `conftest.py` pour afficher le CIN + ajouter une capture d’écran pour les échecs en **setup/call/teardown**.
- [ ] Lancer `pytest` et régénérer le rapport `reports/report.html`.
- [ ] Vérifier manuellement que:
  - [ ] Les tests passés contiennent une ligne CIN
  - [ ] Les tests échoués contiennent une capture d’écran
  - [ ] Les échecs en setup reçoivent aussi une capture d’écran

