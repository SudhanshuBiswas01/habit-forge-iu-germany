import sqlite3
from datetime import datetime

from habit import Habit


class Database:
    def __init__(self, db_path="habits.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.initialize_tables()

    def initialize_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                periodicity TEXT,
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER REFERENCES habits(habit_id),
                completed_at TEXT
            )
        """)
        self.conn.commit()

    def save_habit(self, habit):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
            (
                habit.name,
                habit.description,
                habit.periodicity,
                habit.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        habit.habit_id = cur.lastrowid
        return habit.habit_id

    def delete_habit(self, habit_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        cur.execute("DELETE FROM habits WHERE habit_id = ?", (habit_id,))
        self.conn.commit()

    def load_all_habits(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT habit_id, name, description, periodicity, created_at FROM habits"
        )
        rows = cur.fetchall()
        habits = []
        for row in rows:
            habits.append(
                Habit(
                    name=row[1],
                    description=row[2] or "",
                    periodicity=row[3],
                    habit_id=row[0],
                    created_at=datetime.fromisoformat(row[4]),
                )
            )
        return habits

    def save_completion(self, habit_id, completed_at):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, completed_at.isoformat()),
        )
        self.conn.commit()

    def load_completions(self, habit_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at",
            (habit_id,),
        )
        return [datetime.fromisoformat(row[0]) for row in cur.fetchall()]

    def is_empty(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM habits")
        return cur.fetchone()[0] == 0

    def close(self):
        if self.conn:
            self.conn.close()
