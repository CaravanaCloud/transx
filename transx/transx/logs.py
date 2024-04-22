import logging

logging.basicConfig(level=logging.INFO)


def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logging.error(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logging.warning(msg, *args, **kwargs)

