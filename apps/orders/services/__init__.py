from django.db import transaction
from apps.accounts.models import Restaurant
from apps.orders.models import Order, OrderItem, OrderItemExtra
from apps.menu.models import Product, ProductExtra


@transaction.atomic
def create_order(
    restaurant: Restaurant,
    table_number: int,
    items: list,
    notes: str = "",
) -> Order:
    """
    Cria um pedido completo para uma mesa.

    O @transaction.atomic garante que ou tudo é salvo
    ou nada é salvo. Se der erro no meio do processo,
    o banco volta ao estado anterior automaticamente.

    items esperado:
    [
        {
            "product_id": 1,
            "quantity": 2,
            "notes": "sem cebola",
            "extras": [1, 3]
        }
    ]
    """
    from apps.orders.selectors import get_table

    # Busca a mesa — já valida que pertence ao tenant
    table = get_table(restaurant, table_number)

    # Cria o pedido com total zero por enquanto
    # o total será calculado conforme os itens forem criados
    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        notes=notes,
        status=Order.Status.PENDING,
        total=0,
    )

    total = 0

    for item_data in items:
        # Busca o produto garantindo que pertence ao tenant
        product = Product.objects.get(
            pk=item_data["product_id"],
            restaurant=restaurant,
            is_available=True,
        )

        quantity = item_data.get("quantity", 1)

        # Cria o item com snapshot do preço atual
        # se o preço mudar amanhã, esse pedido mantém o valor de hoje
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            notes=item_data.get("notes", ""),
        )

        item_total = product.price * quantity

        # Processa os adicionais se houver
        for extra_id in item_data.get("extras", []):
            extra = ProductExtra.objects.get(
                pk=extra_id,
                product=product,
                is_available=True,
            )
            OrderItemExtra.objects.create(
                order_item=order_item,
                extra=extra,
                unit_price=extra.price,
            )
            item_total += extra.price * quantity

        total += item_total

    # Atualiza o total do pedido com o valor calculado
    order.total = total
    order.save(update_fields=["total"])

    return order


def update_order_status(
    restaurant: Restaurant,
    order_id: int,
    new_status: str
) -> Order:
    """
    Avança o status de um pedido.
    Chamado pela cozinha quando processa o pedido.
    """
    from apps.orders.selectors import get_order_by_id

    order = get_order_by_id(restaurant, order_id)
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])

    return order