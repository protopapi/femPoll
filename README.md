# femPoll

Streamlit-App zur Verwaltung von Session-Anmeldungen.

## Installation

```bash
pip install -r requirements.txt
```

## Starten der Anwendung

```bash
streamlit run app.py
```

Beim ersten Start wird eine SQLite-Datenbank `event_poll.db` angelegt und mit Beispiel-Sessions gefüllt. Anschließend kann jede:r Teilnehmer:in den Namen eingeben und maximal zwei verfügbare Sessions auswählen. Die aktuelle Auslastung wird live angezeigt.
