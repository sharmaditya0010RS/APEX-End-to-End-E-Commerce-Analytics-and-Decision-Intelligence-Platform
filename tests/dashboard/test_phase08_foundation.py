from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
dashboard = root / "src" / "dashboard"
sys.path.insert(0, str(dashboard))

from app import app
from data_access import executive_kpis
import dash

expected_routes = {
    "/",
    "/customers",
    "/operations",
    "/predictive",
    "/decisions"
}

actual_routes = {page["path"] for page in dash.page_registry.values()}

assert actual_routes == expected_routes, actual_routes
print("FIVE REGISTERED PAGES: PASS")

css = dashboard / "assets" / "apex.css"
assert css.exists() and css.stat().st_size > 5000
print("PREMIUM CSS ASSET: PASS")

client = app.server.test_client()

for route in expected_routes:
    response = client.get(route)
    assert response.status_code == 200, (route, response.status_code)

print("FIVE ROUTE HTTP RESPONSES: PASS")

kpis = executive_kpis()

assert kpis["total_orders"] == 99441, kpis
assert kpis["eligible_orders"] == 96470, kpis
assert kpis["late_orders"] == 6534, kpis
assert abs(kpis["late_rate"] - 6534 / 96470) < 1e-12

print("WAREHOUSE KPI RECONCILIATION: PASS")
print("LIVE KPIS:", kpis)
print("PHASE 8 APPLICATION FOUNDATION: PASS")
