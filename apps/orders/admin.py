from django.contrib import admin
from apps.orders.models import Table, Order, OrderItem

admin.site.register(Table)
admin.site.register(Order)
admin.site.register(OrderItem)