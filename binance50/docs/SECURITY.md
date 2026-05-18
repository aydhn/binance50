# Security Guidelines

## Core Principles
1. **Never log secrets.** API keys, passwords, tokens, and chat IDs must be masked (`***`) before hitting console or files.
2. **Live trading is disabled by default.** Multi-layer confirmation is required to activate live trading.
3. **API Keys belong in `.env`.** Never commit secrets or default them in YAML files.
4. **Testnet and Paper Trading first.** Never start testing on live markets.
5. **Dry-Run guards are mandatory.** The Live Execution Gateway cannot be bypassed.
6. **No manual intervention required.** Once running, the system makes safe decisions; but initiating live mode is a conscious, manual choice by the user.
