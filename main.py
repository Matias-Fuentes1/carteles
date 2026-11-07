
import os
import secrets

from html import escape
from urllib.parse import urlsplit

from fastapi import FastAPI, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

import database


app = FastAPI(title="PlanchaQR - Carteles Inteligentes")


# Inicializar la base de datos al arrancar
@app.on_event("startup")
def startup_event():
    # Render funciona únicamente como puente hacia Vercel
    if not os.getenv("QR_REDIRECT_BASE"):
        database.inicializar_base_de_datos()


# 1. Redireccionar o mostrar formulario de configuración
@app.get("/r/{id_cartel}")
def procesar_redireccion(
    id_cartel: str,
    configurar: int = 0,
    db: Session = Depends(database.get_db)
):

    # Si estamos en Render, enviar el QR antiguo a Vercel
    destino_vercel = os.getenv("QR_REDIRECT_BASE")

    if destino_vercel:
        url = f"{destino_vercel.rstrip('/')}/r/{id_cartel}"

        if configurar == 1:
            url += "?configurar=1"

        return RedirectResponse(url=url, status_code=302)

    # Funcionamiento normal en Vercel
    resultado = (
        db.query(database.CartelLink)
        .filter(database.CartelLink.id_cartel == id_cartel)
        .first()
    )

    # Redirigir al destino guardado solamente si no se pidió configurar
    if resultado and configurar != 1:
        return RedirectResponse(
            url=resultado.url_destino,
            status_code=302
        )

    cartel_html = escape(id_cartel)

    html_setup = f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configurar Cartel #{cartel_html}</title>

        <style>
            body {{
                font-family: -apple-system, sans-serif;
                background: #f4f4f9;
                text-align: center;
                padding: 40px 20px;
            }}

            .card {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                max-width: 400px;
                margin: auto;
            }}

            input {{
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 6px;
                box-sizing: border-box;
                font-size: 16px;
            }}

            button {{
                width: 100%;
                padding: 12px;
                background: #e4405f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>
        <div class="card">

            <h2>🚀 Configurar Cartel #{cartel_html}</h2>

            <form action="/asignar" method="post">

                <input
                    type="hidden"
                    name="id_cartel"
                    value="{cartel_html}"
                >

                <input
                    type="text"
                    name="url_destino"
                    placeholder="Pegá el link de Google o Instagram"
                    required
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Contraseña Maestra"
                    required
                >

                <button type="submit">
                    Vincular y guardar
                </button>

            </form>

        </div>
    </body>

    </html>
    """

    return HTMLResponse(content=html_setup)


# 2. Procesar la asignación o actualización del enlace
@app.post("/asignar")
def asignar_link(
    id_cartel: str = Form(...),
    url_destino: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):

    password_maestra = os.getenv("PASSWORD_MAESTRA")

    if not password_maestra:
        return HTMLResponse(
            content="El sistema no está configurado.",
            status_code=503
        )

    if not secrets.compare_digest(
        password.encode("utf-8"),
        password_maestra.encode("utf-8")
    ):
        return HTMLResponse(
            content="<h3>❌ Contraseña maestra incorrecta</h3>",
            status_code=403
        )

    # Normalizar y validar URL
    url_destino = url_destino.strip()

    if not url_destino.startswith(("http://", "https://")):
        url_destino = "https://" + url_destino

    parsed_url = urlsplit(url_destino)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        return HTMLResponse(
            content="El enlace ingresado no es válido.",
            status_code=400
        )

    # Buscar si el cartel ya existe
    db_link = (
        db.query(database.CartelLink)
        .filter(database.CartelLink.id_cartel == id_cartel)
        .first()
    )

    if db_link:
        db_link.url_destino = url_destino
    else:
        nuevo_link = database.CartelLink(
            id_cartel=id_cartel,
            url_destino=url_destino
        )
        db.add(nuevo_link)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    cartel_html = escape(id_cartel)
    destino_html = escape(url_destino)

    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cartel vinculado</title>
        </head>

        <body style="font-family:sans-serif; text-align:center; padding:50px;">

            <h2>✅ ¡Cartel #{cartel_html} vinculado con éxito!</h2>

            <p>
                Destino guardado:
                <b>{destino_html}</b>
            </p>

            <p style="color:green;">
                Ya podés escanearlo nuevamente para verificar la redirección.
            </p>

        </body>
        </html>
    """)


