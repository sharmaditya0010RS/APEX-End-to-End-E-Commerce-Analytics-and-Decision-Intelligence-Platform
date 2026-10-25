from playwright.sync_api import sync_playwright

pages = {
    "Executive": "/",
    "Customers": "/customers",
    "Operations": "/operations",
    "Predictive": "/predictive",
    "Decisions": "/decisions"
}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    for name, route in pages.items():
        page.goto(
            "http://127.0.0.1:8050" + route,
            wait_until="domcontentloaded",
            timeout=120000
        )

        page.wait_for_function(
            """() => {
                const plots = [...document.querySelectorAll(
                    '.dash-graph .js-plotly-plot'
                )];

                return plots.length === 10 && plots.every(
                    plot => plot._fullLayout && plot.data?.length > 0
                );
            }""",
            timeout=120000
        )

        result = page.evaluate(
            """() => [...document.querySelectorAll(
                '.dash-graph .js-plotly-plot'
            )].map(plot => ({
                paper: plot._fullLayout.paper_bgcolor,
                canvas: plot._fullLayout.plot_bgcolor,
                text: plot._fullLayout.font.color
            }))"""
        )

        def white(color):
            return str(color).lower().replace(" ", "") in {
                "#fff",
                "#ffffff",
                "white",
                "rgb(255,255,255)"
            }

        assert len(result) == 10, (name, result)

        for index, chart in enumerate(result, 1):
            assert white(chart["paper"]), (
                name, index, "paper", chart
            )
            assert chart["canvas"] is None or white(chart["canvas"]), (
                name, index, "canvas", chart
            )

        print(
            f"{name}: 10/10 ACTUAL WHITE PLOTLY FIGURES — PASS",
            flush=True
        )

    browser.close()

print("ALL 50 PLOTLY CHART BACKGROUNDS: WHITE")
