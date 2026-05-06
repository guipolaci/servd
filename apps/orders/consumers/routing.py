from django.urls import re_path
from apps.orders.consumers import KitchenConsumer, OrderStatusConsumer

# URLs WebSocket — usam re_path porque WebSocket não usa
# os converters padrão do Django como <slug:slug>
websocket_urlpatterns = [
    # Cozinha conecta aqui para receber pedidos em tempo real
    re_path(
        r"ws/kitchen/(?P<slug>[\w-]+)/$",
        KitchenConsumer.as_asgi()
    ),
    # Cliente conecta aqui para acompanhar o status do pedido
    re_path(
        r"ws/order/(?P<order_id>\d+)/$",
        OrderStatusConsumer.as_asgi()
    ),
]