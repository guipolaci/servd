from .base import *  # noqa
# Importa tudo do base e sobrescreve só o que muda em desenvolvimento

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"