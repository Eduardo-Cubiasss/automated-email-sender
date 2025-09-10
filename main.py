import smtplib
import ssl
import json
import os
import time
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar credenciales seguras desde .env
load_dotenv()
SMTP_USER = os.getenv("SMTP_USER")
SMTP_USER2 = os.getenv("SMTP_USER2")
SMTP_USER3 = os.getenv("SMTP_USER3")
SMTP_PASS = os.getenv("SMTP_PASS")

# Configuración SMTP PrivateEmail
SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 465  # SSL

# Archivos
JSON_FILE = "datos/pruebas.json"
HTML_DIR = "mensajes/html"
TEXT_DIR = "mensajes/text"

# Tamaño del lote diario
LOTE_DIARIO = 6

def cargar_empresas(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_plantillas():
    """Devuelve lista de tuplas (html, txt) con las plantillas disponibles"""
    plantillas = []
    for i in range(1, 5):
        with open(os.path.join(HTML_DIR, f"mensaje{i}.html"), "r", encoding="utf-8") as f_html, \
             open(os.path.join(TEXT_DIR, f"mensaje{i}.txt"), "r", encoding="utf-8") as f_txt:
            plantillas.append((f_html.read(), f_txt.read()))
    return plantillas

def enviar_correo(empresa, destinatario, gancho, plantillas):
    # Escoger remitente aleatoriamente
    remitente = random.choice([SMTP_USER, SMTP_USER2, SMTP_USER3])

    # Escoger plantilla aleatoriamente
    html_base, txt_base = random.choice(plantillas)

    # Personalizar contenido
    html_personalizado = html_base.replace("[]", empresa)
    txt_personalizado = txt_base.replace("[]", empresa)

    # Armar mensaje con ambas versiones
    msg = MIMEMultipart("alternative")
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = f"{empresa}, {gancho}"

    parte_txt = MIMEText(txt_personalizado, "plain")
    parte_html = MIMEText(html_personalizado, "html")

    msg.attach(parte_txt)
    msg.attach(parte_html)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(remitente, SMTP_PASS)
        server.sendmail(remitente, destinatario, msg.as_string())

    return remitente  # devuelvo cuál remitente se usó

def main():
    empresas = cargar_empresas(JSON_FILE)
    plantillas = cargar_plantillas()

    hoy = datetime.today().date()
    fecha_base = datetime(2025, 9, 10).date()
    dias_transcurridos = (hoy - fecha_base).days

    inicio = dias_transcurridos * LOTE_DIARIO
    fin = inicio + LOTE_DIARIO
    lote_hoy = empresas[inicio:fin]

    print(f"📅 Fecha de hoy: {hoy}")
    print(f"✉️ Enviando correos del {inicio+1} al {min(fin, len(empresas))} de {len(empresas)}")

    fallidos = []  # lista para guardar errores

    for i, item in enumerate(lote_hoy, start=1):
        empresa_raw = item.get("empresa")
        email = item.get("email")
        gancho = item.get("gancho")

        if empresa_raw and email and gancho:
            empresa = empresa_raw.title()

            try:
                remitente_usado = enviar_correo(empresa, email, gancho, plantillas)
                print(f"✅ Correo enviado a {empresa} ({email}) con asunto: {gancho} desde {remitente_usado}")
            except Exception as e:
                print(f"❌ Error al enviar a {empresa} ({email}): {e}")
                fallidos.append({
                    "empresa": empresa,
                    "email": email,
                    "gancho": gancho,
                    "error": str(e)
                })

            if i < len(lote_hoy):
                delay = random.uniform(10, 40)
                print(f"👉 Vamos por el destinatario {empresa} número: {inicio+i}/{len(empresas)}")
                print(f"⏳ Esperando {delay:.1f} segundos antes del siguiente correo...")
                time.sleep(delay)

    # Mostrar resumen de errores en JSON
    if fallidos:
        print("\n📌 Resumen de correos fallidos:")
        print(json.dumps(fallidos, indent=2, ensure_ascii=False))
    else:
        print("\n✅ Todos los correos del lote se enviaron correctamente.")

if __name__ == "__main__":
    main()
