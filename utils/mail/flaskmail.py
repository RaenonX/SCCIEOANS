from flask_mail import Mail, Message

class flaskmail:
    def __init__(self, mail_instance):
        self._mail_instance = mail_instance

    def send_email(self, title, content, recipients):
        if not isinstance(recipients, list):
            recipients = [recipients]

        m = Message(title, recipients=recipients)
        m.body = content;

        self._mail_instance.send(m)