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





def dbg(tag: str, msg: str):
    from panopoker.core.debug import debug_print

    COLORS = {
        "INFO": "\033[94m",
        "SAIR": "\033[95m",
        "ENTRAR": "\033[96m",
        "FOLD": "\033[91m",
        "CHECK": "\033[92m",
        "CALL": "\033[93m",
        "RAISE": "\033[35m",
        "TIMER": "\033[90m",
        "SHOWDOWN": "\033[36m",
        "ERRO": "\033[91m",
        "DEBUG": "\033[37m",
    }

    RESET = "\033[0m"
    tag_upper = tag.upper()
    color = COLORS.get(tag_upper, "\033[97m")

    log_line = f"[{tag_upper}] {msg}"              # limpo pro arquivo
    colored_line = f"{color}[{tag_upper}]{RESET} {msg}"  # com cor no terminal

    debug_print(log_line)             # vai pro arquivo
    debug_print(colored_line, ansi=True)  # vai pro terminal com cor
