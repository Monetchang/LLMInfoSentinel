import smtplib
from email.mime.text import MIMEText

class Notifier:
    def __init__(self, notification_settings):
        self.notification_settings = notification_settings

    def send_email(self, subject, body):
        sender_email = "your-email@example.com"
        receiver_email = self.notification_settings["email"]
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        with smtplib.SMTP('smtp.example.com') as server:
            server.login(sender_email, "password")
            server.sendmail(sender_email, receiver_email, msg.as_string())

    def send_notification(self, subject, body):
        if self.notification_settings["method"] == "email":
            self.send_email(subject, body)
        elif self.notification_settings["method"] == "slack":
            # Slack通知实现
            pass
