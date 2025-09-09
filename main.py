import smtplib
import ssl
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar credenciales seguras desde .env
load_dotenv()
SMTP_USER = os.getenv("SMTP_USER")  # tu correo
SMTP_PASS = os.getenv("SMTP_PASS")  # tu contraseña

# Configuración SMTP PrivateEmail
SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 465  # SSL

# Archivos
JSON_FILE = "empresas.json"
HTML_FILE = "mensaje.html"

def cargar_empresas(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()

def enviar_correo(empresa, destinatario, mensaje_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = f"Propuesta para {empresa}"

    # Personalizar el mensaje
    html_personalizado = mensaje_html.replace("[]", empresa)

    parte_html = MIMEText(html_personalizado, "html")
    msg.attach(parte_html)

    # Enviar por SMTP
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        print(f"✅ Correo enviado a {empresa} ({destinatario})")

def main():
    empresas = cargar_empresas(JSON_FILE)
    mensaje_html = cargar_html(HTML_FILE)

    for item in empresas:
        empresa = item.get("empresa")
        email = item.get("email")
        if empresa and email:
            enviar_correo(empresa, email, mensaje_html)

if __name__ == "__main__":
    main()
