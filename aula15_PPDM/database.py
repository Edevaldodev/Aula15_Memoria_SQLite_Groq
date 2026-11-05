"""Camada de persistência: memória de longo prazo em SQLite."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("memoria.db")

class MemoryDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL,
                    chave TEXT NOT NULL,
                    valor TEXT NOT NULL,
                    UNIQUE(usuario, chave)
                )
            """)
            conn.commit()

    def save_memory(self, usuario, chave, valor):
        """Insere ou substitui a memória de mesma chave para o usuário."""
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO memorias (usuario, chave, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario, chave) DO UPDATE SET valor = excluded.valor
            """, (usuario, chave.strip().lower(), valor.strip()))
            conn.commit()

    def seed_if_empty(self, usuario="joao"):
        """Cadastra os dados de exemplo do PDF apenas na primeira execução."""
        exemplos = {
            "nome": "João",
            "curso": "Desenvolvimento de Sistemas",
            "linguagem": "Python",
            "nível": "Iniciante",
            "objetivo": "Aprender programação",
        }
        with self.connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM memorias WHERE usuario = ?", (usuario,)
            ).fetchone()[0]
            if total == 0:
                conn.executemany(
                    "INSERT OR IGNORE INTO memorias (usuario, chave, valor) VALUES (?, ?, ?)",
                    [(usuario, k, v) for k, v in exemplos.items()],
                )
                conn.commit()

    def get_memories(self, usuario):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT chave, valor FROM memorias WHERE usuario = ? ORDER BY id",
                (usuario,),
            ).fetchall()
        return [(row["chave"], row["valor"]) for row in rows]

    def get_memory(self, usuario, chave):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT valor FROM memorias WHERE usuario = ? AND chave = ?",
                (usuario, chave.strip().lower()),
            ).fetchone()
        return row["valor"] if row else None

    def update_memory(self, usuario, chave, valor):
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE memorias SET valor = ? WHERE usuario = ? AND chave = ?",
                (valor.strip(), usuario, chave.strip().lower()),
            )
            conn.commit()
        return cursor.rowcount > 0

    def delete_memory(self, usuario, chave):
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM memorias WHERE usuario = ? AND chave = ?",
                (usuario, chave.strip().lower()),
            )
            conn.commit()
        return cursor.rowcount > 0

    def format_context(self, usuario):
        memories = self.get_memories(usuario)
        if not memories:
            return "Nenhuma informação persistente cadastrada."
        return "\n".join(f"{chave}: {valor}" for chave, valor in memories)
