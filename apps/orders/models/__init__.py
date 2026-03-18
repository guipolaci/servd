import io
import qrcode
from django.db import models
from django.core.files.base import ContentFile
from apps.accounts.models import Restaurant
from apps.menu.models import Product, ProductExtra


class Table(models.Model):
    """
    Mesa física do restaurante.
    O QR Code é gerado automaticamente quando a mesa é criada.
    Cada QR Code aponta para a URL do cardápio daquela mesa específica.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="tables"
    )
    number = models.PositiveIntegerField()
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Um restaurante não pode ter duas mesas com o mesmo número
        unique_together = ("restaurant", "number")
        ordering = ["number"]

    def save(self, *args, **kwargs):
        # Intercepta o save e gera o QR Code antes de salvar
        if not self.qr_code:
            self._generate_qr_code()
        super().save(*args, **kwargs)

    def _generate_qr_code(self):
        # Monta a URL que o QR Code vai apontar
        url = f"https://servd.app/{self.restaurant.slug}/table/{self.number}/"

        # Gera a imagem do QR Code
        img = qrcode.make(url)

        # Salva a imagem em memória (sem criar arquivo no disco)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        # Salva no campo qr_code do model
        filename = f"qr_{self.restaurant.slug}_table_{self.number}.png"
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False  # não chama save() de novo para evitar loop infinito
        )

    def __str__(self):
        return f"{self.restaurant} — Mesa {self.number}"


class Order(models.Model):
    """
    Pedido feito por um cliente em uma mesa.
    O status avança conforme a cozinha processa o pedido.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PREPARING = "preparing", "Preparando"
        READY = "ready", "Pronto"
        DELIVERED = "delivered", "Entregue"
        CANCELLED = "cancelled", "Cancelado"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.restaurant} Mesa {self.table}"


class OrderItem(models.Model):
    """
    Linha de um pedido. Representa um produto escolhido pelo cliente.

    unit_price é um snapshot do preço no momento do pedido.
    Nunca referenciamos product.price aqui — o dono pode
    alterar o preço do produto e os pedidos antigos devem
    manter o valor que foi cobrado na época.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product}"


class OrderItemExtra(models.Model):
    """
    Adicional selecionado pelo cliente para um item do pedido.
    Também com snapshot de preço pelo mesmo motivo do OrderItem.
    """
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="extras"
    )
    extra = models.ForeignKey(
        ProductExtra,
        on_delete=models.SET_NULL,
        null=True
    )
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.order_item} + {self.extra}"