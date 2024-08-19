from qualitative_coding.helpers import read_settings
from pathlib import Path
import structlog
import logging
import sys

def configure_logger(settings_path):
    """Configures logging and structlog so that future calls to 
    structlog.get_logger() will return a properly-behaved logger.
    The logger logs JSON to a file (specified in settings) and, 
    when settings.verbose is True, also log nicely to the console. 

    Custom log configuration can be stored in a log_config module 
    (e.g. log_config.py).
    """
    try:
        import log_config
        return structlog.get_logger()
    except ModuleNotFoundError:
        pass

    if Path(settings_path).exists():
        settings = read_settings(settings_path)
        verbose = settings.get('verbose', False)
        log_file_path = Path(settings.get('log_path', 'qc.log'))
        if not log_file_path.is_absolute():
            log_file_path = Path(settings_path).parent / log_file_path
    else:
        log_file_path = "qc.log"
        verbose = False

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    file_handler = logging.FileHandler(log_file_path, )
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ]
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    if verbose:
        console_handler = logging.StreamHandler()
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()
