from playwright.sync_api import sync_playwright

URL = "https://mangaplus.shueisha.co.jp/titles/200116"

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    print("Abriendo MANGA Plus...")

    page.goto(
        URL,
        wait_until="networkidle",
        timeout=60000
    )

    print("Título de la página:")
    print(page.title())

    print("\nURL final:")
    print(page.url)

    print("\nTexto obtenido:")
    print(page.locator("body").inner_text()[:15000])

    browser.close()
