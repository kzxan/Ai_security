from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gpt_helper import ask_gpt

from state import (
    get_status_text,
    get_system_uptime_text,
    get_summary_text,
    get_last_image_path
)

app = Flask(__name__)


def smart_reply(user_text: str) -> str:
    text = user_text.lower().strip()

    # 🔒 қауіп командасы бірінші
    if "қауіп бар ма" in text:
        return get_status_text()

    if "status" == text:
        return get_system_uptime_text()

    if "summary" in text:
        return get_summary_text()

    if "соңғы сурет" in text:
        image_path = get_last_image_path()
        if image_path:
            return f"🖼 Соңғы сурет:\n{image_path}"
        return "Сурет жоқ"

    if text == "help":
        return "Командалар:\nstatus\nқауіп бар ма\nsummary\nсоңғы сурет"

    # 🤖 ҚАЛҒАН БӘРІ → GPT
    return ask_gpt(user_text)

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