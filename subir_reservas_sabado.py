"""
SUBIR AS RESERVAS DO SÁBADO — Show BON JOVI EXPERIENCE — 26/09/2026.

O que este script faz:
  1. Encontra o show do Bon Jovi Experience pela data.
  2. APAGA as reservas de TESTE que estiverem nesse show.
  3. Insere as 26 reservas confirmadas, todas com status 'Aprovada'.

É seguro rodar mais de uma vez: antes de inserir, ele limpa as reservas do show
e recadastra do zero (assim nunca duplica). Só mexe neste show.

Como usar (no terminal, dentro da pasta do projeto):

    # Para subir no banco de PRODUÇÃO (Neon), defina a DATABASE_URL antes:
    #   Windows: $env:DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"
    #   Mac/Linux: export DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"
    # Sem DATABASE_URL, ele usa o pub.db local.

    python subir_reservas_sabado.py
"""

import secrets
from database import get_db_connection, init_db

# Data do show na agenda (Bon Jovi Experience — sábado 26/09/2026)
DATA_SHOW = "2026-09-26"

# Reservas confirmadas: (nome_cliente, qtd_pessoas, mesas_alocadas, aniversario)
# Obs.: algumas mesas ficam com mais gente do que a capacidade oficial
# (ajuste feito na hora pela equipe) — Ivan (26), Renata (37), Saulo (38),
# Erika Oliveira (39). Isso é intencional.
RESERVAS = [
    ("Leandro",          4, "17",       "Não"),
    ("Henrique",         2, "12",       "Não"),
    ("Fabiana Candido",  6, "4,5",      "Não"),
    ("Lia",              8, "1,2",      "Não"),
    ("Gabi",             3, "6",        "Não"),
    ("Clelia",           3, "7",        "Não"),
    ("Giovani",          2, "8",        "Não"),
    ("Jacqueline",       2, "3",        "Não"),
    ("Fabiana Oliveira", 4, "13",       "Não"),
    ("Graciela",         2, "16",       "Não"),
    ("Edivaldo",         4, "9",        "Não"),
    ("Erika",            2, "10",       "Não"),
    ("Luciene",          2, "11",       "Não"),
    ("Rosana",          10, "18,19",    "Sim"),   # lado esquerdo frente palco - aniversário
    ("Thais",            6, "20",       "Não"),   # lado esquerdo
    ("Lorrene",          6, "21",       "Não"),   # lado esquerdo
    ("Thania",           2, "28",       "Não"),   # mezanino lado esquerdo grade
    ("João",             2, "23",       "Não"),   # mezanino frente
    ("Angelica",         4, "24",       "Não"),   # mezanino frente
    ("Edinei",           2, "25",       "Não"),   # mezanino frente
    ("Ivan",             6, "26",       "Não"),   # mezanino frente (ajusta no dia)
    ("Carmen",          15, "41,42,43", "Sim"),   # bilhar - aniversário
    ("Dekalaf",         15, "29,30,31", "Sim"),   # mezanino lado esquerdo - aniversário
    ("Renata",           4, "37",       "Não"),   # frente (ajusta no dia)
    ("Saulo",            4, "38",       "Não"),   # frente (ajusta no dia)
    ("Erika Oliveira",   6, "39",       "Não"),   # frente (ajusta no dia)
]


def subir():
    # Garante que as tabelas existem
    init_db()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Localiza o show do Bon Jovi Experience
    cursor.execute("SELECT id, banda FROM shows WHERE data_show = ?", (DATA_SHOW,))
    show = cursor.fetchone()
    if not show:
        print(f"ERRO: não encontrei nenhum show na data {DATA_SHOW}.")
        print("Rode o import_shows.py antes, ou confira a data da agenda.")
        conn.close()
        return

    show_id = show["id"]
    print(f"-> Show encontrado: {show['banda']} (id={show_id}, {DATA_SHOW})")

    # 2. Apaga as reservas existentes desse show (limpa testes antes de recadastrar)
    cursor.execute("DELETE FROM reservas WHERE show_id = ?", (show_id,))
    conn.commit()
    print("-> Reservas antigas removidas deste show.")

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

    print(f"-> Sucesso! {inseridas} reservas cadastradas no show do Bon Jovi Experience.")
    print(f"-> Total de pessoas: {total_pessoas}")


if __name__ == "__main__":
    subir()
