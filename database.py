import sqlite3

def get_db_connection():
    conn = sqlite3.connect('pub.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Mesas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT UNIQUE NOT NULL,
            setor TEXT NOT NULL,
            capacidade INTEGER NOT NULL
        )
    ''')
    
    # 2. Shows
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_show TEXT NOT NULL UNIQUE,
            banda TEXT NOT NULL,
            limite_capacidade INTEGER DEFAULT 150,
            visivel INTEGER DEFAULT 1
        )
    ''')
    try:
        cursor.execute("ALTER TABLE shows ADD COLUMN visivel INTEGER DEFAULT 1")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE reservas ADD COLUMN aniversario TEXT DEFAULT 'Não'")
    except Exception:
        pass
    
    # 3. Reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            show_id INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            email TEXT NOT NULL,
            qtd_pessoas INTEGER NOT NULL,
            status TEXT DEFAULT 'Pendente',
            mesas_alocadas TEXT,
            token_cancelamento TEXT UNIQUE NOT NULL,
            FOREIGN KEY (show_id) REFERENCES shows (id)
        )
    ''')
    
    # 4. Cardápio
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cardapio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            preco_meia REAL,
            disponivel INTEGER DEFAULT 1
        )
    ''')

    # Povoar Mesas se estiver vazio ou atualizar
    cursor.execute('SELECT COUNT(*) FROM mesas')
    if cursor.fetchone()[0] < 45:
        cursor.execute('DELETE FROM mesas') # Limpa para recadastrar todas perfeitamente
        
        mesas_completas = []
        # Térreo: 1 a 17 (Bistrôs 4 lug) e 18 a 22 (Mesas 6 lug)
        for i in range(1, 18):
            mesas_completas.append((str(i), 'Térreo', 4))
        for i in range(18, 23):
            mesas_completas.append((str(i), 'Térreo', 6))
            
        # Mezanino: 23 a 45 com capacidades reais
        capacidades_mezanino = {
            23: 4, 24: 4, 25: 4, 26: 4,
            27: 2, 28: 2,
            29: 6, 30: 6, 31: 6,
            32: 3, 33: 3, 34: 3, 35: 3, 36: 3, 37: 3, 38: 3, 39: 3, 40: 3,
            41: 6, 42: 6,
            43: 3,
            44: 4,
            45: 2
        }
        for num, cap in capacidades_mezanino.items():
            mesas_completas.append((str(num), 'Mezanino', cap))
            
        cursor.executemany('INSERT INTO mesas (identificacao, setor, capacidade) VALUES (?, ?, ?)', mesas_completas)
        print("-> 45 Mesas cadastradas (Térreo + Mezanino) com sucesso!")

    # Povoar Cardápio completo
    cursor.execute('SELECT COUNT(*) FROM cardapio')
    if cursor.fetchone()[0] == 0:
        itens = [
            # CHOPPS
            ('Chopps', 'Chopp Brahma 500ML', 'Chopp claro e refrescante', 17.90, None),
            ('Chopps', 'Chopp Brahma 300ML', 'Chopp claro e refrescante', 15.90, None),
            ('Chopps', 'Chopp Heineken 500ML', 'Puro malte premium', 18.90, None),
            ('Chopps', 'Chopp Heineken 300ML', 'Puro malte premium', 16.90, None),
            
            # CERVEJAS 600ML
            ('Cervejas 600ml', 'Heineken 600ML', 'Garrafa 600ml', 21.90, None),
            ('Cervejas 600ml', 'Original 600ML', 'Garrafa 600ml', 19.90, None),
            ('Cervejas 600ml', 'Spaten 600ML', 'Garrafa 600ml puro malte', 19.90, None),
            ('Cervejas 600ml', 'Baden Baden Pilsen Cristal 600ML', 'Artesanal premium', 26.00, None),

            # CERVEJAS LONG NECK & LATAS
            ('Long Neck & Latas', 'Lagunitas IPA Lata 350ML', 'India Pale Ale aromática', 16.00, None),
            ('Long Neck & Latas', 'Heineken Long Neck 330ML', 'Disponível também na versão 0% Álcool', 15.00, None),
            ('Long Neck & Latas', 'Stella Artois Long Neck 330ML', 'Disponível também na versão Sem Glúten', 15.00, None),
            ('Long Neck & Latas', 'Chá de Pinheirinho', 'Hard Tea refrescante', 16.90, None),
            ('Long Neck & Latas', 'Smirnoff ICE 275ML', 'Bebida mista refrescante', 16.00, None),
            ('Long Neck & Latas', 'Skol Beats 269ML', 'Consulte sabores disponíveis', 16.00, None),
            
            # GIN & TONICA
            ('Gins Especiais', 'Gin Tônica Tradicional Nacional', 'Gin Nacional, limão siciliano e água tônica', 32.90, None),
            ('Gins Especiais', 'Gin Tônica Tradicional Bombay', 'Gin Bombay, limão siciliano e água tônica', 37.90, None),
            ('Gins Especiais', 'Gin Nacional Melancia com Red Bull', 'Gin Nacional, melancia e Red Bull Melancia', 36.90, None),
            ('Gins Especiais', 'Gin Bombay Melancia com Red Bull', 'Gin Bombay, melancia e Red Bull Melancia', 42.90, None),
            ('Gins Especiais', 'Gin Nacional Maracujá com Red Bull', 'Gin Nacional, maracujá e Red Bull Tropical', 36.90, None),
            ('Gins Especiais', 'Gin Bombay Maracujá com Red Bull', 'Gin Bombay, maracujá e Red Bull Tropical', 42.90, None),
            ('Gins Especiais', 'Gin Tônica Frutas Nacional', 'Frutas: Morango, Amora, Melancia, Abacaxi ou Frutas Vermelhas', 34.90, None),
            ('Gins Especiais', 'Gin Tônica Frutas Bombay', 'Frutas: Morango, Amora, Melancia, Abacaxi ou Frutas Vermelhas', 39.90, None),
            ('Gins Especiais', 'GinTaya Nacional', 'Gin Nacional, pitaya e água tônica', 34.90, None),
            ('Gins Especiais', 'GinTaya Bombay Sapphire', 'Gin Bombay, pitaya e água tônica', 39.90, None),
            ('Gins Especiais', 'Gin Fake (Sem Álcool)', 'Água com gás, limão e gelo', 19.90, None),

            # COQUETÉIS
            ('Coquetéis', 'Margarita', 'Tequila, Curaçau Blue, Limão e Sal', 39.90, None),
            ('Coquetéis', 'Moscow Mule', 'Limão, água com gás, vodka e espuma de gengibre', 34.90, None),
            ('Coquetéis', 'Piña Colada', 'Suco de abacaxi, leite de coco, rum e leite condensado', 34.90, None),
            ('Coquetéis', 'Mojito Cubano', 'Rum, limão, hortelã, água com gás e açúcar', 34.90, None),
            ('Coquetéis', 'Negroni Nacional', 'Vermouth, Gin Nacional, Campari e rodelas de laranja', 34.90, None),
            ('Coquetéis', 'Negroni Bombay Sapphire', 'Vermouth, Gin Bombay Sapphire, Campari e rodelas de laranja', 39.90, None),
            ('Coquetéis', 'Dry Martini', 'Vermouth Seco, Gin e azeitona verde', 34.90, None),
            ('Coquetéis', 'Aperol Spritz', 'Aperol, espumante, laranja e água com gás', 34.90, None),
            ('Coquetéis', 'Melangibre Nacional', 'Xarope de melancia e gengibre, Gin Nacional e tônica', 39.90, None),
            ('Coquetéis', 'Melangibre Bombay Sapphire', 'Xarope de melancia e gengibre, Gin Bombay e tônica', 44.90, None),
            ('Coquetéis', 'Malibu Pineapple Frozen', 'Rum Malibu, suco de abacaxi, limão e açúcar', 34.90, None),
            ('Coquetéis', 'Coquetel de Vodka', 'Vodka, leite condensado e limão ou morango', 32.90, None),
            ('Coquetéis', 'Coquetel de Champanhe', 'Champagne, morango e leite condensado', 29.90, None),
            ('Coquetéis', 'Aperol com Melancia', 'Xarope de melancia, Aperol, champagne e fatia de laranja', 39.90, None),
            ('Coquetéis', 'Aperol com Morango', 'Xarope de morango, Aperol, champagne e fatia de laranja', 39.90, None),

            # CAIPIRINHAS (Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora e Frutas Vermelhas)
            ('Caipirinhas', 'Caipirinha Sagatiba', 'Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora ou Frutas Vermelhas', 31.90, None),
            ('Caipirinhas', 'Caipiroska Absolut', 'Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora ou Frutas Vermelhas', 37.90, None),
            ('Caipirinhas', 'Caipiroska Smirnoff', 'Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora ou Frutas Vermelhas', 33.90, None),
            ('Caipirinhas', 'Saquerinha Azuma Kirin', 'Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora ou Frutas Vermelhas', 29.90, None),
            ('Caipirinhas', 'Caipirinha Velho Barreiro', 'Sabores: Morango, Limão, Melancia, Abacaxi, Maracujá, Amora ou Frutas Vermelhas', 29.90, None),

            # DOSES
            ('Doses', 'Johnnie Walker Red Label', 'Dose', 29.90, None),
            ('Doses', 'Johnnie Walker Black Label', 'Dose', 41.90, None),
            ('Doses', 'Chivas Regal 12 anos', 'Dose', 36.90, None),
            ('Doses', 'Jack Daniel\'s', 'Dose', 39.90, None),
            ('Doses', 'Absolut Vodka', 'Dose', 27.90, None),
            ('Doses', 'Smirnoff Vodka', 'Dose', 17.90, None),
            ('Doses', 'José Cuervo - Carta Ouro', 'Dose Tequila', 29.90, None),
            ('Doses', 'José Cuervo - Carta Prata', 'Dose Tequila', 29.90, None),
            ('Doses', 'Rum Bacardi - Ouro ou Prata', 'Dose Rum', 18.90, None),
            ('Doses', 'Licor 43', 'Dose Licor Espanhol', 31.90, None),
            ('Doses', 'Jägermeister', 'Dose', 31.90, None),
            ('Doses', 'Gin Bombay Sapphire', 'Dose', 31.90, None),
            ('Doses', 'Gin Seagers (Nacional)', 'Dose', 17.90, None),
            ('Doses', 'Rum Malibu', 'Dose', 24.90, None),
            ('Doses', 'Campari / Aperol', 'Dose', 19.90, None),
            ('Doses', 'Cachaça Salinas', 'Dose', 19.90, None),
            ('Doses', 'Cachaça Sagatiba', 'Dose', 17.90, None),
            ('Doses', 'Conhaque Domecq', 'Dose', 17.90, None),
            ('Doses', 'Saquê Azuma Kirin', 'Dose', 15.90, None),

            # PORÇÕES (Com opção de Inteira e Meia Porção)
            ('Porções', 'Dadinho de Tapioca com Provolone', 'Acompanha 14 unidades (Meia: 7 unid)', 49.50, 29.90),
            ('Porções', 'Mini X-Burguer (3 unid)', '3 mini hambúrgueres com queijo e batata frita', 44.90, None),
            ('Porções', 'Bolinho de Bacalhau', 'Acompanha 15 unidades', 59.90, None),
            ('Porções', 'Bolinho de Mandioca com Camarão', 'Acompanha 15 unidades', 59.90, 34.90),
            ('Porções', 'Bolinho de Mandioca com Carne Seca', 'Acompanha 15 unidades', 54.90, 29.90),
            ('Porções', 'Kibe recheado com Queijo', 'Acompanha 10 unidades', 54.90, 29.90),
            ('Porções', 'Calabresa Acebolada', 'Calabresa frita acebolada. Acompanha maionese e pão', 49.90, None),
            ('Porções', 'Mini Pastel (16 unid)', 'Sabores: Carne e Queijo', 44.90, 24.90),
            ('Porções', 'Batata Frita Tradicional', 'Porção crocante', 49.90, 29.90),
            ('Porções', 'Batata Frita com Cheddar', 'Cheddar cremoso derretido', 54.90, 34.90),
            ('Porções', 'Batata Frita com Muçarela', 'Muçarela gratinada', 54.90, 34.90),
            ('Porções', 'Filé de Frango Acebolado', 'Acompanha vinagrete, farofa e pão', 54.90, None),
            ('Porções', 'Filé de Frango com Polenta', 'Acompanha vinagrete, farofa, pão e polenta', 69.90, 44.90),
            ('Porções', 'Contra Filé Acebolado', 'Acompanha vinagrete, farofa e pão', 89.90, None),
            ('Porções', 'Contra Filé Acebolado com Fritas', 'Acompanha vinagrete, farofa, pão e fritas', 119.90, 59.90),
            ('Porções', 'Croquete de Picanha', 'Acompanha 15 unidades', 54.90, 29.90),
            ('Porções', 'Polenta Frita Tradicional', 'Polenta crocante por fora e macia por dentro', 44.90, 29.90),
            ('Porções', 'Polenta Frita com Muçarela', 'Com queijo muçarela gratinado', 54.90, 34.90),

            # NÃO ALCOÓLICOS & SUCOS
            ('Não Alcoólicos', 'Refrigerantes Lata 350ML', 'Coca-Cola, Zero, Guaraná, Guaraná Zero, Tônica, Tônica Zero, Citrus', 7.90, None),
            ('Não Alcoólicos', 'Red Bull 255ML', 'Tradicional, Zero, Frutas Tropicais ou Melancia', 16.90, None),
            ('Não Alcoólicos', 'Água Mineral sem gás 500ML', 'Crystal 500ml', 5.00, None),
            ('Não Alcoólicos', 'Água Mineral com gás 500ML', 'Crystal 500ml', 6.50, None),
            ('Não Alcoólicos', 'Sucos Naturais', 'Morango, Abacaxi, Maracujá ou Limão', 12.00, None),
            ('Não Alcoólicos', 'Suco de Morango com Leite Condensado', 'Morango batido com leite condensado e gelo', 16.00, None),
            ('Não Alcoólicos', 'Limonada Suíça', 'Limão com leite condensado e gelo', 16.00, None),

            # VINHOS & SOBREMESA
            ('Vinhos & Sobremesa', 'Garrafa Vinho Concha y Toro', 'Chileno: Cabernet Sauvignon, Merlot, Malbec ou Carmenére', 79.90, None),
            ('Vinhos & Sobremesa', 'Petit Gateau', 'Bolinho quente de chocolate com uma bola de sorvete de creme', 24.90, None)
        ]
        
        cursor.executemany('''
            INSERT INTO cardapio (categoria, nome, descricao, preco, preco_meia)
            VALUES (?, ?, ?, ?, ?)
        ''', itens)
        print("-> Cardápio completo cadastrado com sucesso!")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()