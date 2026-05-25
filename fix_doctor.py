import sys

filename = 'binance50/src/binance50/cli.py'
with open(filename, 'r') as f:
    content = f.read()

# Remove the duplicate doctor definition and rename the second one to just include the walkforward bits in the first
doctor_idx = content.find("def doctor() -> None:")
second_doctor_idx = content.find("def doctor():", doctor_idx + 10)

if second_doctor_idx != -1:
    content = content[:second_doctor_idx] + "def optimizer_doctor():\n" + content[second_doctor_idx+14:]

with open(filename, 'w') as f:
    f.write(content)
