from django.urls import path
from apps.dashboard.views import (
    panel_home_view,
    menu_list_view,
    product_create_view,
    product_edit_view,
    product_delete_view,
    category_create_view,
)

urlpatterns = [
    path("<slug:slug>/", panel_home_view, name="panel_home"),
    path("<slug:slug>/menu/", menu_list_view, name="panel_menu"),
    path("<slug:slug>/menu/product/create/", product_create_view, name="panel_product_create"),
    path("<slug:slug>/menu/product/<int:product_id>/edit/", product_edit_view, name="panel_product_edit"),
    path("<slug:slug>/menu/product/<int:product_id>/delete/", product_delete_view, name="panel_product_delete"),
    path("<slug:slug>/menu/category/create/", category_create_view, name="panel_category_create"),
]