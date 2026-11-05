"""Agente educacional com memória curta (RAM) e longa (SQLite)."""
import os
import re
from collections import deque

SYSTEM_PROMPT = """Você é um assistente educacional prestativo. Responda em português,
com explicações claras e adequadas a um estudante. Use as memórias persistentes
como contexto, mas não invente informações que não estejam nelas ou na conversa."""

class EducationalAgent:
    def __init__(self, database, usuario="joao", client=None, model=None):
        self.database = database
        self.usuario = usuario
        self.historico = deque(maxlen=6)  # últimas seis mensagens da sessão
        self.client = client
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    def remember_from_text(self, message):
        """Reconhece pedidos simples: 'lembre que estou aprendendo SQL'."""
        patterns = [
            r"(?:quero que você )?lembre que (?:eu )?estou aprendendo (.+)",
            r"(?:quero que você )?lembre que (?:eu )?estudo (.+)",
            r"(?:guarde|salve|lembre) (?:que )?(?:meu|minha) ([\wÀ-ÿ ]+?) é (.+)",
        ]
        for index, pattern in enumerate(patterns):
            match = re.search(pattern, message.strip(), re.IGNORECASE)
            if match:
                if index < 2:
                    self.database.save_memory(self.usuario, "aprendendo", match.group(1).strip().rstrip(".!?"))
                else:
                    self.database.save_memory(self.usuario, match.group(1).strip().lower(), match.group(2).strip().rstrip(".!?"))
                return True
        return False

    def build_messages(self, user_message):
        memory_context = self.database.format_context(self.usuario)
        system = (
            f"{SYSTEM_PROMPT}\n\nMEMÓRIA DE LONGO PRAZO DO ESTUDANTE:\n{memory_context}\n\n"
            "Considere também o histórico recente abaixo. Se perguntarem sobre dados memorizados, "
            "responda usando esses dados."
        )
        messages = [{"role": "system", "content": system}]
        messages.extend(list(self.historico))
        messages.append({"role": "user", "content": user_message})
        return messages

    def ask(self, user_message):
        if self.remember_from_text(user_message):
            response = "Informação armazenada na memória de longo prazo! Ela continuará disponível quando o programa for reiniciado."
            self._add_to_history(user_message, response)
            return response

        if self.client is None:
            raise RuntimeError("Cliente Groq não configurado. Verifique GROQ_API_KEY no arquivo .env.")

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.build_messages(user_message),
            temperature=0.4,
            max_tokens=700,
        )
        response = completion.choices[0].message.content or "Não consegui gerar uma resposta."
        self._add_to_history(user_message, response)
        return response

    def _add_to_history(self, user_message, assistant_message):
        self.historico.append({"role": "user", "content": user_message})
        self.historico.append({"role": "assistant", "content": assistant_message})
