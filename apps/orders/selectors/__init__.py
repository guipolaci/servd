from apps.orders.models import Order, Table
from apps.accounts.models import Restaurant


def get_active_orders(restaurant: Restaurant):
    """
    Retorna os pedidos ativos para o painel da cozinha.
    Ativos = tudo exceto entregue e cancelado.
    Ordenado por criação — mais antigo primeiro,
    para a cozinha priorizar quem esperou mais.
    """
    return (
        Order.objects
        .filter(restaurant=restaurant)
        .exclude(status__in=[
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
        ])
        .select_related("table")
        .prefetch_related(
            "items__product",
            "items__extras__extra",
        )
        .order_by("created_at")
    )


def get_order_by_id(restaurant: Restaurant, order_id: int) -> Order:
    """
    Retorna um pedido pelo ID, escopado ao tenant.
    """
    return Order.objects.get(
        pk=order_id,
        restaurant=restaurant
    )


def get_table(restaurant: Restaurant, table_number: int) -> Table:
    """
    Retorna uma mesa pelo número, escopada ao tenant.
    """
    return Table.objects.get(
        restaurant=restaurant,
        number=table_number,
        is_active=True
    )