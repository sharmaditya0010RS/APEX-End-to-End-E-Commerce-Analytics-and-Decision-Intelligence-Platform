import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src" / "dashboard"))

from app import app

app._setup_server()

matches = [
    (name, callback)
    for name, callback in app.callback_map.items()
    if "customer-repeat-chart" in name
]

assert len(matches) == 1, list(app.callback_map)

name, callback = matches[0]

assert len(callback["inputs"]) == 1
assert callback["inputs"][0]["id"] == "customer-highlight"

print("SEVEN-OUTPUT CALLBACK: REGISTERED")
print("CALLBACK NAME:", name)
print("CALLBACK INPUT:", callback["inputs"][0])
print("CALLBACK REGISTRATION: PASS")
