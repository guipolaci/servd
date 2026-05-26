from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.orders.models import Table
from apps.orders.services import create_table, delete_table
from apps.accounts.decorators import panel_required
from apps.menu.selectors import get_categories_panel, get_product_panel
from apps.orders.models import Order
from apps.menu.services import (
    create_product,
    update_product,
    delete_product,
    create_category,
)


@panel_required
def panel_home_view(request, slug):
    return render(request, "panel/home.html", {
        "restaurant": request.restaurant,
        "active": "home",
    })


@panel_required
def menu_list_view(request, slug):
    """
    Lista todas as categorias e produtos do restaurante.
    """
    categories = get_categories_panel(request.restaurant).prefetch_related("products")

    return render(request, "panel/menu/list.html", {
        "restaurant": request.restaurant,
        "categories": categories,
        "active": "menu",
    })


@panel_required
def product_create_view(request, slug):
    """
    GET  → exibe formulário de criação
    POST → cria o produto via service e redireciona
    """
    categories = get_categories_panel(request.restaurant)

    if request.method == "POST":
        try:
            create_product(
                restaurant=request.restaurant,
                name=request.POST.get("name", "").strip(),
                description=request.POST.get("description", "").strip(),
                price=request.POST.get("price", "0"),
                category_id=request.POST.get("category"),
                tag=request.POST.get("tag", ""),
                image=request.FILES.get("image"),
            )
            messages.success(request, "Produto criado com sucesso!")
            return redirect("panel_menu", slug=slug)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "panel/menu/form.html", {
        "restaurant": request.restaurant,
        "categories": categories,
        "active": "menu",
        "action": "Criar Produto",
        "product": None,
    })


@panel_required
def product_edit_view(request, slug, product_id):
    """
    GET  → exibe formulário preenchido
    POST → atualiza o produto via service e redireciona
    """
    product = get_product_panel(request.restaurant, product_id)
    categories = get_categories_panel(request.restaurant)

    if request.method == "POST":
        try:
            update_product(
                restaurant=request.restaurant,
                product_id=product_id,
                name=request.POST.get("name", "").strip(),
                description=request.POST.get("description", "").strip(),
                price=request.POST.get("price", "0"),
                category_id=request.POST.get("category"),
                tag=request.POST.get("tag", ""),
                image=request.FILES.get("image"),
                is_available=request.POST.get("is_available") == "on",
            )
            messages.success(request, "Produto atualizado com sucesso!")
            return redirect("panel_menu", slug=slug)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "panel/menu/form.html", {
        "restaurant": request.restaurant,
        "categories": categories,
        "product": product,
        "active": "menu",
        "action": "Editar Produto",
    })


@panel_required
@require_POST
def product_delete_view(request, slug, product_id):
    """
    Deleta um produto. Só aceita POST.
    """
    delete_product(restaurant=request.restaurant, product_id=product_id)
    messages.success(request, "Produto removido.")
    return redirect("panel_menu", slug=slug)


@panel_required
def category_create_view(request, slug):
    """
    GET  → exibe formulário de categoria
    POST → cria a categoria via service e redireciona
    """
    if request.method == "POST":
        try:
            create_category(
                restaurant=request.restaurant,
                name=request.POST.get("name", "").strip(),
            )
            messages.success(request, "Categoria criada com sucesso!")
            return redirect("panel_menu", slug=slug)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "panel/menu/category_form.html", {
        "restaurant": request.restaurant,
        "active": "menu",
    })

@panel_required
def tables_list_view(request, slug):
    """
    Lista todas as mesas do restaurante.
    """
    tables = Table.objects.filter(
        restaurant=request.restaurant
    ).order_by("number")

    return render(request, "panel/tables/list.html", {
        "restaurant": request.restaurant,
        "tables": tables,
        "active": "tables",
    })


@panel_required
def table_create_view(request, slug):
    """
    GET  → exibe formulário
    POST → cria a mesa e gera QR Code
    """
    if request.method == "POST":
        try:
            number = int(request.POST.get("number", 0))
            create_table(request.restaurant, number)
            messages.success(request, f"Mesa {number} criada com sucesso!")
            return redirect("panel_tables", slug=slug)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Erro ao criar mesa. Tente novamente.")

    return render(request, "panel/tables/form.html", {
        "restaurant": request.restaurant,
        "active": "tables",
    })


@panel_required
def table_delete_view(request, slug, table_id):
    """
    Deleta uma mesa.
    """
    if request.method == "POST":
        try:
            delete_table(request.restaurant, table_id)
            messages.success(request, "Mesa removida com sucesso!")
        except Exception:
            messages.error(request, "Erro ao remover mesa.")

    return redirect("panel_tables", slug=slug)

@panel_required
def orders_list_view(request, slug):
    """
    Histórico completo de pedidos do restaurante.
    Filtro por status via query string: ?status=pending
    """
    status_filter = request.GET.get("status", "")

    orders = Order.objects.filter(
        restaurant=request.restaurant
    ).select_related("table").prefetch_related(
        "items__product"
    ).order_by("-created_at")

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, "panel/orders/list.html", {
        "restaurant": request.restaurant,
        "orders": orders,
        "status_filter": status_filter,
        "active": "orders",
    })