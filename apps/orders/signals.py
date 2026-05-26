from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.models import Order


@receiver(post_save, sender=Order)
def order_saved(sender, instance: Order, created: bool, update_fields, **kwargs):
    """
    Notifica cozinha e cliente em qualquer escrita no Order,
    independente de vir do service, admin ou shell.
    """
    status_relevant = (
        created
        or update_fields is None
        or "status" in (update_fields or [])
    )

    if not status_relevant:
        return

    _notify_kitchen(instance)

    if not created:
        _notify_customer(instance)


def _notify_kitchen(order: Order) -> None:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"kitchen_{order.restaurant.slug}",
        {
            "type": "orders.update",
            "order_id": order.pk,
            "status": order.status,
        },
    )


def _notify_customer(order: Order) -> None:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"order_{order.pk}",
        {
            "type": "orders.status",
            "status": order.status,
        },
    )
