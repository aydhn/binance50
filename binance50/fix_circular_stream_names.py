with open("src/binance50/streams/subscription.py") as f:
    content = f.read()

content = content.replace(
    "from binance50.streams.stream_names import build_combined_stream_path, build_stream_name",
    "from binance50.streams.stream_names import build_stream_name\nfrom binance50.connectors.stream_names import build_combined_stream_path",
)

with open("src/binance50/streams/subscription.py", "w") as f:
    f.write(content)
