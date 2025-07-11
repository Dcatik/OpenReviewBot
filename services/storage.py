import sqlite3
from datetime import datetime


class Storage:
    def __init__(self, db_name="reviews.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    registration_date TEXT
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    user_id INTEGER,
                    rating INTEGER,
                    review_text TEXT,
                    status TEXT,
                    date TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies (company_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """
            )

    def add_user(self, user_id: int, username: str):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, registration_date) VALUES (?, ?, ?)",
                (user_id, username, datetime.now().isoformat()),
            )

    def get_all_companies(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM companies").fetchall()

    def get_reviews_by_company_name(self, company_name: str):
        with self.conn:
            return self.conn.execute(
                """
                SELECT r.* FROM reviews r
                JOIN companies c ON r.company_id = c.company_id
                WHERE c.name = ? AND r.status = 'approved'
                """,
                (company_name,),
            ).fetchall()

    def get_or_create_company(self, company_name: str) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT company_id FROM companies WHERE name = ?", (company_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
                return cursor.lastrowid

    def add_review(self, company_id: int, user_id: int, rating: int, review_text: str) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO reviews (company_id, user_id, rating, review_text, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    company_id,
                    user_id,
                    rating,
                    review_text,
                    "pending",
                    datetime.now().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_pending_review(self):
        with self.conn:
            return self.conn.execute(
                """
                SELECT r.review_id, c.name, r.rating, r.review_text, u.username
                FROM reviews r
                JOIN companies c ON r.company_id = c.company_id
                JOIN users u ON r.user_id = u.user_id
                WHERE r.status = 'pending'
                ORDER BY r.date
                LIMIT 1
                """
            ).fetchone()

    def approve_review(self, review_id: int):
        with self.conn:
            self.conn.execute(
                "UPDATE reviews SET status = 'approved' WHERE review_id = ?", (review_id,)
            )

    def reject_review(self, review_id: int):
        with self.conn:
            self.conn.execute(
                "UPDATE reviews SET status = 'rejected' WHERE review_id = ?", (review_id,)
            )

    def get_review_by_id(self, review_id: int) -> dict:
        with self.conn:
            result = self.conn.execute(
                """
                SELECT c.name, r.rating, r.review_text, u.username, r.date
                FROM reviews r
                JOIN companies c ON r.company_id = c.company_id
                JOIN users u ON r.user_id = u.user_id
                WHERE r.review_id = ?
                """,
                (review_id,),
            ).fetchone()
            if result:
                return {
                    "company_name": result[0],
                    "rating": result[1],
                    "review_text": result[2],
                    "username": result[3],
                    "date": result[4],
                }
            return {}

def get_company_recommendations(self):
        with self.conn:
            return self.conn.execute(
                """
                SELECT c.name, AVG(r.rating)
                FROM companies c
                JOIN reviews r ON c.company_id = r.company_id
                WHERE r.status = 'approved'
                GROUP BY c.name
                """
            ).fetchall()

storage = Storage()