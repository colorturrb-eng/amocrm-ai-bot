from fastapi import FastAPI, Request
import requests
import time
import os

app = FastAPI()

AMO_TOKEN = os.getenv("AMO_TOKEN")
AMO_DOMAIN = os.getenv("AMO_DOMAIN")
AI_TOKEN = os.getenv("AI_TOKEN")

def ask_ai(text):
    prompt = f"""
Ты менеджер по продаже туров.
Отвечай вежливо, кратко и по делу.
Можно называть цены и записывать клиента.
Если клиент готов — предложи оформить заявку.

Сообщение клиента: {text}
"""

    r = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {AI_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
    )

    return r.json()["choices"][0]["message"]["content"]

def send_to_amocrm(chat_id, text):
    time.sleep(5)  # антибан — задержка
    requests.post(
        f"https://{AMO_DOMAIN}.amocrm.ru/api/v4/chats/{chat_id}/messages",
        headers={
            "Authorization": f"Bearer {AMO_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "message": {
                "type": "text",
                "text": text
            }
        }
    )

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    try:
        text = data["message"]["text"]
        chat_id = data["message"]["chat_id"]

        answer = ask_ai(text)
        send_to_amocrm(chat_id, answer)

    except:
        pass

    return {"status": "ok"}
