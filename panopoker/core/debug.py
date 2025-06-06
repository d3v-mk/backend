import os
from datetime import datetime

debug_log = open(os.path.join(os.path.dirname(__file__), "..", "debug.log"), "a", encoding="utf-8")

def debug_print(*args, silent=False, level="INFO", **kwargs):
    if silent:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}] [{level}]"

    # Texto sem ANSI → vai pro arquivo
    raw_line = prefix + " " + " ".join(str(arg) for arg in args)
    print(raw_line, file=debug_log, flush=True)

    # Texto com ANSI (se houver) → vai pro terminal
    if kwargs.get("ansi"):
        print(*args)

def debug_silencioso(*args, **kwargs):
    pass  # Não faz nada, só silencia