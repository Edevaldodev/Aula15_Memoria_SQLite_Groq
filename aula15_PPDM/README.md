# Aula 15 — Agente com memória de curto e longo prazo

Projeto da atividade prática do PDF **Memória de Curto e Longo Prazo: Armazenamento e Recuperação com SQLite**.

## Funcionalidades implementadas

- **Memória de curto prazo:** histórico em uma `deque` Python, limitado às últimas seis mensagens (mensagens do usuário e do agente).
- **Memória de longo prazo:** banco local `memoria.db`, com tabela `memorias` e restrição `UNIQUE(usuario, chave)`.
- **SQLite/SQL:** `CREATE TABLE`, `INSERT ... ON CONFLICT`, `SELECT`, `UPDATE` e `DELETE`.
- **Groq API:** envia ao modelo o contexto persistente recuperado do SQLite e o histórico da sessão.
- **Persistência:** os dados continuam no arquivo `.db` após fechar e reabrir o programa.
- **Cadastro por solicitação:** reconhece frases como “Quero que você lembre que estou aprendendo SQL”.
- **Atualização:** comando `/atualizar nível=Intermediário`.

## Estrutura

```text
aula15_sqlite_memoria/
├── agent.py          # Agente e memória de curto prazo
├── database.py       # Memória de longo prazo com SQLite
├── main.py           # Interface de terminal + Groq API
├── tests.py          # Testes automatizados locais
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Como executar no Windows

1. Instale Python 3.10 ou superior.
2. Abra o CMD dentro da pasta do projeto.
3. (Opcional, recomendado) Crie e ative um ambiente virtual:

```bat
python -m venv .venv
.venv\Scripts\activate
```

4. Instale as dependências:

```bat
pip install -r requirements.txt
```

5. Faça uma cópia de `.env.example` com o nome `.env` e coloque sua chave da Groq em `GROQ_API_KEY`.
6. Execute:

```bat
python main.py
```

O modelo padrão está configurado como `openai/gpt-oss-20b`. Se necessário, altere `GROQ_MODEL` no `.env` para outro modelo disponível na sua conta Groq.

## Comandos do assistente

- `/memorias` — mostra as informações persistentes.
- `/atualizar nível=Intermediário` — atualiza o nível do estudante.
- `/excluir objetivo` — remove uma informação persistente.
- `/sair` — encerra o programa sem apagar o banco.

Também é possível pedir em linguagem natural: `Quero que você lembre que estou aprendendo SQL.`

## Testes

Os testes não precisam de chave da Groq, pois verificam a camada SQLite e o gerenciamento do histórico:

```bat
python -m unittest -v tests
```

## Roteiro de validação solicitado no PDF

1. Inicie o programa e consulte `/memorias`: os dados de exemplo (João, Desenvolvimento de Sistemas, Python, Iniciante e Aprender programação) são cadastrados na primeira execução.
2. Pergunte: `Qual linguagem estou estudando?` — o contexto persistente informa Python ao modelo.
3. Pergunte: `Qual é o meu curso?` — o contexto informa Desenvolvimento de Sistemas.
4. Atualize: `/atualizar nível=Intermediário`.
5. Consulte `/memorias` para confirmar a alteração.
6. Digite `/sair` e execute `python main.py` novamente.
7. Consulte `/memorias`: os dados continuam disponíveis. O histórico de conversa, por outro lado, começa vazio.
8. Digite: `Quero que você lembre que estou aprendendo SQL.`. Feche e reabra o programa; depois pergunte `O que estou aprendendo?`.

## Observações

- A chave da API fica somente no `.env`; não compartilhe esse arquivo.
- O histórico curto é mantido em RAM e não é salvo no SQLite. Ao reiniciar, ele é perdido intencionalmente.
- As informações de longo prazo ficam no arquivo `memoria.db`, criado automaticamente.
- A chamada real à Groq depende de internet, chave válida, saldo/limites e disponibilidade do modelo configurado.
