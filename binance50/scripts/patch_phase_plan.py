from pathlib import Path

file_path = Path("docs/PHASE_PLAN.md")
if file_path.exists():
    content = file_path.read_text()

    # We'll just append Phase 11 & 12 info if not present
    if "Phase 11" not in content:
        content += "\n- Phase 11: Indicator engine v1; trend, momentum, volatilite, hacim ve temel transform indikatörleri native pandas/numpy backend ile kurulur."
    if "Phase 12" not in content:
        content += "\n- Phase 12: Indicator engine v2 genişletilecek: divergence, multi-timeframe alignment, pattern/candlestick hazırlıkları ve feature grouping modeli kurulacak."

    file_path.write_text(content)
else:
    # Create the file if it doesn't exist
    content = """# Phase Plan
- Phase 11: Indicator engine v1; trend, momentum, volatilite, hacim ve temel transform indikatörleri native pandas/numpy backend ile kurulur.
- Phase 12: Indicator engine v2 genişletilecek: divergence, multi-timeframe alignment, pattern/candlestick hazırlıkları ve feature grouping modeli kurulacak.
"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

print("Patched PHASE_PLAN.md")
