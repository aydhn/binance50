import re

with open("binance50/src/binance50/app.py", "r") as f:
    app = f.read()

app = app.replace(
    '# This logic is handled inside environment_guard build_environment_safety_report / validate_environment_matrix',
    '# This logic is handled inside environment_guard build_environment_safety_report \\\n        # / validate_environment_matrix'
)
with open("binance50/src/binance50/app.py", "w") as f:
    f.write(app)


with open("binance50/src/binance50/config/loader.py", "r") as f:
    loader = f.read()

loader = loader.replace(
    '# but wait, it is NOT in the model according to the specs... wait, we only check OS env in live_guard!',
    '# but wait, it is NOT in the model according to the specs... wait,\n            # we only check OS env in live_guard!'
)
loader = loader.replace(
    '# safety.require_manual_live_unlock: true ise env BINANCE50_LIVE_UNLOCK tam olarak required phrase olmalı.',
    '# safety.require_manual_live_unlock: true ise env BINANCE50_LIVE_UNLOCK \\\n            # tam olarak required phrase olmalı.'
)

with open("binance50/src/binance50/config/loader.py", "w") as f:
    f.write(loader)


with open("binance50/src/binance50/core/exception_handler.py", "r") as f:
    eh = f.read()
eh = eh.replace(
    'log_msg = f"[{component}] {action} failed: {safe_dict[\'message\']} (Code: {safe_dict[\'error_code\']})"',
    'log_msg = (f"[{component}] {action} failed: {safe_dict[\'message\']} "\n                   f"(Code: {safe_dict[\'error_code\']})")'
)
with open("binance50/src/binance50/core/exception_handler.py", "w") as f:
    f.write(eh)


with open("binance50/src/binance50/logging/redaction.py", "r") as f:
    lr = f.read()
lr = lr.replace(
    '# E.g., very long alphanumeric strings that might be tokens or keys (Binance keys are typically 64 chars)',
    '# E.g., very long alphanumeric strings that might be tokens or keys\n# (Binance keys are typically 64 chars)'
)
with open("binance50/src/binance50/logging/redaction.py", "w") as f:
    f.write(lr)


with open("binance50/src/binance50/safety/api_key_guard.py", "r") as f:
    akg = f.read()
akg = akg.replace(
    '# According to requirements: "live profilde IP restriction false ise bu fazda hard error yerine blocking warning üret"',
    '# According to requirements: "live profilde IP restriction false ise "\n        # "bu fazda hard error yerine blocking warning üret"'
)
akg = akg.replace(
    '# However, we only have Exceptions here. We\'ll raise a custom check but we might bypass it in live guard.',
    '# However, we only have Exceptions here. We\'ll raise a custom check\n        # but we might bypass it in live guard.'
)
with open("binance50/src/binance50/safety/api_key_guard.py", "w") as f:
    f.write(akg)


with open("binance50/src/binance50/safety/connector_guard.py", "r") as f:
    cg = f.read()
cg = cg.replace(
    '"Phase 5 explicitly blocks real network calls. allow_real_network_in_phase5 must be false."',
    '"Phase 5 explicitly blocks real network calls. "\n            "allow_real_network_in_phase5 must be false."'
)
with open("binance50/src/binance50/safety/connector_guard.py", "w") as f:
    f.write(cg)


with open("binance50/src/binance50/safety/mode_guard.py", "r") as f:
    mg = f.read()
mg = mg.replace(
    'f"Profile {profile.profile_name.value} is readonly but trade permissions are configured"',
    'f"Profile {profile.profile_name.value} is readonly "\n                "but trade permissions are configured"'
)
with open("binance50/src/binance50/safety/mode_guard.py", "w") as f:
    f.write(mg)

print("Fixed lingering ruff errors")
