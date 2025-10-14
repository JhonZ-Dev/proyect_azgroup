# app/utils/email_utils.py
from typing import List
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader, select_autoescape

def enviar_email(subject: str, body: str, to_emails: List[str]):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "jhonmacias1999@gmail.com"
    msg['To'] = ', '.join(to_emails)
    msg.set_content(body, subtype='html')  # Para HTML
    print("DEBUG: Mensaje construido")

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        print("DEBUG: Conectando SMTP...")
        server.starttls()
        server.login("zambranomaciasjhon@gmail.com", "jfvc ubbf wkxa sguz")
        print("DEBUG: Login SMTP exitoso")
        server.send_message(msg)
        print("DEBUG: Email enviado correctamente")
def render_template(template_name: str, context: dict):
    env = Environment(
        loader=FileSystemLoader('app/templates/emails'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    return template.render(context)