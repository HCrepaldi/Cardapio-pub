from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import secrets
from database import get_db_connection, init_db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SENHA_ADMIN = "Giovani57@"

@app.on_event("startup")
def startup():
    init_db()

# --- SEGURANÇA / SESSÃO DA FLÁVIA ---
def verificar_autenticacao(request: Request):
    token = request.cookies.get("admin_session")
    if token != "autenticado_flavia_pub":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"}
        )
    return True

@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request, erro: str = None):
    return templates.TemplateResponse(request=request, name="login.html", context={"erro": erro})

@app.post("/login")
def processar_login(senha: str = Form(...)):
    if senha == SENHA_ADMIN:
        response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="admin_session", value="autenticado_flavia_pub", httponly=True)
        return response
    return RedirectResponse(url="/login?erro=1", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="admin_session")
    return response

# --- 1. PÁGINA PRINCIPAL PÚBLICA: O CARDÁPIO DIGITAL (ROTA '/') ---
@app.get("/", response_class=HTMLResponse)
@app.get("/cardapio", response_class=HTMLResponse)
def home_cardapio(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT categoria FROM cardapio WHERE disponivel = 1")
    categorias_brutas = [row["categoria"] for row in cursor.fetchall()]
    
    ordem_preferida = [
        'Chopps', 'Cervejas 600ml', 'Long Neck & Latas', 'Gins Especiais', 
        'Coquetéis', 'Caipirinhas', 'Doses', 'Porções', 'Não Alcoólicos', 'Vinhos & Sobremesa'
    ]
    categorias = [c for c in ordem_preferida if c in categorias_brutas]
    
    cursor.execute("SELECT * FROM cardapio WHERE disponivel = 1 ORDER BY id ASC")
    todos_itens = cursor.fetchall()
    
    cardapio_por_categoria = {cat: [i for i in todos_itens if i["categoria"] == cat] for cat in categorias}
    conn.close()
    
    return templates.TemplateResponse(
        request=request,
        name="cardapio.html",
        context={"cardapio": cardapio_por_categoria, "categorias": categorias}
    )

# --- 2. PAINEL DE GESTÃO DA FLÁVIA E DO CAIXA (ROTA '/admin') ---
@app.get("/admin", response_class=HTMLResponse)
def painel_admin(request: Request, show_id: int = None, auth: bool = Depends(verificar_autenticacao)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    shows = cursor.execute("SELECT * FROM shows ORDER BY data_show DESC").fetchall()
    
    if not show_id and shows:
        show_id = shows[0]["id"]
        
    reservas = []
    show_selecionado = None
    mesas_ocupadas = []
    total_pessoas = 0
    
    if show_id:
        cursor.execute("SELECT * FROM shows WHERE id = ?", (show_id,))
        show_selecionado = cursor.fetchone()
        
        cursor.execute("SELECT * FROM reservas WHERE show_id = ? ORDER BY id DESC", (show_id,))
        reservas = cursor.fetchall()

        for r in reservas:
            if r["status"] == "Aprovada":
                total_pessoas += r["qtd_pessoas"]
                if r["mesas_alocadas"]:
                    for m in r["mesas_alocadas"].split(","):
                        mesas_ocupadas.append(m.strip())
        
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "shows": shows, 
            "show_atual": show_selecionado, 
            "reservas": reservas,
            "mesas_ocupadas": mesas_ocupadas,
            "total_pessoas": total_pessoas
        }
    )

# Flávia cadastra uma nova reserva vinda do Instagram
@app.post("/admin/reservas/nova")
def cadastrar_reserva_manual(
    show_id: int = Form(...),
    nome_cliente: str = Form(...),
    whatsapp: str = Form(""),
    qtd_pessoas: int = Form(...),
    aniversario: str = Form("Não"),
    mesas_alocadas: str = Form(...),
    auth: bool = Depends(verificar_autenticacao)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    codigo = f"#NBT-{secrets.token_hex(2).upper()}"
    token_fake = secrets.token_urlsafe(8)
    
    cursor.execute("""
        INSERT INTO reservas (codigo, show_id, nome_cliente, whatsapp, email, qtd_pessoas, status, aniversario, mesas_alocadas, token_cancelamento)
        VALUES (?, ?, ?, ?, '-', ?, 'Aprovada', ?, ?, ?)
    """, (codigo, show_id, nome_cliente, whatsapp, qtd_pessoas, aniversario, mesas_alocadas, token_fake))
    
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/admin?show_id={show_id}", status_code=status.HTTP_303_SEE_OTHER)

# Flávia EDITA uma reserva existente
@app.post("/admin/reservas/editar")
def editar_reserva(
    reserva_id: int = Form(...),
    nome_cliente: str = Form(...),
    whatsapp: str = Form(""),
    qtd_pessoas: int = Form(...),
    aniversario: str = Form("Não"),
    mesas_alocadas: str = Form(...),
    auth: bool = Depends(verificar_autenticacao)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE reservas 
        SET nome_cliente = ?, whatsapp = ?, qtd_pessoas = ?, aniversario = ?, mesas_alocadas = ?
        WHERE id = ?
    """, (nome_cliente, whatsapp, qtd_pessoas, aniversario, mesas_alocadas, reserva_id))
    
    cursor.execute("SELECT show_id FROM reservas WHERE id = ?", (reserva_id,))
    show_id = cursor.fetchone()["show_id"]
    
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/admin?show_id={show_id}", status_code=status.HTTP_303_SEE_OTHER)

# Excluir Reserva
@app.post("/admin/reservas/excluir/{reserva_id}")
def excluir_reserva(reserva_id: int, auth: bool = Depends(verificar_autenticacao)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT show_id FROM reservas WHERE id = ?", (reserva_id,))
    reserva = cursor.fetchone()
    show_id = reserva["show_id"] if reserva else None
    
    cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/admin?show_id={show_id}", status_code=status.HTTP_303_SEE_OTHER)

# Gestão de Shows
@app.post("/admin/shows/novo")
def criar_show(data_show: str = Form(...), banda: str = Form(...), limite_capacidade: int = Form(150), auth: bool = Depends(verificar_autenticacao)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO shows (data_show, banda, limite_capacidade, visivel) VALUES (?, ?, ?, 1)", (data_show, banda, limite_capacidade))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/shows/excluir/{show_id}")
def excluir_show(show_id: int, auth: bool = Depends(verificar_autenticacao)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE show_id = ?", (show_id,))
    cursor.execute("DELETE FROM shows WHERE id = ?", (show_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

# Impressão na Bobina de 80mm
@app.get("/admin/imprimir/{show_id}", response_class=HTMLResponse)
def imprimir_lista_80mm(request: Request, show_id: int, auth: bool = Depends(verificar_autenticacao)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shows WHERE id = ?", (show_id,))
    show = cursor.fetchone()
    cursor.execute("SELECT * FROM reservas WHERE show_id = ? ORDER BY nome_cliente ASC", (show_id,))
    reservas = cursor.fetchall()
    cursor.execute("SELECT COALESCE(SUM(qtd_pessoas), 0) FROM reservas WHERE show_id = ?", (show_id,))
    total_pessoas = cursor.fetchone()[0]
    conn.close()
    return templates.TemplateResponse(request=request, name="imprimir_80mm.html", context={"show": show, "reservas": reservas, "total_pessoas": total_pessoas})