from django.shortcuts import get_object_or_404

from apps.menu.models import Category, Product
from apps.accounts.models import Restaurant


def get_menu(restaurant: Restaurant):
    """
    Retorna todas as categorias ativas com seus produtos disponíveis.
    Essa é a query principal da página de cardápio do cliente.

    select_related e prefetch_related evitam o problema N+1:
    sem eles, o Django faria uma query para cada categoria
    e uma para cada produto — podendo gerar dezenas de queries
    numa única requisição.
    """
    return (
        Category.objects
        .filter(restaurant=restaurant, is_active=True)
        .prefetch_related("products")
        .order_by("sort_order")
    )


def get_product_by_id(restaurant: Restaurant, product_id: int) -> Product:
    """
    Retorna um produto pelo ID, sempre escopado ao tenant.
    Garante que um restaurante nunca acesse produto de outro.
    """
    return Product.objects.get(
        pk=product_id,
        restaurant=restaurant,
        is_available=True
    )


def get_categories_panel(restaurant: Restaurant):
    """
    Retorna todas as categorias do restaurante para o painel administrativo.
    Diferente do get_menu, inclui categorias inativas — o gestor precisa vê-las.
    """
    return Category.objects.filter(restaurant=restaurant).order_by("sort_order", "name")


def get_product_panel(restaurant: Restaurant, product_id: int) -> Product:
    """
    Retorna um produto para o painel administrativo, escopado ao tenant.
    Não filtra por is_available — gestor pode editar produtos indisponíveis.
    """
    return get_object_or_404(Product, pk=product_id, restaurant=restaurant)