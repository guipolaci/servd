from django.contrib import admin
from apps.menu.models import Category, Product, ProductExtra

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductExtra)