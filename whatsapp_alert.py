import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()


class WhatsAppAlert:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.to_whatsapp = os.getenv("MY_WHATSAPP_NUMBER")

        self.client = Client(self.account_sid, self.auth_token)

    def send_alert(self, text):
        self.client.messages.create(
            body=text,
            from_=self.from_whatsapp,
            to=self.to_whatsapp
        )