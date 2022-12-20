from flask_mail import Message
from flask import current_app, render_template
from threading import Thread

from app import mail, app

def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)

def send_reset_email(token, user):
    msg = Message("[Invoice Recognition] Reset Password",
                  sender=current_app.config["MAIL_USERNAME"],
                  recipients=[user.email],
                  html=render_template('reset_email_page.html', token=token, user=user)
                  )
    Thread(target=send_email_async, args=(app, msg)).start()