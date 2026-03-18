from django.urls import path
from apps.orders.views import (
    menu_view,
    place_order_view,
    order_tracking_view,
    kitchen_view,
    update_order_status_view,
)

urlpatterns = [
    # ── Público ──────────────────────────────────────
    # Cliente acessa o cardápio via QR Code
    path(
        "<slug:slug>/table/<int:table_number>/",
        menu_view,
        name="menu"
    ),
    # Cliente confirma o pedido
    path(
        "<slug:slug>/table/<int:table_number>/order/",
        place_order_view,
        name="place_order"
    ),
    # Cliente acompanha o status do pedido
    path(
        "<slug:slug>/order/<int:order_id>/",
        order_tracking_view,
        name="order_tracking"
    ),

    # ── Cozinha ──────────────────────────────────────
    # Painel principal da cozinha
    path(
        "kitchen/<slug:slug>/",
        kitchen_view,
        name="kitchen"
    ),
    # Cozinha atualiza o status do pedido
    path(
        "kitchen/<slug:slug>/order/<int:order_id>/status/",
        update_order_status_view,
        name="update_order_status"
    ),
]