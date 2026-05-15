import os


def _env_bool(name, default="False"):
    value = os.getenv(name, default)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class MailConfig:
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = _env_int("MAIL_PORT")
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
