from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from state import (
    get_status_text,
    get_system_uptime_text,
    get_summary_text,
    get_last_image_path
)

app = Flask(__name__)


def smart_reply(user_text: str) -> str:
    text = user_text.lower().strip()

    if text in ["сәлем", "салем", "hello", "hi"]:
        return (
            "Сәлем 👋\n"
            "Мен AI қауіпсіздік ботымын.\n"
            "Командалар:\n"
            "• қауіп бар ма\n"
            "• status\n"
            "• summary\n"
            "• соңғы сурет\n"
            "• help"
        )

    if "қауіп бар ма" in text or text == "status danger":
        return get_status_text()

    if text == "status":
        return get_system_uptime_text()

    if "summary" in text or "қорытынды" in text:
        return get_summary_text()

    if "соңғы сурет" in text or "last image" in text:
        image_path = get_last_image_path()
        if image_path:
            return f"🖼 Соңғы сақталған сурет бар:\n{image_path}\n\nҚазір файл локалда сақталған."
        return "🖼 Соңғы сурет әлі жоқ."

    if text == "help" or text == "көмек":
        return (
            " Қол жетімді командалар:\n"
            "• қауіп бар ма\n"
            "• status\n"
            "• summary\n"
            "• соңғы сурет\n"
            "• help"
        )

    return (
        "🤖 Сұрағыңды түсіндім, бірақ қазір менің негізгі функциям — қауіпсіздік мониторингі.\n\n"
        "Мыналарды жаза аласың:\n"
        "• қауіп бар ма\n"
        "• status\n"
        "• summary\n"
        "• соңғы сурет\n"
        "• help"
    )


@app.route("/")
def home():
    return "AI Security WhatsApp Bot is running."


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "")
    reply_text = smart_reply(incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply_text)

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)