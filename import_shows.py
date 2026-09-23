from database import get_db_connection

shows_agenda = [
    # SETEMBRO/2026
    ("2026-09-04", "X-Rock"),
    ("2026-09-05", "Monny"),
    ("2026-09-11", "Core"),
    ("2026-09-12", "Echoes"),
    ("2026-09-18", "Classic Zoom"),
    ("2026-09-19", "Kaleidoscope"),
    ("2026-09-25", "Lost Dogs"),
    ("2026-09-26", "Bon Jovi"),

    # OUTUBRO/2026
    ("2026-10-02", "Radio Galena"),
    ("2026-10-03", "Velotroll"),
    ("2026-10-09", "Makina La"),
    ("2026-10-10", "Hot Rocks"),
    ("2026-10-16", "Old Chevy"),
    ("2026-10-17", "Cinner"),
    ("2026-10-23", "Sonic Boom"),
    ("2026-10-24", "Rock Collection"),
    ("2026-10-30", "Mr Legacy"),
    ("2026-10-31", "Monny"),

    # NOVEMBRO/2026
    ("2026-11-06", "X-Rock"),
    ("2026-11-07", "7 Cidades"),
    ("2026-11-13", "Rock Collection"),
    ("2026-11-14", "Dom Paulinho"),
    ("2026-11-19", "Allstar 40 (Véspera de Feriado)"),
    ("2026-11-20", "Kaleidoscope"),
    ("2026-11-21", "Velotroll"),
    ("2026-11-27", "Classic Zoom"),
    ("2026-11-28", "Core"),

    # DEZEMBRO/2026
    ("2026-12-04", "Radio Galena"),
    ("2026-12-05", "Monny"),
    ("2026-12-11", "Makina La"),
    ("2026-12-12", "Lost Dogs"),
    ("2026-12-18", "Hot Rocks"),
    ("2026-12-19", "X-Rock (Última do ano/26)"),
    # Férias até 08/01/2027
]

def importar():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_inseridos = 0
    for data_show, banda in shows_agenda:
        try:
            cursor.execute("""
                INSERT INTO shows (data_show, banda, limite_capacidade, visivel)
                VALUES (?, ?, 150, 1)
            """, (data_show, banda))
            total_inseridos += 1
        except Exception:
            # Se já existir, apenas ignora para não duplicar
            pass

    conn.commit()
    conn.close()
    print(f"-> Sucesso! {total_inseridos} shows foram adicionados à agenda do Pub!")

if __name__ == "__main__":
    importar()
