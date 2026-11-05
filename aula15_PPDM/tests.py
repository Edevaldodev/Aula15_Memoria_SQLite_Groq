"""Testes locais sem precisar chamar a API da Groq."""
import tempfile
import unittest
from pathlib import Path
from database import MemoryDatabase
from agent import EducationalAgent

class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "teste.db"
        self.db = MemoryDatabase(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_recover(self):
        self.db.save_memory("joao", "linguagem", "Python")
        self.assertEqual(self.db.get_memory("joao", "linguagem"), "Python")

    def test_update_existing_memory(self):
        self.db.save_memory("joao", "nível", "Iniciante")
        self.assertTrue(self.db.update_memory("joao", "nível", "Intermediário"))
        self.assertEqual(self.db.get_memory("joao", "nível"), "Intermediário")

    def test_unique_user_key(self):
        self.db.save_memory("joao", "curso", "Curso A")
        self.db.save_memory("joao", "curso", "Curso B")
        self.assertEqual(self.db.get_memory("joao", "curso"), "Curso B")
        self.assertEqual(len(self.db.get_memories("joao")), 1)

    def test_short_term_keeps_six_messages(self):
        agent = EducationalAgent(self.db)
        for number in range(4):
            agent._add_to_history(f"pergunta {number}", f"resposta {number}")
        self.assertEqual(len(agent.historico), 6)
        self.assertEqual(agent.historico[0]["content"], "pergunta 1")

    def test_remember_request(self):
        agent = EducationalAgent(self.db)
        answer = agent.ask("Quero que você lembre que estou aprendendo SQL.")
        self.assertIn("armazenada", answer)
        self.assertEqual(self.db.get_memory("joao", "aprendendo"), "SQL")

if __name__ == "__main__":
    unittest.main(verbosity=2)
