from flask_mail import current_app, Message


class FlaskMail:
    @staticmethod
    def send_html_mail(title, html_content, recipients):
        if not isinstance(recipients, list):
            recipients = [recipients]

        m = Message(title, recipients=recipients)
        m.html = html_content

        current_app.config["MAIL_INSTANCE"].send(m)
