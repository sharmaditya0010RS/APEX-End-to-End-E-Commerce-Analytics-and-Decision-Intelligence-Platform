from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8050/decisions"

def choose(page, control_id, label):
    trigger = page.locator(f"button#{control_id}")
    trigger.click()
    page.get_by_role("option", name=label, exact=True).click()

def verify(page, expected_text, expected_number):
    page.wait_for_function(
        """([text, number]) => {
            const kpi = document.querySelector('#decision-selected-net');
            const plot = document.querySelector(
                '#decision-visual-42 .js-plotly-plot'
            );

            return (
                kpi?.textContent?.trim() === text &&
                plot?.data?.length > 0 &&
                Math.abs(Number(plot.data[0].y[2]) - number) < 0.001
            );
        }""",
        arg=[expected_text, expected_number],
        timeout=30000
    )

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 1440, "height": 900}
    )

    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    response = page.goto(
        BASE,
        wait_until="domcontentloaded",
        timeout=120000
    )

    assert response is not None
    assert response.status == 200

    verify(page, "R$-2,217.50", -2217.5)
    print("REFERENCE DEFAULT SCENARIO: PASS", flush=True)

    choose(page, "decision-capacity", "Top 1% of test orders")
    choose(page, "decision-effectiveness", "10% prevented")
    choose(page, "decision-cost", "R$2 per reviewed order")
    choose(page, "decision-value", "R$100 per prevented late")

    verify(page, "R$+28.00", 28.0)
    print("OPTIMISTIC HYPOTHETICAL SCENARIO: PASS", flush=True)

    choose(page, "decision-capacity", "Top 5% of test orders")
    choose(page, "decision-effectiveness", "25% prevented")
    choose(page, "decision-cost", "R$5 per reviewed order")
    choose(page, "decision-value", "R$50 per prevented late")

    verify(page, "R$-2,217.50", -2217.5)
    print("FILTER RESET AND CHART RECOMPUTATION: PASS", flush=True)

    assert not errors, errors

    plots = page.locator(".dash-graph .js-plotly-plot")
    assert plots.count() == 10

    print("TEN DECISION CHARTS REMAIN RENDERED: PASS", flush=True)
    print("BROWSER JAVASCRIPT ERRORS: NONE", flush=True)
    print("PHASE 8 REAL FILTER INTERACTION: PASS", flush=True)

    browser.close()
