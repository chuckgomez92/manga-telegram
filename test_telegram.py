import os
import requests

token = os.environ["TELEGRAM_BOT_TOKEN"]
channel = os.environ["TELEGRAM_CHANNEL"]

url = f"https://api.telegram.org/bot{token}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": channel,
        "text": "🤖 Prueba automática: el bot de MANGA Plus está conectado correctamente.",
    },
    timeout=30,
)

print(response.status_code)
print(response.text)

response.raise_for_status()
