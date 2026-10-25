from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8050/decisions"

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 1440, "height": 900}
    )

    page.goto(
        BASE,
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.locator("#decision-selected-net").get_by_text(
        "R$-2,217.50",
        exact=True
    ).wait_for(timeout=120000)

    for control_id in [
        "decision-capacity",
        "decision-effectiveness",
        "decision-cost",
        "decision-value"
    ]:
        print(f"\n=== {control_id} ===", flush=True)

        locator = page.locator(f"#{control_id}")
        print("MATCH COUNT:", locator.count(), flush=True)

        if locator.count() == 1:
            print(
                "OUTER HTML:",
                locator.evaluate(
                    "(element) => element.outerHTML.slice(0, 1800)"
                ),
                flush=True
            )

            print(
                "BUTTONS:",
                locator.locator("button").count(),
                flush=True
            )

            print(
                "ROLE COMBOBOX:",
                locator.get_by_role("combobox").count(),
                flush=True
            )

            print(
                "ROLE LISTBOX:",
                locator.get_by_role("listbox").count(),
                flush=True
            )

    browser.close()
