import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-5.3",  # немесе gpt-4o-mini (арзан)
            messages=[
                {"role": "system", "content": "Сен қауіпсіздік AI чат-ботсың. Қысқа әрі нақты жауап бер."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=200
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ GPT қате: {e}"