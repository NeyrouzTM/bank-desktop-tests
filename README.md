# Bank Desktop App Test Framework

Small desktop demo application and automated UI test framework for the Bank Desktop App.

## Requirements

- Python 3.11+
- Windows
- Virtual environment recommended

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the app

```powershell
python app\main.py
```

Manual real-time testing flow:

1. Launch the app with `python app\\main.py`
2. Log in with:
	- Username: `admin`
	- Password: `admin123`
3. Use Dashboard buttons to test customer creation, search, and transfer interactively.

## Run the tests

```powershell
python -m pytest -v
```

## HTML report

The test run generates an HTML report at `reports/report.html`.
When a UI test fails, the report now includes the screenshot captured at the moment of failure.

## Screenshots on failure

Failed UI tests save screenshots in `screenshots/`.

## Project structure

- `app/` desktop demo application
- `pages/` Page Object Model classes
- `tests/` automated test cases
- `data/` Excel test data
- `reports/` HTML test reports
- `screenshots/` failure captures

