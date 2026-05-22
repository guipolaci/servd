import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Inicializa o Django antes de importar qualquer coisa
# que dependa dos models ou settings
django_asgi_app = get_asgi_application()

# Importado depois do setup do Django — ordem importa aqui
from apps.orders.consumers.routing import websocket_urlpatterns  # noqa
from django.conf import settings  # noqa

if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
    http_handler = ASGIStaticFilesHandler(django_asgi_app)
else:
    http_handler = django_asgi_app

application = ProtocolTypeRouter({
    # Requisições HTTP normais — tratadas pelo Django padrão
    "http": http_handler,

    # Conexões WebSocket — tratadas pelos consumers
    # AuthMiddlewareStack permite acessar request.user nos consumers
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})