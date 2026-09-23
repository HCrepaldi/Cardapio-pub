"""
SUBIR AS RESERVAS DA SEXTA — Show LOST DOGS (Pearl Jam Cover) — 12/12/2026.

O que este script faz:
  1. Encontra o show do Lost Dogs pela data.
  2. APAGA as reservas de TESTE que estiverem nesse show (a antiga era teste).
  3. Insere as 26 reservas confirmadas, todas com status 'Aprovada'.

É seguro rodar mais de uma vez: antes de inserir, ele limpa as reservas do show
e recadastra do zero (assim nunca duplica).

Como usar (no terminal, dentro da pasta do projeto):

    # Para subir no banco de PRODUÇÃO (Neon), defina a DATABASE_URL antes:
    #   Windows: $env:DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"
    #   Mac/Linux: export DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"
    # Sem DATABASE_URL, ele usa o pub.db local.

    python subir_reservas_sexta.py
"""

import secrets
from database import get_db_connection, init_db

# Data do show na agenda (Lost Dogs / Pearl Jam Cover)
DATA_SHOW = "2026-12-12"

# Reservas confirmadas: (nome_cliente, qtd_pessoas, mesas_alocadas, aniversario)
RESERVAS = [
    ("Camila",            8, "3,4",   "Não"),
    ("Elaine",            2, "5",     "Sim"),   # aniversário
    ("Gabi",              3, "6",     "Não"),
    ("Giovani",           2, "1",     "Não"),
    ("Vanessa",           2, "7",     "Não"),
    ("Andrielly",         3, "8",     "Não"),
    ("Alessandra",        4, "9",     "Não"),
    ("Thiago",            2, "11",    "Não"),
    ("Danny",             2, "2",     "Não"),
    ("Renata",            4, "17",    "Não"),
    ("Simone",            4, "16",    "Não"),
    ("Felipe",            6, "18",    "Não"),
    ("Cristiane",         4, "19",    "Não"),
    ("Lais",              6, "20",    "Não"),   # lado esquerdo
    ("Claudia Yara",      8, "12,13", "Não"),   # frente escada (2 mesas juntas)
    ("Claudia Fernandes", 4, "14",    "Não"),   # bistrô
    ("Thais Katetina",    2, "27",    "Não"),   # mezanino frente (térreo estava lotado)
    ("Eli",               8, "21,22", "Não"),   # lado esquerdo
    ("Meire",             4, "10",    "Não"),
    ("Vanessa",           2, "15",    "Não"),   # a 2ª Vanessa (bistrô no térreo)
    ("Vasthi",            4, "26",    "Não"),   # mezanino frente
    ("Pakal",             2, "25",    "Não"),   # mezanino frente
    ("Rafael",            8, "24,23", "Não"),   # mezanino frente
    ("Rodrigo",           2, "34",    "Não"),   # mezanino frente
    ("Alex",              8, "42,43", "Não"),   # bilhar
    ("Carolina",          4, "41",    "Não"),   # bilhar
]


def subir():
    # Garante que as tabelas existem
    init_db()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Localiza o show do Lost Dogs
    cursor.execute("SELECT id, banda FROM shows WHERE data_show = ?", (DATA_SHOW,))
    show = cursor.fetchone()
    if not show:
        print(f"ERRO: não encontrei nenhum show na data {DATA_SHOW}.")
        print("Rode o import_shows.py antes, ou confira a data da agenda.")
        conn.close()
        return

    show_id = show["id"]
    print(f"-> Show encontrado: {show['banda']} (id={show_id}, {DATA_SHOW})")

    # 2. Apaga as reservas existentes desse show (a antiga era teste)
    cursor.execute("DELETE FROM reservas WHERE show_id = ?", (show_id,))
    conn.commit()
    print("-> Reservas antigas (teste) removidas deste show.")

    # 3. Insere as reservas confirmadas
    inseridas = 0
    total_pessoas = 0
    for nome, qtd, mesas, aniversario in RESERVAS:
        codigo = f"#NBT-{secrets.token_hex(2).upper()}"
        token = secrets.token_urlsafe(8)
        cursor.execute("""
            INSERT INTO reservas
                (codigo, show_id, nome_cliente, whatsapp, email, qtd_pessoas,
                 status, aniversario, mesas_alocadas, token_cancelamento)
            VALUES (?, ?, ?, '-', '-', ?, 'Aprovada', ?, ?, ?)
        """, (codigo, show_id, nome, qtd, aniversario, mesas, token))
        inseridas += 1
        total_pessoas += qtd

    conn.commit()
    conn.close()

    print(f"-> Sucesso! {inseridas} reservas cadastradas no show do Lost Dogs.")
    print(f"-> Total de pessoas: {total_pessoas}")


if __name__ == "__main__":
    subir()
