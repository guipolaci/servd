from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404

from apps.accounts.models import Restaurant
from apps.menu.models import Category, Product


def create_product(
    *,
    restaurant: Restaurant,
    name: str,
    description: str,
    price: str,
    category_id: str | None,
    tag: str,
    image,
) -> Product:
    """
    Cria um produto escopado ao tenant.
    Lança ValueError se algum campo obrigatório for inválido.
    """
    if not name:
        raise ValueError("O nome do produto é obrigatório.")
    if not category_id:
        raise ValueError("Selecione uma categoria.")

    try:
        price_decimal = Decimal(price)
        if price_decimal < 0:
            raise ValueError("O preço não pode ser negativo.")
    except InvalidOperation:
        raise ValueError("Preço inválido.")

    category = get_object_or_404(Category, pk=category_id, restaurant=restaurant)

    return Product.objects.create(
        restaurant=restaurant,
        category=category,
        name=name,
        description=description,
        price=price_decimal,
        tag=tag or "",
        image=image,
        is_available=True,
    )


def update_product(
    *,
    restaurant: Restaurant,
    product_id: int,
    name: str,
    description: str,
    price: str,
    category_id: str | None,
    tag: str,
    image,
    is_available: bool,
) -> Product:
    """
    Atualiza um produto. Garante que pertence ao tenant antes de salvar.
    Lança ValueError se algum campo obrigatório for inválido.
    """
    if not name:
        raise ValueError("O nome do produto é obrigatório.")
    if not category_id:
        raise ValueError("Selecione uma categoria.")

    try:
        price_decimal = Decimal(price)
        if price_decimal < 0:
            raise ValueError("O preço não pode ser negativo.")
    except InvalidOperation:
        raise ValueError("Preço inválido.")

    product = get_object_or_404(Product, pk=product_id, restaurant=restaurant)
    category = get_object_or_404(Category, pk=category_id, restaurant=restaurant)

    product.name = name
    product.description = description
    product.price = price_decimal
    product.category = category
    product.tag = tag or ""
    product.is_available = is_available

    if image:
        product.image = image

    product.save()
    return product


def delete_product(*, restaurant: Restaurant, product_id: int) -> None:
    """
    Deleta um produto. Garante que pertence ao tenant antes de remover.
    """
    product = get_object_or_404(Product, pk=product_id, restaurant=restaurant)
    product.delete()


def create_category(*, restaurant: Restaurant, name: str) -> Category:
    """
    Cria uma categoria escopada ao tenant.
    Lança ValueError se o nome vier vazio.
    """
    if not name:
        raise ValueError("O nome da categoria é obrigatório.")

    return Category.objects.create(
        restaurant=restaurant,
        name=name,
        sort_order=0,
        is_active=True,
    )