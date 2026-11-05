# main.py
from fastapi import FastAPI, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
import database

app = FastAPI(title="PlanchaQR Clon Profesional - Postgres")
PASSWORD_MAESTRA = "Olavarria2026"

# Asegurar que las tablas existan en Postgres al arrancar
database.inicializar_base_de_datos()

# 1. El Link Puente (://tudominio.com)
@app.get("/r/{id_cartel}")
def procesar_redireccion(id_cartel: str, db: Session = Depends(database.get_db)):
    resultado = db.query(database.CartelLink).filter(database.CartelLink.id_cartel == id_cartel).first()
    
    if resultado:
        # Si ya esta asignado, desvia de inmediato a Postgres
        return RedirectResponse(url=resultado.url_destino, status_code=302)
    else:
        # Si esta vacio, abre el formulario de activacion en caliente
        html_setup = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Configurar Cartel #{id_cartel}</title>
            <style>
                body {{ font-family: -apple-system, sans-serif; background: #f4f4f9; text-align: center; padding: 40px 20px; }}
                .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }}
                input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }}
                button {{ width: 100%; padding: 12px; background: #e4405f; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class='card'>
                <h2>🚀 Activar Cartel Inteligente #{id_cartel}</h2>
                <form action='/asignar' method='post'>
                    <input type='hidden' name='id_cartel' value='{id_cartel}'>
                    <input type='text' name='url_destino' placeholder='Pegá el link de Google o Instagram' required>
                    <input type='password' name='password' placeholder='Contraseña Maestra' required>
                    <button type='submit'>Vincular y Guardar en Postgres</button>
                </form>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_setup, status_code=200)

# 2. El endpoint que procesa la grabacion del link en caliente
@app.post("/asignar")
def asignar_link(
    id_cartel: str = Form(...), 
    url_destino: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    if password != PASSWORD_MAESTRA:
        return HTMLResponse(content="<h3>❌ Contraseña maestra incorrecta</h3>", status_code=403)
    
    if not url_destino.startswith("http://") and not url_destino.startswith("https://"):
        url_destino = "https://" + url_destino

    # Buscamos si ya existe para actualizarlo o creamos uno nuevo
    db_link = db.query(database.CartelLink).filter(database.CartelLink.id_cartel == id_cartel).first()
    if db_link:
        db_link.url_destino = url_destino
    else:
        nuevo_link = database.CartelLink(id_cartel=id_cartel, url_destino=url_destino)
        db.add(nuevo_link)
        
    db.commit()
    
    return HTMLResponse(content=f"""
        <body style='font-family:sans-serif; text-align:center; padding:50px;'>
            <h2>✅ ¡Cartel #{id_cartel} Vinculado con éxito!</h2>
            <p>Destino actual guardado en Postgres: <b>{url_destino}</b></p>
            <p style='color:green;'>Ya podés escanearlo de nuevo para verificar el desvío directo.</p>
        </body>
    """)
# Requerimiento obligatorio para que Vercel Serverless mapee correctamente la app
app = app