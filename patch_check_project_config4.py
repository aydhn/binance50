with open("binance50/scripts/check_project.py", "r") as f:
    content = f.read()

# Make sure Doctor points to config too if needed, though standard config loader defaults to config anyway
# Let's fix the missing `--config-dir` for the signals check that failed earlier
if "[\"python\", \"-m\", \"binance50.cli\", \"signal-quality-check\"" in content:
    content = content.replace("[\"python\", \"-m\", \"binance50.cli\", \"signal-quality-check\"], \"Signal Quality Check\"", "[\"python\", \"-m\", \"binance50.cli\", \"signal-quality-check\", \"--config-dir\", \"config\"], \"Signal Quality Check\"")

with open("binance50/scripts/check_project.py", "w") as f:
    f.write(content)
