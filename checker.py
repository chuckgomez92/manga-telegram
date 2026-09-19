import os
import requests

MANGA_ID = "200116"
MANGA_URL = "https://mangaplus.shueisha.co.jp/titles/200116"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

STATE_FILE = "last_chapter.txt"


def get_latest_chapter():
    url = "https://jumpg-webapi.tokyo-cdn.com/api/title_detailV3"

    response = requests.get(
        url,
        params={
            "title_id": MANGA_ID,
            "format": "json",
        },
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Origin": "https://mangaplus.shueisha.co.jp",
            "Referer": "https://mangaplus.shueisha.co.jp/",
        },
        timeout=30,
    )

    print("API status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    title_detail = data["success"]["titleDetailView"]

    print("Título:", title_detail["title"]["name"])

    chapters = title_detail.get("chapters", [])

    if not chapters:
        raise RuntimeError("La API no devolvió capítulos.")

    # Mostrar información para comprobar qué está devolviendo MANGA Plus
    for chapter in chapters[:5]:
        print(
            "Capítulo:",
            chapter.get("name"),
            "| ID:",
            chapter.get("chapterId")
        )

    latest = chapters[0]

    chapter_name = latest.get("name", "")
    chapter_id = latest.get("chapterId")

    return chapter_name, chapter_id


def send_telegram(chapter_name):
    message = (
        "📖 *BORUTO: TWO BLUE VORTEX*\n\n"
        f"🔥 *Nuevo capítulo disponible*\n"
        f"🔖 {chapter_name}\n\n"
        f"👉 [Leer en MANGA Plus]({MANGA_URL})"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown",
        },
        timeout=30,
    )

    print("Telegram status:", response.status_code)

    response.raise_for_status()


def main():
    chapter_name, chapter_id = get_latest_chapter()

    current_id = str(chapter_id)

    print("Capítulo actual:", chapter_name)
    print("ID actual:", current_id)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            previous_id = file.read().strip()
    else:
        previous_id = ""

    print("ID guardado:", previous_id)

    # Primera ejecución: guardar el capítulo sin enviar Telegram
    if not previous_id:
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            file.write(current_id)

        print("Primera ejecución. Capítulo guardado.")
        return

    # Capítulo nuevo
    if current_id != previous_id:
        send_telegram(chapter_name)

        with open(STATE_FILE, "w", encoding="utf-8") as file:
            file.write(current_id)

        print("Nuevo capítulo enviado a Telegram.")

    else:
        print("No hay capítulo nuevo.")


if __name__ == "__main__":
    main()
