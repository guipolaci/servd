from django.contrib import admin
from apps.accounts.models import Plan, Restaurant, Subscription, User

admin.site.register(Plan)
admin.site.register(Restaurant)
admin.site.register(Subscription)
admin.site.register(User)