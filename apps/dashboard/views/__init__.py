from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from apps.accounts.decorators import panel_required
from apps.menu.selectors import get_categories_panel, get_product_panel
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