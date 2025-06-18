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

Die Anwendung setzt eine PostgreSQL-Datenbank voraus. Hinterlege die Verbindungs-URL
in der Umgebungsvariable `DATABASE_URL`, z. B.:

```bash
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.zwghpoibdgbldnbsafym.supabase.co:5432/postgres"
```

Erstelle darin folgende Tabellen (z. B. über das SQL-Fenster in Supabase):

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS registrations (
    participant TEXT NOT NULL,
    session_id BIGINT NOT NULL REFERENCES sessions(id),
    PRIMARY KEY (participant, session_id)
);
```

Danach kann jede:r Teilnehmer:in den Namen eingeben und maximal zwei verfügbare Sessions wählen. Die aktuelle Auslastung wird live angezeigt.
