"""
SCRIPT DE MIGRAÇÃO: copia os dados do pub.db (SQLite) para o PostgreSQL (Neon).

Rode este script UMA ÚNICA VEZ, no seu computador (VS Code), depois de já ter
criado o banco no Neon.

Como usar (no terminal, dentro da pasta do projeto):

    # 1) Instale as dependências (se ainda não instalou)
    pip install -r requirements.txt

    # 2) Cole a sua connection string do Neon aqui e rode:
    #    (No Windows PowerShell)
    $env:DATABASE_URL="postgresql://USUARIO:SENHA@HOST/NOME_DO_BANCO?sslmode=require"
    python migrar_para_postgres.py

    #    (No Mac/Linux)
    export DATABASE_URL="postgresql://USUARIO:SENHA@HOST/NOME_DO_BANCO?sslmode=require"
    python migrar_para_postgres.py

O script:
  1. Cria as tabelas no PostgreSQL (chamando init_db).
  2. Lê TODOS os dados do pub.db local.
  3. Insere no PostgreSQL, sem duplicar (se rodar de novo, ele ignora o que já existe).
"""

import os
import sqlite3

ARQUIVO_SQLITE = "pub.db"

# Tabelas na ordem correta (shows antes de reservas por causa da chave estrangeira)
TABELAS = ["mesas", "shows", "cardapio", "reservas"]


def ler_sqlite():
    if not os.path.exists(ARQUIVO_SQLITE):
        print(f"ERRO: não encontrei o arquivo '{ARQUIVO_SQLITE}' nesta pasta.")
        print("Rode este script na mesma pasta onde está o seu pub.db.")
        return None

    conn = sqlite3.connect(ARQUIVO_SQLITE)
    conn.row_factory = sqlite3.Row
    dados = {}
    for tabela in TABELAS:
        try:
            linhas = conn.execute(f"SELECT * FROM {tabela}").fetchall()
            dados[tabela] = [dict(l) for l in linhas]
        except sqlite3.OperationalError:
            dados[tabela] = []
    conn.close()
    return dados


def migrar():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERRO: a variável DATABASE_URL não está definida.")
        print("Defina ela com a connection string do Neon antes de rodar.")
        print('Exemplo (Windows): $env:DATABASE_URL="postgresql://..."')
        return

    dados = ler_sqlite()
    if dados is None:
        return

    # Importa aqui para garantir que DATABASE_URL já esteja definida
    import database
    import psycopg

    # 1) Garante que as tabelas existam no PostgreSQL
    print("-> Criando as tabelas no PostgreSQL (se necessário)...")
    database.init_db()

    conn = psycopg.connect(database_url)
    cursor = conn.cursor()

    total_geral = 0
    for tabela in TABELAS:
        linhas = dados.get(tabela, [])
        if not linhas:
            print(f"   {tabela}: nada para migrar.")
            continue

        inseridos = 0
        for linha in linhas:
            colunas = list(linha.keys())
            valores = [linha[c] for c in colunas]
            placeholders = ", ".join(["%s"] * len(colunas))
            nomes_colunas = ", ".join(colunas)
            sql = (
                f"INSERT INTO {tabela} ({nomes_colunas}) VALUES ({placeholders}) "
                f"ON CONFLICT DO NOTHING"
            )
            try:
                cursor.execute(sql, valores)
                inseridos += cursor.rowcount
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"   Aviso ao inserir em {tabela}: {e}")

        print(f"   {tabela}: {inseridos} registro(s) migrado(s).")
        total_geral += inseridos

    # 2) Ajusta as sequências (auto-incremento) do PostgreSQL para o próximo id
    for tabela in TABELAS:
        try:
            cursor.execute(
                f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {tabela}), 1))"
            )
            conn.commit()
        except Exception:
            conn.rollback()

    cursor.close()
    conn.close()
    print(f"\n-> Migração concluída! {total_geral} registro(s) copiados para o PostgreSQL.")
    print("-> Agora seus dados estão salvos permanentemente. 🎉")


if __name__ == "__main__":
    migrar()
