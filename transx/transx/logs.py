import logging
from rich.logging import RichHandler


logger = None
if not logger:
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]  # Use RichHandler
    )
    logger = logging.getLogger("rich_logger")


def info(msg, *args, **kwargs): 
    logger.info(msg, *args, stacklevel=2, **kwargs)


def error(msg, *args, **kwargs):
    logger.error(msg, *args, stacklevel=2, **kwargs)


def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, stacklevel=2, **kwargs)


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, stacklevel=2, **kwargs)

def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, stacklevel=2, **kwargs)
