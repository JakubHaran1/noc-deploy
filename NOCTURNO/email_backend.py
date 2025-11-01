from django.core.mail.backends.base import BaseEmailBackend
import resend
import os


class NocturnoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for mail in email_messages:
            params = {
                "from": mail.from_email,
                "to": mail.to,
                "subject": mail.subject,
                "html": mail.body
            }

            try:
                resend.api_key = os.environ["RESEND_API_KEY"]
                resend.Emails.send(params)
                print("✅ Email wysłany przez Resend")

            except Exception as e:
                print("❌ Błąd wysyłki przez Resend:", e)

        return super().send_messages(email_messages)
