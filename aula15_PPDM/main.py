"""Interface de terminal do projeto Aula 15."""
import os
from dotenv import load_dotenv
from groq import Groq
from database import MemoryDatabase
from agent import EducationalAgent


def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("ERRO: configure sua GROQ_API_KEY no arquivo .env (veja .env.example).")
        return

    usuario = os.getenv("STUDENT_ID", "joao").strip() or "joao"
    database = MemoryDatabase()
    database.seed_if_empty(usuario)
    client = Groq(api_key=api_key)
    agent = EducationalAgent(database, usuario, client)

    print("=" * 58)
    print("       ASSISTENTE EDUCACIONAL — AULA 15")
    print(" Memória curta: últimas 6 mensagens | Longa: SQLite")
    print("=" * 58)
    print(f"Estudante: {usuario}")
    print("Comandos: /memorias | /atualizar chave=valor | /excluir chave | /sair")
    print("Exemplo: Quero que você lembre que estou aprendendo SQL.\n")

    while True:
        try:
            message = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando. A memória persistente foi mantida no SQLite.")
            break
        if not message:
            continue
        lower = message.lower()
        if lower in {"/sair", "sair", "exit", "quit"}:
            print("Até a próxima! Os dados do SQLite continuam salvos.")
            break
        if lower == "/memorias":
            print("\nMEMÓRIA DE LONGO PRAZO")
            print(database.format_context(usuario), "\n", sep="\n")
            continue
        if lower.startswith("/atualizar "):
            payload = message[len("/atualizar "):]
            if "=" not in payload:
                print("Use: /atualizar chave=novo valor")
                continue
            key, value = payload.split("=", 1)
            if database.update_memory(usuario, key.strip(), value.strip()):
                print("Informação atualizada no SQLite.")
            else:
                database.save_memory(usuario, key.strip(), value.strip())
                print("Chave não existia; informação cadastrada no SQLite.")
            continue
        if lower.startswith("/excluir "):
            key = message[len("/excluir "):].strip()
            print("Memória excluída." if database.delete_memory(usuario, key) else "Chave não encontrada.")
            continue
        try:
            print(f"Agente: {agent.ask(message)}\n")
        except Exception as exc:
            print(f"Não foi possível consultar a Groq: {exc}\n")


if __name__ == "__main__":
    main()
