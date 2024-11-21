import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Datenbank_Struktur import *
import re

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/fitnessappv33")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

html_body= """
<html>
  <head>
    <style>
      body {
        font-family: Arial, sans-serif;
        color: #333;
        background-color: #f4f4f9;
      }
      h1 {
        color: #4CAF50;
      }
      p {
        font-size: 14px;
      }
      .highlight {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
      }
      .footer {
        font-size: 12px;
        color: #777;
        margin-top: 20px;
      }
    </style>
  </head>
  <body>
    <h1>Willkommen bei MoveMate!</h1>
    <p>Hallo,</p>
    <p>Willkommen bei <span class="highlight">MoveMate</span>, viel Spaß beim Verwenden der App!</p>
    <p>Falls du Fragen hast, kannst du dich gerne bei uns melden!</p>

    <p>Mit freundlichen Grüßen,</p>
    <p><strong>Das MoveMate Team</strong></p>

    <div class="footer">
        <p>Diese Nachricht wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
    </div>
  </body>
</html>
"""

def send_email(to_email: str, user: str):
    """Funktion, um eine einzelne E-Mail zu senden."""
    subject = f"Willkommen bei MoveMate {user}!"
    from_email = "movemate.fitness@gmail.com"
    from_password = "tipb opxf osju ujes"
    
    try:

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=60)
        server.starttls()  
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"E-Mail erfolgreich an {to_email} gesendet!")

    except smtplib.SMTPServerDisconnected as srv_dcn_err:
        print(f"Verbindung wurde unerwartet getrennt: {srv_dcn_err}")
    except smtplib.SMTPException as smtp_err:
        print(f"SMTP-Fehler beim Senden der E-Mail an {to_email}: {smtp_err}")
    except Exception as e:
        print(f"Allgemeiner Fehler beim Senden der E-Mail an {to_email}: {e}")

def send_email_to_all_users(from_email, from_password, subject, body):
    """Sendet eine E-Mail an alle Benutzer in der AllUser-Datenbank"""
    try:
        with SessionLocal() as session:
            users = session.query(AllUser).all()
            
            to_emails = [user.email for user in users if user.email]
            
            for email in to_emails:
                send_email(subject, body, email, from_email, from_password)

    except Exception as e:
        print(f"Fehler beim Abrufen der Benutzerdaten: {e}")
        