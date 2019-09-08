# Logs
# -----
# (c) 2019 Chris Proctor

# Configures and returns a logger

from pathlib import Path
import logging
import sys

def get_logger(name, logs_dir, debug_console=False):
    "Configures a logger with two file handlers, one at DEBUG and one at INFO"
    log = logging.getLogger(name)
    debug_file_handler = logging.FileHandler(Path(logs_dir) / "qc.debug.log")
    debug_file_handler.setLevel(logging.DEBUG)
    info_file_handler = logging.FileHandler(Path(logs_dir) / "qc.info.log")
    info_file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug_console else logging.INFO)

    formatter = logging.Formatter("%(level)s\t%(asctime)s\t%(message)s")
    for h in [debug_file_handler, info_file_handler, console_handler]:
        h.setFormatter(formatter)
        log.addHandler(h)
    return log
