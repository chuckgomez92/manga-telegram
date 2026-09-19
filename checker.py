import os
import re
from playwright.sync_api import sync_playwright

MANGA_URL = "https://mangaplus.shueisha.co.jp/titles/200116"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

STATE_FILE = "last_chapter.txt"


def get_latest_chapter():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Abriendo MANGA Plus...")

        page.goto(
            MANGA_URL,
            wait_until="networkidle",
            timeout=60000
        )

        text = page.locator("body").inner_text()

        browser.close()

    # Buscar capítulos con formato:
    # #037
    # ...
    # Capítulo 37: Confía en él

    pattern = r"#(\d+).*?Capítulo\s+(\d+)(?::\s*(.*?))?(?=\n|$)"

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not matches:
        raise RuntimeError(
            "No se encontraron capítulos en MANGA Plus."
        )

    # El último capítulo de la página es el más reciente
    chapter_id, chapter_number, chapter_title = matches[-1]

    chapter_number = int(chapter_number)

    if chapter_title:
        chapter_title = chapter_title.strip()
    else:
        chapter_title = ""

    print("Capítulo encontrado:", chapter_number)
    print("Título:", chapter_title)

    return str(chapter_number), chapter_title


def send_telegram(chapter_number, chapter_title):

    if chapter_title:

        message = (
            "📖 *BORUTO - TWO BLUE VORTEX*\n\n"
            "🔥 *Nuevo capítulo disponible*\n\n"
            f"🔖 Capítulo *{chapter_number}*\n"
            f"📚 {chapter_title}\n\n"
            "👉 [Leer oficialmente en MANGA Plus]"
            f"({MANGA_URL})"
        )

    else:

        message = (
            "📖 *BORUTO - TWO BLUE VORTEX*\n\n"
            "🔥 *Nuevo capítulo disponible*\n\n"
            f"🔖 Capítulo *{chapter_number}*\n\n"
            "👉 [Leer oficialmente en MANGA Plus]"
            f"({MANGA_URL})"
        )

    import requests

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

    print("Telegram status:", response.status_code)

    response.raise_for_status()


def main():

    current_chapter, chapter_title = get_latest_chapter()

    print("Capítulo actual:", current_chapter)

    if os.path.exists(STATE_FILE):

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            previous_chapter = file.read().strip()

    else:

        previous_chapter = ""

    print("Capítulo guardado:", previous_chapter)

    # Primera ejecución
   if not previous_chapter:

    print("Primera ejecución.")

    send_telegram(
        current_chapter,
        chapter_title
    )

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(current_chapter)

    print("Capítulo inicial enviado a Telegram.")

    return

    # Capítulo nuevo
    if current_chapter != previous_chapter:

        print("🎉 ¡CAPÍTULO NUEVO!")

        send_telegram(
            current_chapter,
            chapter_title
        )

        with open(
            STATE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(current_chapter)

        print("Mensaje enviado a Telegram.")

    else:

        print("No hay capítulo nuevo.")


if __name__ == "__main__":
    main()
