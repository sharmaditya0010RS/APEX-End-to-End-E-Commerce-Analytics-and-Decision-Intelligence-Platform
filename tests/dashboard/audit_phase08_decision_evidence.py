from pathlib import Path
import json
import pandas as pd

root = Path.cwd()
evidence = root / "docs" / "decision" / "evidence"

scenarios = pd.read_csv(
    evidence / "phase07_decision_scenarios.csv"
)

break_even = pd.read_csv(
    evidence / "phase07_break_even_summary.csv"
)

manifest = json.loads(
    (evidence / "phase07_decision_scenario_manifest.json")
    .read_text(encoding="utf-8-sig")
)

print("\n=== SCENARIO DATASET ===")
print("ROWS:", len(scenarios))
print("COLUMNS:", list(scenarios.columns))
print("DTYPES:")
print(scenarios.dtypes.to_string())

print("\nFIRST THREE SCENARIOS:")
print(scenarios.head(3).to_string(index=False))

print("\nNUMERIC RANGES:")
print(
    scenarios.select_dtypes(include="number")
    .agg(["min", "max", "nunique"])
    .to_string()
)

print("\n=== BREAK-EVEN DATASET ===")
print("ROWS:", len(break_even))
print("COLUMNS:", list(break_even.columns))
print(break_even.to_string(index=False))

print("\n=== SCENARIO MANIFEST ===")
print(json.dumps(manifest, indent=2, ensure_ascii=False))

print("\n=== VALIDATION ===")

assert len(scenarios) == 162
assert len(break_even) == 6
assert not scenarios.empty
assert not scenarios.columns.duplicated().any()
assert not break_even.columns.duplicated().any()

print("162 SCENARIOS: PASS")
print("SIX BREAK-EVEN RECORDS: PASS")
print("DECISION EVIDENCE CONTRACT: PASS")
