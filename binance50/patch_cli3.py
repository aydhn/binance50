with open("src/binance50/cli.py") as f:
    content = f.read()

import_statement = """
from binance50.streams.event_types import StreamType
from binance50.streams.subscription import build_subscription_plan
from binance50.streams.routing import build_full_stream_url
from binance50.streams.parser import parse_stream_payload
from binance50.streams.event_types import StreamSource
from binance50.streams.buffer import StreamBuffer
from binance50.streams.metrics import StreamMetricsCollector
from binance50.streams.simulator import StreamSimulator
from binance50.streams.replay import StreamReplayEngine
from binance50.streams.state import StreamStateStore
from binance50.safety.stream_guard import build_stream_safety_report, assert_real_stream_connect_allowed
from binance50.streams.reports import build_stream_health_report
from binance50.streams.models import StreamEvent
from binance50.streams.dispatcher import StreamDispatcher
from binance50.market_data.realtime_store import RealtimeMarketDataStore
"""

if "build_subscription_plan" not in content:
    lines = content.split('\n')
    import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import") or line.startswith("from"):
            import_idx = i
    lines.insert(import_idx + 1, import_statement)
    content = "\n".join(lines)

commands = """
@app.command()
def stream_config():
    config = get_config()
    console.print("Stream Config:", config.streams.model_dump())
    try:
        assert_real_stream_connect_allowed(config)
        console.print("[green]Real stream connect allowed.[/green]")
    except Exception as e:
        console.print(f"[yellow]Real stream connect disabled: {e}[/yellow]")

@app.command()
def stream_plan(
    symbols: str = typer.Option(..., help="Comma separated symbols"),
    scope: str = typer.Option(..., help="Market scope (spot, usdm_futures)"),
    types: str = typer.Option(..., help="Comma separated stream types (kline, bookTicker, etc)"),
    interval: str = typer.Option("1m", help="Kline interval")
):
    config = get_config()
    market_scope = MarketScope(scope)
    syms = [s.strip().upper() for s in symbols.split(",")]
    tps = [StreamType(t.strip()) for t in types.split(",")]
    plan = build_subscription_plan(syms, tps, market_scope, config, interval)
    console.print("Subscription Plan:", plan.model_dump())

@app.command()
def stream_url_test(
    symbols: str = typer.Option("BTCUSDT", help="Comma separated symbols"),
    scope: str = typer.Option("spot", help="Market scope"),
    types: str = typer.Option("kline", help="Comma separated stream types"),
    interval: str = typer.Option("1m", help="Kline interval")
):
    config = get_config()
    market_scope = MarketScope(scope)
    syms = [s.strip().upper() for s in symbols.split(",")]
    tps = [StreamType(t.strip()) for t in types.split(",")]
    plan = build_subscription_plan(syms, tps, market_scope, config, interval)
    url = build_full_stream_url(plan, config)
    console.print(f"Full Stream URL: {url}")

@app.command()
def stream_fixture_parse(
    fixture: str = typer.Option(..., help="Fixture filename"),
    scope: str = typer.Option("spot", help="Market scope")
):
    from binance50.streams.fixtures import load_stream_fixture
    raw = load_stream_fixture(fixture)
    market_scope = MarketScope(scope)
    res = parse_stream_payload(raw, market_scope, StreamSource.fixture)
    if res.success and res.event:
        console.print("Parsed Event:", res.event.dump_redacted())
    else:
        console.print("[red]Parse Failed:[/red]", res.error)

@app.command()
def stream_simulate():
    config = get_config()
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT)
    console.print("Simulation Result:", res.model_dump())

@app.command()
def stream_buffer_test():
    config = get_config()
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(["spot_kline_btcusdt_1m_closed.json", "spot_kline_btcusdt_1m_open.json"], MarketScope.SPOT)
    console.print("Buffer Test Simulation Result:", res.model_dump())

@app.command()
def stream_replay_fixtures():
    config = get_config()
    engine = StreamReplayEngine(config)
    res = engine.replay_fixture_sequence(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT, 1.0)
    console.print("Replay Result:", res.model_dump())

@app.command()
def stream_state_report():
    config = get_config()
    sim = StreamSimulator(config)
    store = StreamStateStore()
    events = sim.load_fixture_events(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT)
    for e in events:
        store.update(e)
    console.print("State Report:", store.to_report())

@app.command()
def stream_safety_check():
    config = get_config()
    rep = build_stream_safety_report(config)
    console.print("Stream Safety Report:", rep)

@app.command()
def stream_health():
    config = get_config()
    rep = build_stream_health_report(config)
    console.print("Stream Health:", rep)
"""

if "def stream_config" not in content:
    content += "\n" + commands

    # Update doctor command
    doctor_check = """
        console.print("Running Stream Safety Check...")
        s_rep = build_stream_safety_report(config)
        console.print("Stream Safety:", s_rep)
"""
    content = content.replace('console.print("[green]Doctor check complete.[/green]")', doctor_check + '\n        console.print("[green]Doctor check complete.[/green]")')

    with open("src/binance50/cli.py", "w") as f:
        f.write(content)
