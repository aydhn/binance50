with open("src/binance50/core/exceptions.py") as f:
    content = f.read()

content = content.replace("from binance50.logging.redaction import redact_dict", "from binance50.logging.redaction import redact_mapping")
content = content.replace("d[\"metadata\"] = redact_dict(d[\"metadata\"])", "d[\"metadata\"] = redact_mapping(d[\"metadata\"])")

with open("src/binance50/core/exceptions.py", "w") as f:
    f.write(content)
