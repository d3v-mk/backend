import os
from datetime import datetime

# Caminho absoluto pro arquivo de log
debug_log = open(os.path.join(os.path.dirname(__file__), "..", "debug.log"), "a", encoding="utf-8")

def debug_print(*args, silent=False, level="INFO", **kwargs):
    if silent:
        return  # Não faz nada se silent=True
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}] [{level}]"
    print(prefix, *args, **kwargs, file=debug_log, flush=True)



def debug_silencioso(*args, **kwargs):
    pass  # Não faz nada, só silencia
