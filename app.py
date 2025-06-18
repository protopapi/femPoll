import os
import psycopg2
import pandas as pd
import streamlit as st
from typing import List, Dict

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Katzenklo$42@db.zwghpoibdgbldnbsafym.supabase.co:5432/postgres",
)

SESSION_CONFIG = [
    ("Session 1", 5),
    ("Session 2", 7),
    ("Session 3", 8),
    ("Session 4", 10),
]

def get_connection():
    return psycopg2.connect(DB_URL)

def init_db(conn):
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
                id BIGSERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                capacity INTEGER NOT NULL
            );"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS registrations (
                participant TEXT NOT NULL,
                session_id BIGINT NOT NULL REFERENCES sessions(id),
                PRIMARY KEY(participant, session_id)
            );"""
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sessions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO sessions(name, capacity) VALUES (%s, %s)", SESSION_CONFIG
        )
        conn.commit()


def get_sessions(conn) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM sessions", conn)


def get_counts(conn) -> Dict[int, int]:
    cur = conn.cursor()
    cur.execute(
        "SELECT session_id, COUNT(*) FROM registrations GROUP BY session_id"
    )
    return {row[0]: row[1] for row in cur.fetchall()}


def get_user_sessions(conn, name: str) -> List[int]:
    cur = conn.cursor()
    cur.execute(
        "SELECT session_id FROM registrations WHERE participant = %s", (name,)
    )
    return [row[0] for row in cur.fetchall()]


def update_user_sessions(conn, name: str, sessions: List[int]):
    cur = conn.cursor()
    cur.execute("DELETE FROM registrations WHERE participant = %s", (name,))
    cur.executemany(
        "INSERT INTO registrations(participant, session_id) VALUES (%s, %s)",
        [(name, s) for s in sessions],
    )
    conn.commit()


conn = get_connection()
init_db(conn)

st.title("Event-Umfrage")
name = st.text_input("Name eingeben")

if name:
    user_sessions = get_user_sessions(conn, name)
    all_sessions = get_sessions(conn)
    counts = get_counts(conn)

    # Liste für Anzeige und Auswahl vorbereiten
    available = []
    labels = {}
    for _, row in all_sessions.iterrows():
        sid = row["id"]
        count = counts.get(sid, 0)
        label = f"{row['name']} ({count}/{row['capacity']})"
        full = count >= row["capacity"]
        if not full or sid in user_sessions:
            available.append(label)
            labels[label] = sid
    default = [label for label, sid in labels.items() if sid in user_sessions]
    selected_labels = st.multiselect(
        "Wähle bis zu zwei Sessions:", options=available, default=default
    )
    selected_ids = [labels[l] for l in selected_labels]

    if len(selected_ids) > 2:
        st.error("Es dürfen maximal zwei Sessions gewählt werden.")
    else:
        # Prüfen ob eine neu gewählte Session voll ist
        errors = []
        for sid in selected_ids:
            count = counts.get(sid, 0)
            capacity = int(all_sessions[all_sessions.id == sid].iloc[0]["capacity"])
            if count >= capacity and sid not in user_sessions:
                errors.append(f"{all_sessions[all_sessions.id == sid].iloc[0]['name']} ist bereits voll.")
        if errors:
            for msg in errors:
                st.error(msg)
        else:
            if st.button("Speichern"):
                update_user_sessions(conn, name, selected_ids)
                st.success("Auswahl gespeichert")
                counts = get_counts(conn)  # aktualisieren

    st.subheader("Aktuelle Anmeldungen")
    count_data = [
        {
            "Session": row["name"],
            "Anmeldungen": counts.get(row["id"], 0),
            "Kapazität": row["capacity"],
        }
        for _, row in all_sessions.iterrows()
    ]
    st.table(pd.DataFrame(count_data))

else:
    st.info("Bitte Namen eingeben, um teilzunehmen.")
