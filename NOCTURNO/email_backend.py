from django.core.mail.backends.base import BaseEmailBackend
import resend
import os


class NocturnoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for mail in email_messages:
            for el in mail.alternatives:
                if el[0][1] == "text/html":
                    html = el[0][0]
                else:
                    html = mail.body
            params = {
                "from": mail.from_email,
                "to": mail.to,
                "subject": mail.subject,
                "html": html
            }

            try:
                resend.api_key = os.environ["RESEND_API_KEY"]
                resend.Emails.send(params)
                print("✅ Email wysłany przez Resend")

            except Exception as e:
                print("❌ Błąd wysyłki przez Resend:", e)

        return len(email_messages)
