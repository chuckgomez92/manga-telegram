import os
import requests
import re

MANGA_ID = "200116"
MANGA_URL = "https://mangaplus.shueisha.co.jp/titles/200116"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

STATE_FILE = "last_chapter.txt"


def get_latest_chapter():
    url = "https://jumpg-webapi.tokyo-cdn.com/api/title_detail"

    response = requests.get(
        url,
        params={"title_id": MANGA_ID},
        headers={
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://mangaplus.shueisha.co.jp",
            "Referer": "https://mangaplus.shueisha.co.jp/",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    title_detail = data["success"]["titleDetailView"]

    chapters = title_detail.get("chapters", [])

    if not chapters:
        raise RuntimeError("No se encontraron capítulos.")

    latest = chapters[0]

    name = latest.get("name", "")

    match = re.search(r"(\d+(?:\.\d+)?)", name)

    if not match:
        raise RuntimeError(f"No pude identificar el número del capítulo: {name}")

    chapter_number = match.group(1)

    return chapter_number


def send_telegram(chapter):
    message = (
        "📖 *BORUTO: TWO BLUE VORTEX*\n\n"
        f"🔥 Nuevo capítulo: *{chapter}*\n\n"
        "👉 [Leer oficialmente en MANGA Plus]"
        f"({MANGA_URL})"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    response.raise_for_status()


def main():
    current_chapter = get_latest_chapter()

    print(f"Capítulo encontrado: {current_chapter}")

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            previous_chapter = file.read().strip()
    else:
        previous_chapter = ""

    print(f"Capítulo guardado: {previous_chapter}")

    # Primera ejecución:
    # guarda el capítulo actual pero NO manda mensaje.
    if not previous_chapter:
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            file.write(current_chapter)

        print("Primera ejecución. Capítulo guardado sin enviar.")

        return

    # Si hay capítulo nuevo:
    if current_chapter != previous_chapter:

        send_telegram(current_chapter)

        with open(STATE_FILE, "w", encoding="utf-8") as file:
            file.write(current_chapter)

        print(f"Nuevo capítulo {current_chapter} enviado a Telegram.")

    else:
        print("No hay capítulo nuevo.")


if __name__ == "__main__":
    main()
