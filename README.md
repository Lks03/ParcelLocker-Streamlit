# Parcel Locker System — Streamlit

A web application built on the original `Parcel`, `Locker`, `Recipient`, and `ParcelLockerSystem` classes.
The web entry point is `app.py`. The original command-line interface remains available through `python main.py`.

## Getting Started

Python 3.11 or later is recommended. Tested with Python 3.14 and Streamlit 1.65.0.
Open a terminal in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Pages and Features

- **Home:** Access the main features.
- **Register Parcel:** Enter the recipient's name, contact information, and tracking number. The system assigns an available locker and generates a six-digit pickup code.
- **Collect Parcel:** Verify the pickup code, then confirm collection. The locker becomes available again after confirmation.
- **Parcel Records:** View saved records. Sample records from the mockups are not included.
- **Locker Status:** View 12 lockers in four columns on desktop screens or two columns on narrow screens. Gray indicates an occupied locker.

The interface follows the four supplied mockups, using a white background, dark text, blue buttons, thin borders, and a navigation sidebar.
Success messages appear only after successful actions. Validation covers invalid codes, parcels already collected, full lockers, empty fields, and duplicate tracking numbers.

## Data Storage and Limitations

When `data.json` does not exist, the application starts with 12 available lockers. The file is created when the first parcel is registered.
It stores parcel records and locker states and supports the original JSON format. Back up this file before editing it manually.

Read and write errors are reported without replacing an unreadable file with empty data. Writes use a temporary file and atomic replacement. Operations from sessions within the same Streamlit process are serialized.

Do not use multiple server processes or the command-line interface to write to the same data file at the same time. Public or multi-instance deployments should use a database with transactions.
JSON files on cloud platforms with temporary file systems do not guarantee long-term storage. This version is intended for local coursework demonstrations.

Courier, Customer, and Staff are page labels, not authenticated roles. All demonstration pages are accessible through navigation. Do not expose real personal information in a public deployment of this version.

Locker opening is simulated. Notifications are previews only; no SMS messages or emails are sent.

## MVC Responsibilities

- `parcel.py`, `locker.py`, `recipient.py`: Entity models and their rules.
- `system.py`: Business logic for assigning lockers, generating pickup codes, and processing collection.
- `controller.py`: Coordinates page actions, reads the latest state, and serializes changes.
- `repository.py`: Loads JSON data and writes it safely.
- `views.py`, `styles.css`: Streamlit views and interface styling.
- `app.py`: Web application entry point.
- `main.py`: Original command-line entry point.

## Testing

Run the following command from the project folder:

```powershell
.\.venv\Scripts\python.exe -m unittest test_app.py -v
```

Tests use temporary files and do not modify the application's `data.json`. They cover registration and collection, restoring saved data, duplicate tracking numbers, full capacity, repeated collection attempts, concurrent sessions, corrupted data, failed writes, and Streamlit page interactions.

## Resources

[Streamlit documentation](https://docs.streamlit.io/develop)
