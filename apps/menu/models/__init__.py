from django.db import models
from apps.accounts.models import Restaurant


class Category(models.Model):
    """
    Categoria do cardápio. Ex: Lanches, Bebidas, Sobremesas.
    Cada categoria pertence a um restaurante — isolamento do tenant.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.restaurant} — {self.name}"


class Product(models.Model):
    """
    Item do cardápio. Pertence a uma categoria e a um restaurante.
    O campo tag destaca o produto no cardápio do cliente.
    """
    class Tag(models.TextChoices):
        HIT = "hit", "Mais Pedido"
        NEW = "new", "Novidade"
        VEGETARIAN = "veg", "Vegetariano"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    tag = models.CharField(max_length=10, choices=Tag.choices, blank=True)
    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.restaurant} — {self.name}"


class ProductExtra(models.Model):
    """
    Adicional de um produto. Ex: bacon extra +R$3, queijo duplo +R$2.
    O cliente pode selecionar extras na hora de montar o pedido.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="extras"
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} + {self.name}"