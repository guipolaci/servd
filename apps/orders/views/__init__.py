import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from apps.menu.selectors import get_menu
from apps.orders.selectors import get_active_orders, get_order_by_id
from apps.orders.services import create_order, update_order_status
from apps.orders.selectors import get_table
from django.http import Http404
from apps.accounts.decorators import kitchen_required, login_required

# ─────────────────────────────────────────
# PÚBLICO — acessado pelo cliente via QR Code
# ─────────────────────────────────────────

def menu_view(request, slug, table_number):
    """
    Antes de mostrar o cardápio, valida que a mesa existe
    e pertence ao restaurante. Se não existir, retorna 404.
    """

    try:
        table = get_table(request.restaurant, table_number)
    except Exception:
        raise Http404("Mesa não encontrada.")

    categories = get_menu(request.restaurant)

    return render(request, "public/menu.html", {
        "categories": categories,
        "table_number": table_number,
        "table": table,
        "restaurant": request.restaurant,
    })

@require_POST
def place_order_view(request, slug, table_number):
    """
    Recebe o pedido do cliente e cria no banco.
    @require_POST garante que só aceita requisições POST —
    ninguém consegue criar pedido só acessando a URL pelo navegador.
    """
    data = json.loads(request.body)

    order = create_order(
        restaurant=request.restaurant,
        table_number=table_number,
        items=data.get("items", []),
        notes=data.get("notes", ""),
    )

    return render(request, "public/order_confirmation.html", {
        "order": order,
        "restaurant": request.restaurant,
    })


def order_tracking_view(request, slug, order_id):
    """
    Página de acompanhamento do pedido.
    O cliente vê o status em tempo real via WebSocket.
    """
    order = get_order_by_id(request.restaurant, order_id)

    return render(request, "public/order_tracking.html", {
        "order": order,
        "restaurant": request.restaurant,
    })


# ─────────────────────────────────────────
# COZINHA — acessado pelo staff
# ─────────────────────────────────────────

@kitchen_required
def kitchen_view(request, slug):
    """
    Painel da cozinha.
    Mostra os pedidos ativos em tempo real via WebSocket.
    """
    orders = get_active_orders(request.restaurant)

    return render(request, "kitchen/panel.html", {
        "orders": orders,
        "restaurant": request.restaurant,
    })


@require_POST
@kitchen_required
def update_order_status_view(request, slug, order_id):
    new_status = request.POST.get("status")

    update_order_status(
        restaurant=request.restaurant,
        order_id=order_id,
        new_status=new_status,
    )

    # A UI é atualizada pelo evento WebSocket disparado em update_order_status.
    # Retornar HTML aqui causaria duplicação (dois caminhos: HTTP e WS).
    return HttpResponse(status=204)

def order_card_view(request, slug, order_id):
    """
    Retorna o card HTML de um pedido específico.
    Usado pelo HTMX no painel da cozinha para atualizar
    um card individualmente via WebSocket.
    """
    order = get_order_by_id(request.restaurant, order_id)
    return render(request, "kitchen/partials/order_card.html", {
        "order": order,
    })