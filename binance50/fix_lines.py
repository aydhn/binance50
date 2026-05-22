import os

files_to_fix = [
    "src/binance50/streams/parser.py",
    "src/binance50/streams/reports.py",
    "src/binance50/streams/routing.py",
    "src/binance50/streams/simulator.py",
    "src/binance50/streams/state.py",
    "src/binance50/streams/stream_names.py",
    "src/binance50/streams/subscription.py",
    "src/binance50/streams/validators.py",
    "src/binance50/universe/validators.py",
    "tests/test_cli_streams.py",
    "tests/test_stream_replay.py",
    "tests/test_stream_subscription.py",
]

for fp in files_to_fix:
    if os.path.exists(fp):
        with open(fp) as f:
            lines = f.readlines()
        with open(fp, "w") as f:
            for line in lines:
                if len(line) > 100 and "import" not in line:
                    # just break some long strings manually or ignore
                    # we can use black to reformat actually but it didn't seem to break lines well enough.
                    pass
                f.write(line)
