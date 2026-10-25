from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports" / "dashboard" / "browser_qa"
OUTPUT.mkdir(parents=True, exist_ok=True)

BASE = "http://127.0.0.1:8050"

PAGES = {
    "executive": "/",
    "customers": "/customers",
    "operations": "/operations",
    "predictive": "/predictive",
    "decisions": "/decisions",
}

VIEWPORTS = {
    "desktop": (1440, 900),
    "tablet": (820, 1100),
    "mobile": (390, 844),
}

CHECK_SCRIPT = """
() => {
    const graphs = [...document.querySelectorAll('.dash-graph')]
        .filter(el => el.id);

    const issues = [];
    const details = [];

    for (const graph of graphs) {
        const plot = graph.querySelector('.js-plotly-plot');
        const rect = graph.getBoundingClientRect();
        const figure = plot?._fullLayout;
        const traces = plot?.data || [];

        const card = graph.closest('.apex-graph-card');
        const header = card?.querySelector('.chart-card-header');
        const headerRect = header?.getBoundingClientRect();
        const plotRect = plot?.getBoundingClientRect();

        const gap = headerRect && plotRect
            ? Math.round(plotRect.top - headerRect.bottom)
            : null;

        const bg = figure?.paper_bgcolor || null;

        const record = {
            id: graph.id,
            traces: traces.length,
            height: Math.round(rect.height),
            width: Math.round(rect.width),
            headerGap: gap,
            paperBackground: bg
        };

        details.push(record);

        if (!plot || traces.length === 0) {
            issues.push(`${graph.id}: missing rendered Plotly traces`);
        }

        if (rect.height < 200 || rect.width < 150) {
            issues.push(`${graph.id}: invalid dimensions`);
        }

        if (gap !== null && (gap > 110 || gap < -12)) {
            issues.push(`${graph.id}: header-to-chart gap ${gap}px`);
        }

        const isWhite = bg && [
            '#fff',
            '#ffffff',
            'white',
            'rgb(255,255,255)'
        ].includes(bg.toLowerCase().replace(/\\s/g, ''));

        if (!isWhite) {
            issues.push(`${graph.id}: expected white paper, received ${bg}`);
        }

        const chartFont = figure?.font?.color;

        if (!chartFont || [
            '#fff',
            '#ffffff',
            'white',
            '#edf5ff',
            '#e9f3ff'
        ].includes(chartFont.toLowerCase())) {
            issues.push(
                `${graph.id}: chart typography not converted to dark`
            );
        }
    }

    const documentWidth = document.documentElement.scrollWidth;
    const viewportWidth = window.innerWidth;

    if (documentWidth > viewportWidth + 24) {
        issues.push(
            `Horizontal overflow: document ${documentWidth}px, viewport ${viewportWidth}px`
        );
    }

    return {
        graphCount: graphs.length,
        issues,
        details,
        documentWidth,
        viewportWidth
    };
}
"""

results = []
failed = []

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)

    for viewport_name, size in VIEWPORTS.items():
        context = browser.new_context(
            viewport={"width": size[0], "height": size[1]},
            device_scale_factor=1
        )
        page = context.new_page()
        page.set_default_timeout(120000)

        for name, route in PAGES.items():
            errors = []

            def collect_error(error):
                errors.append(str(error))

            page.on("pageerror", collect_error)

            try:
                response = page.goto(
                    BASE + route,
                    wait_until="domcontentloaded",
                    timeout=120000
                )

                assert response is not None
                assert response.status == 200

                page.wait_for_function(
                    """() => (
                        document.querySelectorAll('.dash-graph').length === 10
                    )""",
                    timeout=120000
                )

                page.wait_for_function(
                    """() => (
                        [...document.querySelectorAll('.dash-graph')]
                        .every(el => {
                            const plot = el.querySelector('.js-plotly-plot');
                            return plot && plot.data && plot.data.length > 0
                                && plot._fullLayout;
                        })
                    )""",
                    timeout=120000
                )

                for graph in page.locator(".dash-graph").all():
                    graph.scroll_into_view_if_needed(timeout=30000)

                page.evaluate("window.scrollTo(0, 0)")

                result = page.evaluate(CHECK_SCRIPT)
                result["page"] = name
                result["viewport"] = viewport_name
                result["javascriptErrors"] = errors

                filename = f"{viewport_name}_{name}.png"
                page.screenshot(
                    path=str(OUTPUT / filename),
                    full_page=True,
                    animations="disabled",
                    timeout=120000
                )
                result["screenshot"] = filename

                results.append(result)

                if result["graphCount"] != 10:
                    result["issues"].append(
                        f"Expected 10 graphs, found {result['graphCount']}"
                    )

                if errors:
                    result["issues"].append(
                        f"{len(errors)} JavaScript errors"
                    )

                if result["issues"]:
                    failed.append(result)
                    print(
                        f"FAIL {viewport_name}/{name}: "
                        + " | ".join(result["issues"]),
                        flush=True
                    )
                else:
                    print(
                        f"PASS {viewport_name}/{name}: "
                        f"10 rendered charts, no detected overflow",
                        flush=True
                    )

            except Exception as exc:
                error = {
                    "page": name,
                    "viewport": viewport_name,
                    "issues": [str(exc)]
                }
                failed.append(error)
                results.append(error)
                print(
                    f"FAIL {viewport_name}/{name}: {exc}",
                    flush=True
                )
            finally:
                page.remove_listener("pageerror", collect_error)

        context.close()

    browser.close()

summary = {
    "total_page_viewports": len(results),
    "passed": len(results) - len(failed),
    "failed": len(failed),
    "results": results
}

(OUTPUT / "browser_qa_results.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print()
print(
    f"BROWSER QA: {summary['passed']}/"
    f"{summary['total_page_viewports']} PAGE-VIEWPORT CHECKS PASSED"
)
print("SCREENSHOT DIRECTORY:", OUTPUT)

if failed:
    sys.exit(1)

print("ALL 50 CHARTS VERIFIED ACROSS THREE VIEWPORTS")
