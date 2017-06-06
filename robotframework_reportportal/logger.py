from robot.api import logger
from .model import LogMessage


def write(msg, level="INFO", html=False, attachment=None):
    log_message = LogMessage(msg)
    log_message.level = level
    log_message.attachment = attachment
    logger.write(log_message, level, html)


def trace(msg, html=False, attachment=None):
    write(msg, "TRACE", html, attachment)


def debug(msg, html=False, attachment=None):
    write(msg, "DEBUG", html, attachment)


def info(msg, html=False, also_console=False, attachment=None):
    write(msg, "INFO", html, attachment)
    if also_console:
        console(msg)


def warn(msg, html=False, attachment=None):
    write(msg, "WARN", html, attachment)


def error(msg, html=False, attachment=None):
    write(msg, "ERROR", html, attachment)


def console(msg, newline=True, stream="stdout"):
    logger.console(msg, newline, stream)
