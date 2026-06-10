from __future__ import annotations
import hashlib, secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from contextlib import contextmanager
import sqlite3

# ── Data Models ─────────────────────────────────────
@dataclass
class User:
    username: str
    password_hash: str
    balance: float
    role: str = "customer"
    id: Optional[int] = None

@dataclass
class Transaction:
    user_id: int
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""

# ── Database Layer ───────────────────────────────────
class Database:
    def __init__(self, db_path: str):
        self._path = db_path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0,
                    role    TEXT NOT NULL DEFAULT 'customer'
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES users(id),
                    amount  REAL NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                );
            """)

# ── Security Utilities ──────────────────────────────
class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        salt = secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
        return f"{salt}${h.hex()}"

    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        salt, expected = stored_hash.split("$")
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
        return secrets.compare_digest(h.hex(), expected)

# ── Repository (Data Access) ────────────────────────
class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, user: User) -> User:
        with self._db.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash, balance, role) VALUES (?,?,?,?)",
                (user.username, user.password_hash, user.balance, user.role)
            )
            return User(**{**user.__dict__, "id": cursor.lastrowid})

    def find_by_username(self, username: str) -> Optional[User]:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            return User(**dict(row)) if row else None

# ── Service Layer (Business Logic) ──────────────────
class StoreService:
    def __init__(self, db: Database, user_repo: UserRepository):
        self._db = db
        self._users = user_repo

    def register_user(self, username: str, password: str,
                      initial_balance: float = 0.0) -> User:
        hashed = PasswordHasher.hash(password)
        return self._users.create(User(username, hashed, initial_balance))

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self._users.find_by_username(username)
        if user and PasswordHasher.verify(password, user.password_hash):
            return user
        return None

    def purchase(self, username: str, amount: float,
                 description: str = "") -> Transaction:
        user = self._users.find_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        if user.balance < amount:
            raise ValueError(f"Insufficient balance: {user.balance:.2f} < {amount:.2f}")

        with self._db.connection() as conn:
            conn.execute(
                "UPDATE users SET balance = balance - ? WHERE id = ?",
                (amount, user.id)
            )
            tx = Transaction(user.id, amount, description=description)
            conn.execute(
                "INSERT INTO transactions (user_id,amount,description,created_at) VALUES (?,?,?,?)",
                (tx.user_id, tx.amount, tx.description, tx.timestamp.isoformat())
            )
        return tx

    def get_sales_report(self) -> dict:
        with self._db.connection() as conn:
            rows = conn.execute("SELECT amount FROM transactions").fetchall()
        if not rows:
            return {"total": 0.0, "average": 0.0, "count": 0}
        amounts = [r["amount"] for r in rows]
        return {
            "total":   round(sum(amounts), 2),
            "average": round(sum(amounts) / len(amounts), 2),
            "count":   len(amounts),
        }

# ── Dependency Injection / Entry Point ──────────────
def create_store(db_path: str = "store.db") -> StoreService:
    db   = Database(db_path)
    db.initialize()
    repo = UserRepository(db)
    return StoreService(db, repo)

if __name__ == "__main__":
    store = create_store()
    user  = store.register_user("ahmed", "s3cur3P@ss", balance=500.0)
    tx    = store.purchase("ahmed", 120.0, "MacBook Pro case")
    print(store.get_sales_report())
